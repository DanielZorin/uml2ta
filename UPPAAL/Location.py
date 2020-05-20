import xml.dom.minidom

class Location:
    ''' UPPAAL state
    
    :param name: state name
    :param invariant: invartian expression
    :param commit: committed or not
    :param init: initial or not
    :param urgent: urgent or not'''

    oldname = None
    '''Name of the corresponding state in UML'''
    
    def __init__(self, name, invariant="true", commit=False, init=False, urgent=False):
        self.name = name
        self.iscommit = commit
        self.isinit = init
        self.isurgent = urgent
        self.invariant = invariant
                
    def addInvariant(self, s):
        ''' And a new clause to the invariant'''
        if self.invariant == None or self.invariant == "true":
            self.invariant = str(s)
        else:
            self.invariant = self.invariant + " && " + str(s)
                 
    def GetXml(self):
        ''' :returns: xml.dom.minidom elements  
             
        Example:
   
        <location id="id1">

            <name>name1</name>

            <label kind="invariant">invariant1</label>

            <committed/>

        </location>'''
        dom = xml.dom.minidom.Document()
        root = dom.createElement("location")
        name = dom.createElement("name")
        txt = dom.createTextNode(self.name)
        name.appendChild(txt)
        root.appendChild(name)
        root.setAttribute("id", self.name)
        
        if self.invariant:
            label = dom.createElement("label")
            label.setAttribute("kind", "invariant")
            inv = dom.createTextNode(self.invariant)
            label.appendChild(inv)
            root.appendChild(label)

        if self.iscommit:
            root.appendChild(dom.createElement("committed"))
        elif self.isurgent:
            root.appendChild(dom.createElement("urgent"))
        return root