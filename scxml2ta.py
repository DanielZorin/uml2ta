import sys

from UMLStateMachine.Model import Model
from TranslationAlgorithm import main_block
from Normalize import NormalizeStateMachine

import logging 

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Translation XMI to TA') # TODO move to Model

from optparse import OptionParser

assert(__name__ == '__main__')

if len(sys.argv) != 2:
    print "Usage python ./scxml2ta.py model.scxml"
    exit()

uml_model = Model()
uml_model.importFromScxml(args[1])
name = args[1][:args[1].index(".")]
norm, renamed = NormalizeStateMachine(uml_model.state_machines[args[1]], True)
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