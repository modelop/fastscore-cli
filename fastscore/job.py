
import sys
import json
import base64

import service
from service import engine_api_name

from tabulate import tabulate
from stats import human_fmt

MAX_INLINE_ATTACHMENT = 1024*1024

stream_shortcuts = {
  "discard": '{"Transport":{"Type":"discard"}}',
  "console": '{"Transport":{"Type":"console"}}'
}

def run(args):
  model_name = args["model-name"]

  in_name = args["in-stream-name"]
  in_desc = get_stream_desc(in_name)

  if "out-stream-name" in args:
    out_name = args["out-stream-name"]
    out_desc = get_stream_desc(out_name)
  else:
    out_name = "discard"
    out_desc = stream_shortcuts["discard"]

  code,body,ctype = service.get_with_ct("model-manage", "/1/model/%s" % model_name)
  if code == 200:
    att = attachments(model_name)
    run1(in_name, in_desc, out_name, out_desc, ctype, model_name, body, attachments=att)
  elif code == 404:
    print "Model '%s' not found" % model_name
  else:
    raise Exception(body)

def attachments(model_name):
  code,body = service.get("model-manage", "/1/model/%s/attachment" % model_name)
  if code == 200:
    return [ get_att(model_name, att_name) for att_name in json.loads(body) ]
  else:
    raise Exception(body)

def get_att(model_name, att_name):
  _,headers = service.head("model-manage",
                  "/1/model/%s/attachment/%s" % (model_name,att_name))
  ctype = headers["content-type"]
  size = int(headers["content-length"])
  if size > MAX_INLINE_ATTACHMENT:

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
      raise Exception(body)

def run1(in_name, in_desc, out_name, out_desc, ctype, model_name, body, attachments=[]):
  headers1 = {"content-type": "application/json",
              "content-disposition": "x-stream; name=\"" + out_name + "\""}
  code3,body3 = service.put_with_headers(engine_api_name(), "/1/job/stream/out", headers1, out_desc)
  if code3 != 204:
    raise Exception(body3)
  print "Output stream set"
  headers2 = {"content-type": "application/json",
              "content-disposition": "x-stream; name=\"" + in_name + "\""}
  code2,body2 = service.put_with_headers(engine_api_name(), "/1/job/stream/in", headers2, in_desc)
  if code2 != 204:
    raise Exception(body2)
  print "Input stream set"
  if attachments == []:
    headers3 = {"content-type": ctype,
                "content-disposition": "x-model; name=\"" + model_name + "\""}
    code1,body1 = service.put_with_headers(engine_api_name(), "/1/job/model", headers3, body)
  else:
    parts = [ ("attachment",x) for x in attachments ]
    parts.append( ("x-model",(model_name,body,ctype)) )
    code1,body1 = service.put_multi(engine_api_name(), "/1/job/model", parts)
  if code1 != 204:
    raise Exception(body1)
  print "Model sent to engine"
  print "The engine is running"

def debug(args):
  model_name = args["model-name"]
  in_desc = get_stream_desc(args["in-stream-name"])
  out_desc = get_stream_desc(args["out-stream-name"]) \
                  if "out-stream-name" in args else stream_shortcuts["discard"]
  code,body,ctype = service.get_with_ct("model-manage", "/1/model/%s" % model_name)
  att = attachments(model_name)
  if code == 200:
    spec = {
      "input": in_desc,
      "output": out_desc,
      "type": ctype_to_type(ctype),
      "model": body,
      "attachments": [{
        "name": att_name,
        "data": base64.b64encode(att_body),
        "type": att_ctype_to_type(att_ctype)
      } for (att_name,att_body,att_ctype) in att ]
    }
    debug1(json.dumps(spec))
  elif code == 404:
    print "Model '%s' not found" % model_name
  else:
    raise Exception(body)

def debug1(data):
  code,report = service.post(engine_api_name(), "/1/job/debug", ctype="application/json", data=data)
  if code == 200:
    print report
  else:
    raise Exception(report)

def get_stream_desc(name):
  if name in stream_shortcuts:
    return stream_shortcuts[name]
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    return body
  elif code == 404:
    raise Exception("Stream '%s' not found" % name)
  else:
    raise Exception(body)

def scale(args):
  n = int(args["num-jets"])
  code,body = service.post(engine_api_name(), "/1/job/scale?n=%d" % n)
  if code == 204:
    print "Model scaling successful"
  else:
    raise Exception(body)

def cpu_utilization(args):
  path = "/1/job/sample/cpu"
  if "duration" in args:
    path += "?duration=" + args["duration"]
  code,body = service.post(engine_api_name(), path)
  if code == 200:
    x = json.loads(body)
    if "error" in x:
      print "Cannot collect CPU utilization info: " + x["error"]
    else:
      report = x["cpu-utilization"]
      report_cpu_util(report)
  else:
    raise Exception(body)

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
         ct(x["user_time"], x["kernel_time"])] for x in jets ]
  print tabulate(t, headers=["Instance","Input","Output","CPU time, s"])

def ct(ut, kt):
  return "%.3f (%.3f user + %.3f kernel)" % (ut + kt,ut,kt)

def rb(bytes, records):
  (v,u) = human_fmt(bytes)
  return "%d record(s) (%.1f%s)" % (records,v,u)

def tc(tm, cnt):
  return "%.3f (%d)" % (tm,cnt)

def stop(args):
  code,body = service.delete(engine_api_name(), "/1/job")
  if code == 204:
    print "Engine stopped"
  else:
    raise Exception(body)

def ctype_to_type(ctype):
  if ctype == "application/vnd.pfa+json":
    return "PFA/json"
  elif ctype == "application/vnd.ppfa":
    return "PrettyPFA"
  elif ctype == "application/x-yaml":
    return "PFA/yaml"
  elif ctype == "application/x-python":
    return "python"
  elif ctype == "application/x-r":
    return "R"
  else:
    raise Exception("%s not recognized" % ctype)

def att_ctype_to_type(ctype):
  if ctype == "application/zip":
    return "zip"
  elif ctype == "application/gzip":
    return "tgz"
  else:
    raise Exception("%s not recognized" % ctype)

