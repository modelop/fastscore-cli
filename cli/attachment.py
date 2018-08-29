
from os import rename

from fastscore.model import Attachment
from fastscore import FastScoreError

from tabulate import tabulate
import os

KNOWN_ATTACHMENT_EXTENSIONS = {
    '.zip':    'zip',
    '.tar.gz': 'tgz',
    '.tgz':    'tgz'
}

def roster(connect, model_name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    if not verbose:
        for x in model.attachments.names():
            print x
    else:
        t = [ [x.name,x.atype,x.datasize] for x in model.attachments ]
        if len(t) > 0:
            print tabulate(t, headers=["Name","Type","Size"])
        else:
            print "No attachments found"

def upload(connect, model_name, file_to_upload, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    #f = open(file_to_upload)
    filename = os.path.basename(file_to_upload)
    aname = filename
    atype = guess_attachment_type(filename)
    att = Attachment(aname, atype=atype, datafile=file_to_upload, model=model)
    att.upload()
    if verbose:
        print "Attachment uploaded"

def download(connect, model_name, att_name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    att = mm.models[model_name].attachments[att_name]
    rename(att.datafile, att_name)
    if verbose:
        print "Attachment downloaded"

def remove(connect, model_name, att_name, verbose=False, **kwargs):
    mm = connect.lookup('model-manage')
    model = mm.models[model_name]
    del model.attachments[att_name]
    if verbose:
        print "Attachment removed"

def guess_attachment_type(filename):
    for pat,atype in KNOWN_ATTACHMENT_EXTENSIONS.items():
        if filename.endswith(pat):
            return atype
    known = ", ".join(KNOWN_ATTACHMENT_EXTENSIONS.keys())
    raise FastScoreError("%s must have a proper extension (%s)" % (filename,known))

