
import json
from tabulate import tabulate
import locale

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
  status = get_status()
  print json.dumps(status, indent=2)

def get_status():
  code,body = fastscore.get("engine", "/1/job/status")
  if code == 200:
    return json.loads(body)
  else:
    raise Exception(body)
  
def output(args):
  raise Exception("TODO")

def statistics(args):
  status = get_status()
  jets = status["jets"]
  for i in range(len(jets)):
    jets[i]["name"] = "jet-" + str(i+1)
  t = [ stat_line(x) for x in jets ]
  if len(jets) > 1:
    summary = {"name":"TOTAL",
               "total_consumed": sum([ x["total_consumed"] for x in jets ]),
               "total_produced": sum([ x["total_produced"] for x in jets ]),
               "run_time": max([ x["run_time"] for x in jets ])}
    t.append(stat_line(summary))
  headers = ["name","total-in","rate-in, rec/s",
                    "total-out","rate-out, rec/s"]
  print tabulate(t, headers=headers)

def stat_line(x):
	secs = x["run_time"]
	rate_in = x["total_consumed"] / secs
	rate_out = x["total_produced"] / secs
	return [x["name"],x["total_consumed"],rate_in,
									  x["total_produced"],rate_out]

def statistics_io(args):
  status = get_status()
  t = [io_line(status, "input"),
       io_line(status, "output")]
  headers = ["","count","size",""]
  print tabulate(t, headers=headers)

def io_line(status, dir):
  x = status[dir]
  if x == None:
    return [dir,0,0,""]
  (b,unit) = human_fmt(x["total_bytes"])
  return [dir,x["total_records"],b,unit]

def statistics0(args):
  code,body = fastscore.delete("engine", "/1/job/statistics")
  if code == 204:
    print "Reset"
  else:
    raise Exception(body)

def memory(args):
  status = get_status()
  jets = status["jets"]
  for i in range(len(jets)):
    jets[i]["name"] = "jet-" + str(i+1)
  t = [ mem_line(x) for x in jets ]
  if len(jets) > 1:
    summary = {"name":"TOTAL",
               "memory": sum([ x["memory"] for x in jets ])}
    t.append(mem_line(summary))
  headers = ["name","size",""]
  print tabulate(t, headers=headers)

def mem_line(x):
  (b,unit) = human_fmt(x["memory"])
  return [x["name"],b,unit]

def human_fmt(num, suffix='B'):
  for unit in ['','KB','MB','GB','TB','PB','EB','ZB']:
    if abs(num) < 1024.0:
      return (num,unit)
    num /= 1024.0
  return (num,'YB')

