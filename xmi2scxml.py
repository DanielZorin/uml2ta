import sys

from UMLStateMachine.Model import Model
from Normalize import NormalizeStateMachine

import logging 

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Translation XMI to TA') # TODO move to Model

from optparse import OptionParser

assert(__name__ == '__main__')

if len(sys.argv) == 1:
    print "Usage python ./xmi2scxml.py model.xmi [state_machine1 ... state_machinen]"
    exit()

args = sys.argv[1:]

uml_model = Model()
uml_model.importFromXMI(args[0])

if len(args) <= 1:
    sm_names = [sm.name for sm in uml_model.state_machines.values()]
else:
    sm_names = args[1:]

for name in sm_names:
    norm = NormalizeStateMachine(uml_model.state_machines[name], flatten)
    res = norm.exportToScxml()
    f = open(name + ".scxml", "w")
    f.write(res)
    f.close()
