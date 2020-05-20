import xml.dom.minidom

class Transition:
    ''' Transition in UPPAAL diagram

    :param src: source :class:`~UPPAAL.Location.Location`
    :param dst: source :class:`~UPPAAL.Location.Location`
    :param guard: guard expression
    :param sync: synchronization
    '''
    def __init__(self, src, dst, guard = None, sync = None):
        self.src = src
        self.dst = dst
        self.sync = sync
        self.select = []
        self.guard = None
        self.assign = None
        if guard:
            self.addGuard(str(guard))
    
    def addGuard(self, s):
        '''Adds a new guard (new guard = old guard AND s)'''
        if self.guard == None or self.guard == "true":
            self.guard = s
        else:
            self.guard = "(" + self.guard + ") && " + s
            
    def addAssign(self, s):
        ''' Adds a new assignment'''
        if s is None:
            return
        if self.assign == None:
            self.assign = str(s)
        else:
            self.assign = str(self.assign) + ", " + str(s)
            
    def addSync(self, s):
        ''' Adds synchronization'''
        self.sync = s;
        
    def addSelect(self, start, end):
        ''' Add random selection operation
        NB: Bool variables are equivalent to int [0,1]
        Trying to select from bool is an error in UPPAAL'''
        name = 'random' + str(len(self.select))
        self.select.append(name + " : int [" + str(start) + "," + str(end) + "]")   
        return name
            
    def GetXml(self):
        ''' :returns: xml.dom.minidom elements

        <transition>

            <source ref="id1"/>

            <target ref="id0"/>

            <label kind="select">select</label>

            <label kind="guard">guard</label>

            <label kind="synchronisation">sync</label>

            <label kind="assignment">update</label>

        </transition>
        '''   
        dom = xml.dom.minidom.Document()
        root = dom.createElement("transition")
        source = dom.createElement("source")
        source.setAttribute("ref", self.src.name)
        target = dom.createElement("target")
        target.setAttribute("ref", self.dst.name)
        root.appendChild(source)
        root.appendChild(target)

        if self.sync != None:
            labelsync = dom.createElement("label")
            labelsync.setAttribute("kind", "synchronisation")
            inv = dom.createTextNode(self.sync)
            labelsync.appendChild(inv)
            root.appendChild(labelsync)
        
        if self.guard != None:
            labelguard = dom.createElement("label")
            labelguard.setAttribute("kind", "guard")
            g = dom.createTextNode(str(self.guard))
            labelguard.appendChild(g)
            root.appendChild(labelguard) 
            
        if self.assign != None:
            labelassign = dom.createElement("label")
            labelassign.setAttribute("kind", "assignment")
            a = dom.createTextNode(self.assign)
            labelassign.appendChild(a)
            root.appendChild(labelassign)
        
        if self.select != []:
            labelselect = dom.createElement("label")
            labelselect.setAttribute("kind", "select")
            s = dom.createTextNode(", ".join(self.select))
            labelselect.appendChild(s)
            root.appendChild(labelselect)       
        
        return root