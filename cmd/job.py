
import sys
import json

import fastscore

def run(args):
  model_name = args["model-name"]
  in_desc = get_stream_desc(args["in-stream-name"])
  out_desc = get_stream_desc(args["out-stream-name"]) \
                  if "out-stream-name" in args else discard_desc()
  code,body,ctype = fastscore.get_with_ct("model-manage", "/1/model/%s" % model_name)
  if code == 200:
    att = attachments(model_name)
    run1(in_desc, out_desc, ctype, body, attachments=att)
  elif code == 404:
    print "Model '%s' not found" % model_name
  else:
    raise Exception(body)

def attachments(model_name):
  code,body = fastscore.get("model-manage", "/1/model/%s/attachment" % model_name)
  if code == 200:
    return [ get_att(model_name, att_name) for att_name in json.loads(body) ]
  else:
    raise Exception(body)

def get_att(model_name, att_name):
  code,body,ctype = fastscore.get_with_ct("model-manage",
                  "/1/model/%s/attachment/%s" % (model_name,att_name))
  if code == 200:
    return (att_name,body,ctype)
  else:
    raise Exception(body)

def run1(in_desc, out_desc, ctype, body, attachments=[]):
  if attachments == []:
    code1,body1 = fastscore.put("engine", "/1/job/model", ctype, body)
  else:
    parts = [ ('attachments',x) for x in attachments ]
    parts.append( ('model',('(source)',body,ctype)) )
    code1,body1 = fastscore.put_multi("engine", "/1/job/model", parts)
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
  elif code == 404:
    raise Exception("Stream '%s' not found" % name)
  else:
    raise Exception(body)

def discard_desc():
  return '{"type":"discard", "connect":{}}'

def scale(args):
  n = int(args["num-jets"])
  code,body = fastscore.post("engine", "/1/job/scale?n=%d" % n)
  if code == 204:
    print "Model scaling successful"
  else:
    raise Exception(body)

def stop(args):
  code,body = fastscore.delete("engine", "/1/job")
  if code == 204:
    print "Engine stopped"
  else:
    raise Exception(body)

