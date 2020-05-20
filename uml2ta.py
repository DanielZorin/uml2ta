import sys

from UMLStateMachine.Model import Model
from TranslationAlgorithm import main_block
from Normalize import NormalizeStateMachine

import logging 

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Translation XMI to TA') # TODO move to Model

from optparse import OptionParser

assert(__name__ == '__main__')

if len(sys.argv) == 1:
    print "Usage python ./uml2ta.py [-f/--flatten] model.xmi [state_machine1 ... state_machinen]"
    exit()
  
flatten = False
args = sys.argv[1:]
if sys.argv[1] == "-f" or sys.argv[1] == "--flatten":
    flatten = True
    if len(sys.argv) == 2:
        print "Usage python ./uml2ta.py [-f/--flatten] model.xmi [state_machine1 ... state_machinen]"
        exit()
    args = sys.argv[2:]

uml_model = Model()
uml_model.importFromXMI(args[0])

if len(args) <= 1:
    sm_names = [sm.name for sm in uml_model.state_machines.values()]
else:
    sm_names = args[1:]

for k in sm_names:
    name = k
    norm, renamed = NormalizeStateMachine(uml_model.state_machines[k], flatten)
    ta = main_block(norm, uml_model.triggers)

    if sys.platform.startswith("linux"):
        from pyuppaal import pyuppaal
        f = open(name + "-uppaal.xml", "w")
        f.write(ta.ExportToXml())
        f.close()
        f = open(name + "-uppaal.xml", "r")
        uppaal = pyuppaal.from_xml(f)
        for u in uppaal.templates:
            u.layout()
        
        f.close()
        f = open(name + "-uppaal.xml", "w")
        f.write(uppaal.to_xml())
        f.close()
        ta.ExportToUpp(name + ".upp", renamed)
    elif sys.platform.startswith("win"):
        f = open(name + "-uppaal.xml", "w")
        f.write(ta.ExportToXml())
        f.close()
        ta.ExportToUpp(name + ".upp", renamed)