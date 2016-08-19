
import json
from tabulate import tabulate

import fastscore

def run(args):
  model_name = args["model-name"]
  in_desc = get_stream_desc(args["in-stream-name"])
  out_desc = get_stream_desc(args["out-stream-name"]) if "out-stream-name" in args else discard_desc()
  code,body,ctype = fastscore.get_with_ct("model-manage", "/1/model/%s" % model_name)
  if code == 200:
    run1(in_desc, out_desc, ctype, body)
  elif code == 404:
    print "Model '%s' not found" % model_name
  else:
    raise Exception(body)

def run1(in_desc, out_desc, ctype, body):
  code1,body1 = fastscore.put("engine", "/1/job/model", ctype, body)
  if code1 != 204:
    raise Exception(body1)
  print "Model sent to engine"
  code2,body2 = fastscore.put("engine", "/1/job/stream/in", "application/json", in_desc) 
  if code2 != 204:
    raise Exception(body2)
  print "Input stream set"
  code3,body3 = fastscore.put("engine", "/1/job/stream/out", "application/json", out_desc) 
  if code3 != 204:
    raise Exception(body3)
  print "Output stream set"
  print "The engine is running"

def get_stream_desc(name):
  code,body = fastscore.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    return body
  else:
    raise Exception(body)

def discard_desc():
  return '{"type":"discard", "connect":{}}'

def scale(args):
  n = int(args["num-jets"])
  code,body = fastscore.post("engine", "/1/job/scale?n=%d" % n)
  if code == 204:
    print "Ok"
  else:
    raise Exception(body)

def status(args):
  code,body = fastscore.get("engine", "/1/job/status")
  if code == 200:
    print json.dumps(json.loads(body), indent=2)
  else:
    raise Exception(body)

def output(args):
  raise Exception("TODO")

def statistics(args):
  code,body = fastscore.get("engine", "/1/job/status")
  if code == 200:
    status = json.loads(body)
    print "Streams:"
    print format_stats1(status)
    print "Jets:"
    print format_stats2(status)
  else:
    raise Exception(body)

def format_stats1(status):
  ni = "-"
  bi = "-"
  if status["input"] != None:
    ni = status["input"]["total_records"]
    bi = status["input"]["total_bytes"]
  no = "-"
  bo = "-"
  if status["output"] != None:
    no = status["output"]["total_records"]
    bo = status["output"]["total_bytes"]
  headers = ["","records", "bytes"]
  t = [["input",ni,bi],
       ["output",no,bo]]
  return tabulate(t, headers=headers)

def format_stats2(status):
  t = [ [x["pid"],fmt1(x, "total_consumed"),fmt1(x, "total_produced")]
            for x in status["jets"] ]
  headers = ["pid","in","out"]
  return tabulate(t,  headers=headers)

def fmt1(x, f):
  t = x["run_time"]
  rate = x[f] / t
  return "%d (%.1f/s)" % (x[f],rate)

def statistics0(args):
  raise Exception("TODO")

def memory(args):
  raise Exception("TODO")

