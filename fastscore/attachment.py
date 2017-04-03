
import os
import json

import service

def list(args):
  model_name = args["model-name"]
  code,body = service.get("model-manage", "/1/model/%s/attachment" % model_name)
  if code == 200:
    for x in json.loads(body.decode('utf-8')):
      print x
  else:
    raise Exception(body.decode('utf-8'))

def upload(args):
  model_name = args["model-name"]
  resource = args["att-file"]
  if not os.path.exists(resource):
    raise Exception("%s not found" % resource)
  with open(resource, "rb") as f:
    data = f.read()
    att_name = os.path.basename(resource)
    code,body = service.put("model-manage",
                    "/1/model/%s/attachment/%s" % (model_name,att_name),
                    guess_att_ctype(resource), data)
    if code == 201:
      print "Attachment '%s' added to model '%s'" % (att_name,model_name)
    elif code == 204:
      print "Attachment '%s' updated" % att_name
    else:
      raise Exception(body.decode('utf-8'))

def download(args):
  model_name = args["model-name"]
  att_name = args["att-name"]
  code,str = service.get_str("model-manage",
                    "/1/model/%s/attachment/%s" % (model_name,att_name))
  if code == 200:
    with open(att_name, "w") as f:
      f.write(str.decode('utf-8'))
    print "Attachment written to %s" % att_name
  elif code == 404:
    print "Attachment '%s' not found" % att_name
  else:
    raise Exception(str.read())

def remove(args):
  model_name = args["model-name"]
  att_name = args["att-name"]
  code,body = service.delete("model-manage",
            "/1/model/%s/attachment/%s" % (model_name,att_name))
  if code == 204:
    print "Attachment '%s' removed" % att_name
  elif code == 404:
    print "Attachment '%s' not found" % att_name
  else:
    raise Exception(body.decode('utf-8'))

def guess_att_ctype(resource):
  _,ext = os.path.splitext(resource)
  if ext == ".zip":
    return "application/zip"
  elif ext == ".gz":
    return "application/gzip"
  else:
    raise Exception("%s must have a proper extension (.zip, .gz)" % resource)

