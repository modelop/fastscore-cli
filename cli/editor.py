
from os import environ, system
from md5 import md5

def run_editor(text, name):
    checksum = md5(text).hexdigest()
    filename = "/tmp/" + name
    with open(filename, "w") as f:
        f.write(text)
    editor = environ['EDITOR'] if 'EDITOR' in environ else 'vi'
    status = system("%s %s" % (editor,filename))
    if status != 0:
        return None
    text1 = open(filename).read()
    return text1 if md5(text1).hexdigest() != checksum else None

