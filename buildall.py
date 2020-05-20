import sys

from UMLStateMachine.Model import Model
from TranslationAlgorithmV2 import main_block
from Normalize import NormalizeStateMachine

import logging 

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Translation XMI to TA') # TODO move to Model

from optparse import OptionParser

assert(__name__ == '__main__')

for i in range(1, 11):
    print "test ", i
    uml_model = Model()
    num = str(i) if i > 9 else "0" + str(i)
    uml_model.importFromXMI("test_models/test_set/test" + num + ".xmi")
    norm, renamed = NormalizeStateMachine(uml_model.state_machines["HTA"], True)
    ta = main_block(norm, uml_model.triggers)
    f = open("test_models/test_set/test" + num + ".xml", "w")
    f.write(ta.ExportToXml())
    f.close()

uml_model = Model()
uml_model.importFromScxml("test_models/Processor.scxml")
norm, renamed = NormalizeStateMachine(uml_model.state_machines["test_models/Processor.scxml"], True)
ta = main_block(norm, uml_model.triggers)

uml_model = Model()
uml_model.importFromXMI("test_models/test2.xmi")
norm, renamed = NormalizeStateMachine(uml_model.state_machines["sm1"], True)
ta = main_block(norm, uml_model.triggers)
'''
uml_model = Model()
uml_model.importFromXMI("test_models/traffic-light.xmi")
norm, renamed = NormalizeStateMachine(uml_model.state_machines["TrafficLight"], True)
ta = main_block(norm, uml_model.triggers)
'''
uml_model = Model()
uml_model.importFromXMI("test_models/D2.xmi")
norm, renamed = NormalizeStateMachine(uml_model.state_machines["Global"], True)
ta = main_block(norm, uml_model.triggers)

uml_model = Model()
uml_model.importFromXMI("test_models/crossroads.xmi")
norm, renamed = NormalizeStateMachine(uml_model.state_machines["crossroads"], True)
ta = main_block(norm, uml_model.triggers)