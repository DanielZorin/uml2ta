def clear(name):
    f = open(name, "r")
    s = f.readlines()
    s = s[1:]
    f.close()
    f = open(name, "w")
    for s0 in s:
        f.write(s0)
    f.close()
    
clear("ActionLexer.py")
clear("ActionParser.py")
clear("GuardLexer.py")
clear("GuardParser.py")
clear("DeclarationsLexer.py")
clear("DeclarationsParser.py")