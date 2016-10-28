
import sys
import json
import base64

import service
from service import engine_api_name

def run(args):
  model_name = args["model-name"]
  in_desc = get_stream_desc(args["in-stream-name"])
  out_desc = get_stream_desc(args["out-stream-name"]) \
                  if "out-stream-name" in args else discard_desc()
  code,body,ctype = service.get_with_ct("model-manage", "/1/model/%s" % model_name)
  if code == 200:
    att = attachments(model_name)
    run1(in_desc, out_desc, ctype, body, attachments=att)
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
  code,body,ctype = service.get_with_ct("model-manage",
                  "/1/model/%s/attachment/%s" % (model_name,att_name))
  if code == 200:
    return (att_name,body,ctype)
  else:
    raise Exception(body)

def run1(in_desc, out_desc, ctype, body, attachments=[]):
  if attachments == []:
    code1,body1 = service.put(engine_api_name(), "/1/job/model", ctype, body)
  else:
    parts = [ ('attachments',x) for x in attachments ]
    parts.append( ('model',('(source)',body,ctype)) )
    code1,body1 = service.put_multi(engine_api_name(), "/1/job/model", parts)
  if code1 != 204:
    raise Exception(body1)
  print "Model sent to engine"
  code2,body2 = service.put(engine_api_name(), "/1/job/stream/in", "application/json", in_desc)
  if code2 != 204:
    raise Exception(body2)
  print "Input stream set"
  code3,body3 = service.put(engine_api_name(), "/1/job/stream/out", "application/json", out_desc)
  if code3 != 204:
    raise Exception(body3)
  print "Output stream set"
  print "The engine is running"

def debug(args):
  model_name = args["model-name"]
  in_desc = get_stream_desc(args["in-stream-name"])
  out_desc = get_stream_desc(args["out-stream-name"]) \
                  if "out-stream-name" in args else discard_desc()
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
  code,body = service.get("model-manage", "/1/stream/%s" % name)
  if code == 200:
    return body
  elif code == 404:
    raise Exception("Stream '%s' not found" % name)
  else:
    raise Exception(body)

def discard_desc():
  return '{"Transport":{"Type":"discard"}}'

def scale(args):
  n = int(args["num-jets"])
  code,body = service.post(engine_api_name(), "/1/job/scale?n=%d" % n)
  if code == 204:
    print "Model scaling successful"
  else:
    raise Exception(body)

def stop(args):
  code,body = service.delete(engine_api_name(), "/1/job")
  if code == 204:
    print "Engine stopped"
  else:
    raise Exception(body)

def ctype_to_type(ctype):
  if ctype == "application/vnd.pfa+json":
    return "pfa"
  elif ctype == "application/vnd.ppfa":
    return "ppfa"
  elif ctype == "application/x-yaml":
    return "yaml"
  elif ctype == "application/x-python":
    return "python"
  elif ctype == "application/x-r":
    return "r"
  else:
    raise Exception("%s not recognized" % ctype)

def att_ctype_to_type(ctype):
  if ctype == "application/zip":
    return "zip"
  elif ctype == "application/gzip":
    return "tgz"
  else:
    raise Exception("%s not recognized" % ctype)

