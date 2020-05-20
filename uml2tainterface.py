import sys, pickle

from UMLStateMachine.Model import Model
from TranslationAlgorithm import main_block
from Normalize import NormalizeStateMachine
from UPPAAL.Trace import Trace

import logging 

logging.basicConfig(level=logging.WARNING)
import_logger = logging.getLogger('Translation XMI to TA') # TODO move to Model

def Parse(xmi):
    ''' Parses the model and returns it'''
    uml_model = Model()
    uml_model.importFromXMI(xmi)
    return uml_model

def Launch(model, name, flatten, wcet, outfile, uppfile):
    ''' Intreface for `uml2ta` '''
    norm, renamed = NormalizeStateMachine(model.state_machines[name], flatten, wcet)
    ta = main_block(norm, model.triggers)

    if sys.platform.startswith("linux"):
        from pyuppaal import pyuppaal
        f = open(outfile, "w")
        f.write(ta.ExportToXml())
        f.close()
        f = open(outfile, "r")
        uppaal = pyuppaal.from_xml(f)
        for u in uppaal.templates:
            u.layout()
        
        f.close()
        f = open(outfile, "w")
        f.write(uppaal.to_xml())
        f.close()
        ta.ExportToUpp(uppfile, renamed)
    elif sys.platform.startswith("win"):
        f = open(outfile, "w")
        f.write(ta.ExportToXml())
        f.close()
        ta.ExportToUpp(uppfile, renamed)

def LaunchScxmlToUppaal(scxml, name, outfile, uppfile):
    ''' Intreface for `scxml2ta` '''
    uml_model = Model()
    uml_model.importFromScxml(scxml)
    for k in uml_model.state_machines.keys():
        name = k
    Launch(uml_model, name, True, False, outfile, uppfile)

def LaunchScxml(model, name, outfile):
    ''' Intreface for `xmi2scxml` '''
    norm = NormalizeStateMachine(model.state_machines[name], True)
    res = norm[0].exportToScxml()
    f = open(outfile, "w")
    f.write(res)
    f.close()

def ConvertTrace(tracefile, statesfile, resfile):
    ''' Intreface for `trace2uml` '''
    f = open(statesfile, "rb")
    data = pickle.load(f)
    f.close()
    tr = Trace()
    tr.Import(tracefile, data)
    res = tr.PrintTrace(data, True, True)
    f = open(resfile, "w")
    f.write(res)
    f.close()