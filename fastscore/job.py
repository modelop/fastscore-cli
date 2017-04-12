
import sys
import json
import base64

import service
from service import engine_api_name

from tabulate import tabulate
from stats import human_fmt

import model, stream
import pneumo

MAX_INLINE_ATTACHMENT = 1024*1024

def run(args):
  model_name = args["model-name"]

  in_name = args["in-stream-name"]
  in_desc = stream.get_desc(in_name)

  if "out-stream-name" in args:
    out_name = args["out-stream-name"]
    out_desc = stream.get_desc(out_name)
  else:
    out_name = "discard"
    out_desc = stream.shortcuts["discard"]

  code,body,ctype = service.get_with_ct("model-manage", "/1/model/%s" % model_name)
  if code == 200:
    att = attachments(model_name)
    run1(in_name, in_desc, out_name, out_desc, ctype, model_name, body, attachments=att)
  elif code == 404:
    print "Model '%s' not found" % model_name
  else:
    raise Exception(body.decode('utf-8'))

def attachments(model_name, force_inline=False):
  code,body = service.get("model-manage", "/1/model/%s/attachment" % model_name)
  if code == 200:
    return [ get_att(model_name, att_name, force_inline) for att_name in json.loads(body.decode('utf-8')) ]
  else:
    raise Exception(body.decode('utf-8'))

def get_att(model_name, att_name, force_inline):
  _,headers = service.head("model-manage",
                  "/1/model/%s/attachment/%s" % (model_name,att_name))
  ctype = headers["content-type"]
  size = int(headers["content-length"])
  if size > MAX_INLINE_ATTACHMENT and not force_inline:

    ## See https://opendatagoup.atlassian.net/wiki/display/FAS/Working+with+large+attachments
    ##
    ## An example of an externalized attachment:
    ##
    ## Content-Type: message/external-body; access-type=x-model-manage; name="att1.zip"
    ##
    ## Content-Type: application/zip
    ## Content-Disposition: attachment; filename="att1.zip"
    ## Content-Length: 1234
    ##

    ext_type = "message/external-body; " + \
               "access-type=x-model-manage; " + \
               "ref=\"urn:fastscore:attachment:%s:%s\"" % (model_name,att_name)

    body = "Content-Type: %s\r\n" % ctype + \
           "Content-Disposition: attachment; filename=\"%s\"\r\n" % att_name + \
           "Content-Length: %d\r\n" % size + \
           "\r\n"

    return (att_name,body,ext_type)

  else:
    code,body = service.get("model-manage",
                    "/1/model/%s/attachment/%s" % (model_name,att_name))
    if code == 200:
      return (att_name,body,ctype)
    else:
      raise Exception(body.decode('utf-8'))

def run1(in_name, in_desc, out_name, out_desc, ctype, model_name, body, attachments=[]):
  headers1 = {"content-type": "application/json",
              "content-disposition": "x-stream; name=\"" + out_name + "\""}
  code3,body3 = service.put_with_headers(engine_api_name(), "/1/job/stream/out", headers1, out_desc)
  if code3 != 204:
    raise Exception(body3.decode('utf-8'))
  print "Output stream set"
  headers2 = {"content-type": "application/json",
              "content-disposition": "x-stream; name=\"" + in_name + "\""}
  code2,body2 = service.put_with_headers(engine_api_name(), "/1/job/stream/in", headers2, in_desc)
  if code2 != 204:
    raise Exception(body2.decode('utf-8'))
  print "Input stream set"

  ws = None
  try:
    if service.options["wait"]:
      ws = pneumo.connect()

    if attachments == []:
      headers3 = {"content-type": ctype,
                  "content-disposition": "x-model; name=\"" + model_name + "\""}
      code1,body1 = service.put_with_headers(engine_api_name(), "/1/job/model", headers3, body)
    else:
      parts = [ ("attachment",x) for x in attachments ]
      parts.append( ("x-model",(model_name,body,ctype)) )
      code1,body1 = service.put_multi(engine_api_name(), "/1/job/model", parts)
    if code1 != 204:
      raise Exception(body1.decode('utf-8'))
    print "Model sent to engine"
    print "The engine is running"

    if ws != None:
      print "Waiting for the model run to complete...",
      while True:
        x = json.loads(ws.recv())
        if x["type"] == "output-eof":
          print "done"
          break

  finally:
    if ws != None:
      ws.close()

