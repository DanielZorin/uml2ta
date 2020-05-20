from UPPAAL.Transition import Transition
import xml.dom.minidom

class Process:
    ''' UPPAAL diagram
    
    :param name: process name'''
    def __init__(self, name):
        self.name = name
        self.locations = {}
        self.transitions = []
        
    def addLocation(self, loc):
        ''' Add a :class:`~UPPAAL.Location.Location` to the process'''
        self.locations[loc.name] = loc
        
    def addTransition(self, t):
        ''' Add a :class:`~UPPAAL.Transition.Transition` to the process'''
        self.transitions.append(t)
            
    def findTransitions(self, src=None, dst=None): 
        ''' Returns a list of transitions matching the wildcard

        :param src: source node. Matches any node if None
        :param dst: source node. Matches any node if None'''  
        return [t for t in self.transitions if (src == None or t.src == src) and (dst == None or t.dst == dst)]
    
    def ClearUp(self):
        locs = self.locations
        self.locations = {}
        for k in locs.keys():
            if len(self.findTransitions(src=locs[k])) > 0 or len(self.findTransitions(dst=locs[k])) > 0:
                self.addLocation(locs[k])

    def GetXml(self):
        ''':returns: xml.dom.minidom elements  
             
        Example:

        <template>

        <name>p1</name>

        <location id="id0"><name>name2</name><label kind="invariant">invariant2</label></location>

        <location id="id1"><name>name1</name><label kind="invariant">invariant1</label><committed/></location>

        <init ref="id1"/>

        <transition><source ref="id1"/><target ref="id0"/><label kind="select">select</label>

            <label kind="guard">guard</label><label kind="synchronisation">sync</label>

            <label kind="assignment">update</label></transition>

        </template>
        '''   
        dom = xml.dom.minidom.Document()
        root = dom.createElement("template")
        name = dom.createElement("name")
        txt = dom.createTextNode(self.name)
        name.appendChild(txt)
        root.appendChild(name)

        # <init> MUST be after all <location> tags
        inits = []
        for l in self.locations.values():
            root.appendChild(l.GetXml())
            if l.isinit:
                init = dom.createElement("init")
                init.setAttribute("ref", l.name)
                inits.append(init)
        for init in inits:
            root.appendChild(init)
            
        for t in self.transitions:
            root.appendChild(t.GetXml())
        return root