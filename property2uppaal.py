import sys, pickle
statesfile = "C:\\Users\\juan\\Documents\\Work\\modeling\\src\\uml2ta\\tl.upp"
f = open(statesfile, "rb")
data = pickle.load(f)
f.close()
for s in data["renamed"]:
    print s
text = "A[] !deadlock \n A[] y > 0 \n b4 --> b7"
properties = text.split("\n")
signs = ["A[]", "A<>", "E<>", "E[]", "-->", "<=", ">=", "==", ">", "<", "deadlock", "!"]
print data
print "==================="
for p in properties:
    vars = p
    for s in signs:
        vars = vars.replace(s, " ")
    vars = [s for s in vars.split(" ") if s != ""]
    oldvars = list(vars)
    for i in range(len(vars)):
        for j in range(len(data["renamed"])):
            if data["renamed"][j][0] == vars[i]:
                vars[i] = data["renamed"][j][1]
        if vars[i] in data["statenames"]:
            vars[i] = data["statenames"][vars[i]]
        for i in range(len(data["renamedvars"])):
            print data["renamedvars"][i]
            pass
    for i in range(len(vars)):
        p = p.replace(oldvars[i], vars[i])
    print p
x = 9