def scale(args):
  n = int(args["num-jets"])
  code,body = service.post(engine_api_name(), "/1/job/scale?n=%d" % n)
  if code == 204:
    print "Model scaling successful"
  else:
    raise Exception(body.decode('utf-8'))

def cpu_utilization(args):
  path = "/1/job/sample/cpu"
  if "duration" in args:
    path += "?duration=" + args["duration"]
  code,body = service.post(engine_api_name(), path)
  if code == 200:
    x = json.loads(body.decode('utf-8'))
    if "error" in x:
      print "Cannot collect CPU utilization info: " + x["error"]
    else:
      report = x["cpu-utilization"]
      report_cpu_util(report)
  else:
    raise Exception(body.decode('utf-8'))

def report_cpu_util(report):
  t = [["Duration, s",report["duration"]],
       ["Input",rb(report["input_bytes"], report["input_records"])],
       ["Output",rb(report["output_bytes"], report["output_records"])],
       ["CPU time (streams), s",ct(report["user_time"], report["kernel_time"])]]
  print tabulate(t)
  op_times = report["op_times"]
  op_names = ["unwrap_envelope",
              "wrap_envelope",
              "decode_input_record",
              "decode_output_record",
              "type_check_input",
              "type_check_output"]
  t = [ [name,tc(op_times[name], op_times[name + "_n"])] for name in op_names ]
  print tabulate(t, headers=["Operation","Time, s (user+kernel)"])
  print
  jets = report["jets"]
  for i in range(len(jets)):
    jets[i]["id"] = i+1
  t = [ [x["id"],
         x["input_records"],
         x["output_records"],
         ct(x["user_time"], x["kernel_time"]),
         x["model_time"]] for x in jets ]
  print tabulate(t, headers=["Instance",
                             "Input",
                             "Output",
                             "CPU time, s",
                             "Model time, s"])

def ct(ut, kt):
  return "%.3f (%.3f user + %.3f kernel)" % (ut + kt,ut,kt)

def rb(bytes, records):
  (v,u) = human_fmt(bytes)
  return "%d record(s) (%.1f%s)" % (records,v,u)

def tc(tm, cnt):
  return "%.3f (%d)" % (tm,cnt)

def input(args):
  data = sys.stdin.read()
  if data == "":
    return

  ## Add a 'pig' control record to the stream.
  ## This implies the JSON encoding and 'delimited' framing scheme.
  pig = '{"$fastscore":"pig"}'
  data += pig + "\n"

  code,body = service.post(engine_api_name(), "/1/job/input", data=data)
  if code != 204:
    raise Exception(body.decode('utf-8'))

  if sys.stdin.isatty() and sys.stdout.isatty():
    print "-------- model output --------"
  ## Output stream may contain multiple chunks.
  chip = ""
  pig_received = False
  while not pig_received:
    code,body = service.get(engine_api_name(), "/1/job/output")
    if code != 200:
      raise Exception(body.decode('utf-8'))
    chunk = chip + body
    while True:
      x = chunk.split("\n", 1)
      if len(x) > 1:
        rec = x[0]
        chunk = x[1]
        if rec == pig:
          pig_received = True
          break
        elif rec != "": # an artifact of delimited framing
          print rec.decode('utf-8')
      else:
        chip = x[0]
        if chip == pig:
          pig_received = True
        break

def stop(args):
  code,body = service.delete(engine_api_name(), "/1/job")
  if code == 204:
    print "Engine stopped"
  else:
    raise Exception(body.decode('utf-8'))

def att_ctype_to_type(ctype):
  if ctype == "application/zip":
    return "zip"
  elif ctype == "application/gzip":
    return "tgz"
  else:
    raise Exception("%s not recognized" % ctype)

