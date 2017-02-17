
import json
from tabulate import tabulate
import service

def install(args):
  inst_name = args["instance-name"]
  sensor_name = args["sensor-name"]
  code,body = service.get("model-manage", "/1/sensor/%s" % sensor_name)
  if code == 200:
    install_sensor(inst_name, sensor_name, body)
  elif code == 404:
    print "Sensor '%s' not found" % sensor_name

def install_sensor(inst_name, sensor_name, desc):
  code,body = service.post(inst_name, "/1/control/sensor",
                            ctype="application/json", data=desc, generic=False)
  if code == 200:
    id = json.loads(body.decode('utf-8'))["id"]
    print "Sensor '%s' installed [%d]" % (sensor_name,id)
  else:
    raise Exception(body.decode('utf-8'))

def inspect(args):
  id = args["tap-id"]
  inst_name = args["instance-name"]
  code,body = service.get(inst_name, "/1/control/sensor/%s" % id, generic=False)
  if code == 200:
    print json.dumps(json.loads(body.decode('utf-8')), indent=2)
  else:
    raise Exception(body.decode('utf-8'))

def list(args):
  inst_name = args["instance-name"]
  code,body = service.get(inst_name, "/1/control/sensor", generic=False)
  if code == 200:
    t = [ [x["id"],x["tap"],"Yes" if x["active"] else "No"] for x in json.loads(body) ]
    print tabulate(t, headers=["Id","Tap","Active"])
  else:
    raise Exception(body)

def available(args):
  inst_name = args["instance-name"]
  code,body = service.get(inst_name, "/1/control/sensor/available", generic=False)
  if code == 200:
    for point in json.loads(body.decode('utf-8')):
      if not point.startswith("sys.test.") or service.options["verbose"] > 0:
        print point
  else:
    raise Exception(body.decode('utf-8'))

def uninstall(args):
  id = args["tap-id"]
  inst_name = args["instance-name"]
  code,body = service.delete(inst_name, "/1/control/sensor/%s" % id, generic=False)
  if code == 204:
    print "Sensor [%s] uninstalled" % id
  elif code == 404:
    print "Sensor [%s] not installed on %s" % (id,inst_name)
  else:
    raise Exception(body.decode('utf-8'))

def yes_no(flag):
  return "Yes" if flag else "No"

