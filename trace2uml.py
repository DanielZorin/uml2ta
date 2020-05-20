import sys, pickle
from UPPAAL.Trace import Trace

assert(__name__ == '__main__')
'''
if len(sys.argv) != 3:
    print "Usage python ./trace2uml.py model.xtr states.upp"
    exit()
  
args = sys.argv[1:]
tracefile = args[1]
statesfile = args[2]
f = open(statesfile, "rb")
data = pickle.load(f)
f.close()
'''
tracefile = "C:\\Users\\acer\\Desktop\\tl.trace.xtr"
statesfile = "C:\\Users\\acer\\Desktop\\tl.upp"
f = open(statesfile, "rb")
data = pickle.load(f)
f.close()
tr = Trace()
'''for i in data["states"].keys():
    for s in data["states"][i].values():
        print s, tr.getName(s, data)'''
tr.Import(tracefile, data)
res = tr.PrintTrace(data, True, True)
f = open("C:\\Users\\acer\\Desktop\\umltrace.txt", "w")
f.write(res)
f.close()
