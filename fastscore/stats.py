
import json
from tabulate import tabulate

import service
from service import engine_api_name

def status(args):
  status = get_status()
  print json.dumps(status, indent=2)

def get_status():
  code,body = service.get(engine_api_name(), "/1/job/status")
  if code == 200:
    return json.loads(body.decode('utf-8'))
  else:
    raise Exception(body.decode('utf-8'))

def statistics(args):
  status = get_status()
  try:
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
  except Exception as e:
    if e.message != 'jets':
        raise
    else:
      code,body = service.get(engine_api_name(), "/1/job/statistics")
      if code == 200:
          print json.dumps(json.loads(body.decode('utf-8')), indent=2)
      else:
          raise Exception(body.decode('utf-8'))

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
  code,body = service.delete(engine_api_name(), "/1/job/statistics")
  if code == 204:
    print "Reset"
  else:
    raise Exception(body.decode('utf-8'))

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

