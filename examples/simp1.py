import pickle

attachment = None

class simpleclass:
    def return1(self):
        return 1
    def return2(self):
        return 2

def begin():
  try:
     with open('simpleattach.pkl','r') as f:
        global attachment 
        print "unpickling"
        attachment = pickle.load(f)
        print "unpickled:", attachment
  except Exception as e:
    print(e)

def action(datum):
    print "action: ", attachment
    yield str(attachment.return1())
    

def end():
    pass

