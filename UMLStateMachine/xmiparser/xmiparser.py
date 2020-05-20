# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        XMIParser.py
# Purpose:     Parse XMI (UML-model) and provide a logical model of it
#
# Author:      Philipp Auersperg
#
# Created:     2003/19/07
# Copyright:   (c) 2003-2008 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

from UMLStateMachine.xmiparser.xmi import *

class PseudoElement(object):
    #urgh, needed to pretend a class
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def getName(self):
        return self.name

    def getModuleName(self):
        return self.getName()


class XMIElement(object):
    package = None
    parent = None

    def __init__(self, domElement=None, name='', *args, **kwargs):
        self.domElement = domElement
        self.name = name
        self.cleanName = ''
        self.atts = {}
        self.children = []
        self.maxOccurs = 1
        self.complex = 0
        self.type = 'NoneType'
        self.attributeDefs = []
        self.methodDefs = []
        self.id = ''
        self.subTypes = []
        self.stereoTypes = []
        self.clientDependencies = []
        # Space to store values by external access. Use annotate() to
        # store values in this dict, and getAnnotation() to fetch it.
        self.annotations = {}
        # Take kwargs as attributes
        self.__dict__.update(kwargs)
        if domElement:
            allObjects[domElement.getAttribute('xmi.id')] = self
            self.initFromDOM(domElement)
            self.buildChildren(domElement)

    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__,self.getName())
    
    __repr__=__str__
    def getId(self):
        return self.id

    def getParent(self):
        return self.parent

    def setParent(self, parent):
        self.parent = parent

    def parseTaggedValues(self):
        """Gather the tagnames and tagvalues for the element.
        """
        log.debug("Gathering the taggedvalues for element %s.", self.name)
        tgvsm = getElementByTagName(self.domElement, XMI.TAGGED_VALUE_MODEL,
                                    default=None, recursive=0)
        if tgvsm is None:
            log.debug("Found nothing.")
            return
        tgvs = getElementsByTagName(tgvsm, XMI.TAGGED_VALUE, recursive=0)
        for tgv in tgvs:
            try:
                tagname, tagvalue = XMI.getTaggedValue(tgv)
                log.debug("Found tag '%s' with value '%s'.", tagname, tagvalue)
                if self.taggedValues.has_key(tagname):
                    log.debug("Invoking Poseidon multiline fix for "
                              "tagname '%s'.", tagname)
                    self.taggedValues[tagname] += '\n'+tagvalue
                else:
                    self.taggedValues[tagname] = tagvalue
            except TypeError, e:
                log.warn("Broken tagged value in id '%s'.",
                         XMI.getId(self.domElement))
        log.debug("Found the following tagged values: %r.",
                  self.getTaggedValues())

    def setTaggedValue(self, k, v):
        self.taggedValues[k] = v

    def initFromDOM(self, domElement):
        if not domElement:
            domElement = self.domElement

        if domElement:
            self.id = str(domElement.getAttribute('xmi.id'))
            self.name = XMI.getName(domElement)
            log.debug("Initializing from DOM: name='%s', id='%s'.",
                      self.name, self.id)
            self.parseTaggedValues()
            self.calculateStereoType()
            mult = getElementByTagName(domElement, XMI.MULTIPLICITY, None)
            if mult:
                maxNodes = mult.getElementsByTagName(XMI.MULT_MAX)
                if maxNodes and len(maxNodes):
                    maxNode = maxNodes[0]
                    self.maxOccurs = int(getAttributeValue(maxNode))
                    if self.maxOccurs == -1:
                        self.maxOccurs = 99999
                    log.debug("maxOccurs = '%s'.", self.maxOccurs)
            domElement.xmiElement = self

    def addChild(self, element):
        self.children.append(element)

    def addSubType(self, st):
        self.subTypes.append(st)

    def getChildren(self):
        return self.children

    def getName(self, doReplace=False):
        if self.name:
            res = self.name
        else:
            res = self.id
        return res
    
    @property
    def classcategory(self):
        return "%s.%s" % (self.__class__.__module__, self.__class__.__name__)

    def getTaggedValue(self, name, default=''):
        log.debug("Getting value for tag '%s' (default=%s). "
                  "Note: we're not doing this recursively.",
                  name, default)
#===============================================================================
#        if not tgvRegistry.isRegistered(name, self.classcategory):
#            # The registry does the complaining :-)
#            pass
#===============================================================================
        res = self.taggedValues.get(name, default)
        log.debug("Returning value '%s',", res)
        return res

    def hasTaggedValue(self, name):
        return self.taggedValues.has_key(name)

    def hasAttributeWithTaggedValue(self, tag, value=None):
        """Return True if any attribute has a TGV 'tag'.

        If given, also check for a matching value.
        """
        log.debug("Searching for presence of an attribute with tag '%s'.", tag)
        if value:
            log.debug("But, extra condition, the value should be '%s'.", value)
        attrs = self.getAttributeDefs()
        for attr in attrs:
            if attr.hasTaggedValue(tag):
                log.debug("Yep, we've found an attribute with that tag.")
                if not value:
                    # We don't have to have a specific value
                    return True
                else:
                    # We need a specific value
                    if attr.getTaggedValue(tag, None) == value:
                        return True
                    else:
                        log.debug("But, alas, the value isn't right.")
        log.debug("No, found nothing.")
        return False

    def getTaggedValues(self):
#===============================================================================
#        for tagname in self.taggedValues.keys():
#            if not tgvRegistry.isRegistered(tagname, self.classcategory, 
#                                            silent=True):
#                # The registry does the complaining :-)
#                pass
#===============================================================================
        return self.taggedValues

    def getDocumentation(self, striphtml=0, wrap=-1):
        """Return formatted documentation string.

        try to use stripogram to remove (e.g. poseidon) HTML-tags, wrap and
        indent text. If no stripogram is present it uses wrap and indent
        from own utils module.

        striphtml(boolean) -- use stripogram html2text to remove html tags

        wrap(integer) -- default: 60, set to 0: do not wrap,
                         all other >0: wrap with this value
        """

        log.debug("Trying to find documentation for this element.")
        #TODO: create an option on command line to control the page width
        log.debug("First trying a tagged value.")

        # tagged value documentation? Probably this gets the UML
        # documentation or so. I mean, having a tagged value for
        # this?!?
        # returning an empty string to get rid of the "unregistered
        # TGV" warnings.
        if True:
            return ''
        # The rest isn't executed.
        doc = self.getTaggedValue('documentation')
        if not doc:
            log.debug("Didn't find a tagged value 'documentation'. "
                      "Returning empty string.")
            return ''
        if wrap == -1:
            wrap = default_wrap_width
        if has_stripogram and striphtml:
            log.debug("Stripping html.")
            doc = html2text(doc, (), 0, 1000000).strip()
        if wrap:
            log.debug("Wrapping the documenation.")
            doc = doWrap(doc, wrap)
        log.debug("Returning documenation '%r'.",
                  doc)
        return doc

    def getUnmappedCleanName(self):
        return self.unmappedCleanName

    def setName(self, name):
        log.debug("Setting our name to '%s' the hard way. "
                  "The automatic mechanism set it to '%s' already.",
                  name, self.getName())
        self.name = name

    def getAttrs(self):
        return self.attrs

    def getMaxOccurs(self):
        return self.maxOccurs

    def getType(self):
        return self.type

    def isComplex(self):
        return self.complex

    def addAttributeDef(self, attrs, pos=None):
        if pos is None:
            self.attributeDefs.append(attrs)
        else:
            self.attributeDefs.insert(0, attrs)

    def getAttributeDefs(self):
        return self.attributeDefs

    def getRef(self):
        return None

    def getRefs(self):
        """Returns all referenced schema names."""
        return [str(c.getRef()) for c in self.getChildren() if c.getRef()]

    def show(self, outfile, level):
        showLevel(outfile, level)
        outfile.write('Name: %s  Type: %s\n' % (self.name, self.type))
        showLevel(outfile, level)
        outfile.write('  - Complex: %d  MaxOccurs: %d\n' % \
            (self.complex, self.maxOccurs))
        showLevel(outfile, level)
        outfile.write('  - Attrs: %s\n' % self.attrs)
        showLevel(outfile, level)
        outfile.write('  - AttributeDefs: %s\n' % self.attributeDefs)
        for key in self.attributeDefs.keys():
            showLevel(outfile, level + 1)
            outfile.write('key: %s  value: %s\n' % \
                (key, self.attributeDefs[key]))
        for child in self.getChildren():
            child.show(outfile, level + 1)

    def addMethodDefs(self, m):
        if m.getName():
            self.methodDefs.append(m)

    def getCleanName(self):
        # If there is a namespace, replace it with an underscore.
        if self.getName():
            self.unmappedCleanName = str(self.getName()).translate(clean_trans)
        else:
            self.unmappedCleanName = ''
        return mapName(self.unmappedCleanName)

    def isIntrinsicType(self):
        return str(self.getType()).startswith('xs:')

    def buildChildren(self, domElement):
        pass

    def getMethodDefs(self, recursive=0):
        log.debug("Getting method definitions (recursive=%s)...", recursive)
        res = [m for m in self.methodDefs]
        log.debug("Our own methods: %r.", res)
        if recursive:
            log.debug("Also looking recursively to our parents...")
            parents = self.getGenParents(recursive=1)
            for p in parents:
                res.extend(p.getMethodDefs())
            log.debug("Our total methods: %r.", res)
        return res

    def calculateStereoType(self):
        return XMI.calculateStereoType(self)

    def setStereoType(self, st):
        self.stereoTypes = [st]

    def getStereoType(self):
        if self.stereoTypes:
            return self.stereoTypes[0]
        else:
            return None

    def addStereoType(self, st):
        log.debug("Adding stereotype '%s' to this element's internal list.", st)
        self.stereoTypes.append(st)

    def getStereoTypes(self):
        return self.stereoTypes

    def hasStereoType(self, stereotypes, umlprofile=None):
        log.debug("Looking if element has stereotype %r", stereotypes)
        if isinstance(stereotypes, (str, unicode)):
            stereotypes = [stereotypes]
        if umlprofile:
            for stereotype in stereotypes:
                found = umlprofile.findStereoTypes(entities=[self.classcategory])
                if found:
                    log.debug("Stereotype '%s' is registered.",
                              stereotype)
                else:
                    log.warn("DEVELOPERS: Stereotype '%s' isn't registered "
                             "for element '%s'.", stereotype, self.classcategory)
        for stereotype in stereotypes:
            if stereotype in self.getStereoTypes():
                return True
        return False

    def getFullQualifiedName(self):
        return self.getName()

    def getPackage(self):
        """Returns the package to which this object belongs."""
        if self.package is not None:
            return self.package
        if self.getParent():
            return self.getParent().getPackage()
        return None

    def getPath(self):
        return [self.getName()]

    def getModuleName(self, lower=False):
        """Gets the name of the module the class is in."""
        basename = self.getCleanName()
        return self.getTaggedValue('module') or \
               (lower and basename.lower() or basename)

    def annotate(self, key, value):
        self.annotations[key] = value

    def getAnnotation(self, name, default=[]):
        return self.annotations.get(name, default)

    def addClientDependency(self, dep):
        self.clientDependencies.append(dep)

    def getClientDependencies(self, includeParents=False,
                              dependencyStereotypes=None):
                                  
        res = list(self.clientDependencies)
        if includeParents:
            o = self.getParent()
            if o:
                res.extend(o.getClientDependencies(includeParents=includeParents))
                res.reverse()
        if dependencyStereotypes:
            res = [r for r in res if r.hasStereoType(dependencyStereotypes)]
        return res

    def getClientDependencyClasses(self, includeParents=False,
                                   dependencyStereotypes=None,
                                   targetStereotypes=None):
        res = [dep.getSupplier()
               for dep in self.getClientDependencies(
                   includeParents=includeParents,
                   dependencyStereotypes=dependencyStereotypes)
               if dep.getSupplier() and
                  dep.getSupplier().__class__.__name__
                  in ('XMIClass', 'XMIInterface')]

        if targetStereotypes:
            res = [r for r in res if r.hasStereoType(targetStereotypes)]

        return res

class StateMachineContainer(object):
    def __init__(self):
        self.statemachines = []
    def buildStateMachines(self, recursive=1):
        res = {}
        statemachines = self.findStateMachines()
        for m in statemachines:
            sm = XMIStateMachine(m, parent=self)
            if sm.getName():
                res[sm.getName()] = sm
                self.statemachines.append(sm)
        return res

    def addStateMachine(self, sm, reparent=0):
        if not sm in self.statemachines:
            self.statemachines.append(sm)
            if reparent:
                sm.setParent(self)
        if hasattr(self, 'isProduct') and not self.isProduct():
            self.getProduct().addStateMachine(sm, reparent=0)
        if not hasattr(self, 'isProduct'):
            self.getPackage().getProduct().addStateMachine(sm, reparent=0)

    def getStateMachines(self):
        return self.statemachines


class XMIPackage(XMIElement, StateMachineContainer):
    implements(IPackage)
    project = None
    isroot = 0

    def __init__(self, el):
        self.triggers = []
        self.comments = []
        XMIElement.__init__(self, el)
        StateMachineContainer.__init__(self)
        self.classes = []
        self.interfaces = []
        self.packages = []
        # outputDirectoryName is used when setting the output
        # directory on the command line. Effectively only used for
        # single products. Ignored when not set.
        self.outputDirectoryName = None

    def addTrigger(self, trigger):
        self.triggers.append(trigger)

    def buildTriggers(self):
        sels = getElementsByTagName(self.domElement, 'UML:TimeEvent', recursive=1)
        for sel in sels:
            if sel.parentNode.nodeName in ['UML:Transition.trigger']:
                continue
            when = getElementByTagName(sel, 'UML:TimeExpression', recursive=1)
            body = when.getAttribute('body')
            name =  sel.getAttribute('name')
            self.addTrigger(XMITimeTrigger(name, body, sel.getAttribute('xmi.id')))
        sels = getElementsByTagName(self.domElement, 'UML:SignalEvent', recursive=1)
        for sel in sels:
            if sel.parentNode.nodeName == 'UML:Transition.trigger':
                continue
            name = sel.getAttribute('name') 
            if name=="":
                log.error("Ignoring unnamed signal trigger (xmi-id=\"%s\")"%(sel.getAttribute('xmi.id'),))
            else:
                self.addTrigger(XMISignalTrigger(name, sel.getAttribute('xmi.id')))

    def addComment(self, comment):
        self.comments.append(comment)

    def buildComments(self):
        sels = getElementsByTagName(self.domElement, 'UML:Comment', recursive=1)
        for sel in sels:            
            if sel.parentNode.nodeName in ['UML:ModelElement.comment', 'UML:ModelElement.comment', 'UML:Comment.annotatedElement']:
                continue
            body = sel.getAttribute('body')
            comment_id = sel.getAttribute('xmi.id')
            a = getElementByTagName(sel, 'UML:Comment.annotatedElement', recursive=0)
            ids = [x.getAttribute('xmi.idref') for x in a.childNodes if x.nodeType == x.ELEMENT_NODE] 
            if len(ids) == 0:
                log.error('No element is annotated by comment \"%s\" (xmi-id = %s)'%(body, comment_id))
            elif len(ids) > 1:
                log.error('Several elements are associated with the same comment \"%s\" (xmi-id = %s)'%(body, comment_id))
            for id in ids:
                self.addComment(XMIComment(id, body))

    def initFromDOM(self, domElement=None):
        self.parentPackage = None
        XMIElement.initFromDOM(self, domElement)
        self.buildTriggers()
        self.buildComments()

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent
    
    def getChildren(self):
        return self.children + self.getClasses() + \
               self.getPackages() + self.getInterfaces()

    def isRoot(self):
        # TBD Handle this through the stereotype registry
        return self.isroot or self.hasStereoType(['product', 'zopeproduct',
                                                  'Product', 'ZopeProduct'])

    isProduct = isRoot

    def getPath(self, includeRoot=1, absolute=0, parent=None):
        res = []
        o = self

        if self.isProduct():
            # Products are always handled as top-level
            if includeRoot:
                return [o]
            else:
                return []

        while True:
            if includeRoot:
                res.append(o)
            if o.isProduct():
                break
            if not o.getParent():
                break
            if o == parent:
                break
            if not includeRoot:
                res.append(o)
            o = o.getParent()

        res.reverse()
        return res

    def getFilePath(self, includeRoot=1, absolute=0):
        names = [p.getModuleNameForDirectoryName() for p in
                 self.getPath(includeRoot=includeRoot, absolute=absolute)]
        if not names:
            return ''
        res = os.path.join(*names)
        return res

    def getRootPackage(self):
        o = self
        while not o.isRoot():
            o = o.getParent()
        return o

    def getProduct(self):
        o = self
        while not o.isProduct():
            o = o.getParent()
        return o

    def getProductName(self):
        return self.getProduct().getCleanName()

    def getModuleNameForDirectoryName(self):
        outdir = self.getOutputDirectoryName()
        if outdir:
            return outdir
        else:
            return self.getModuleName()

    def getOutputDirectoryName(self):
        return self.outputDirectoryName

    def setOutputDirectoryName(self, name):
        self.outputDirectoryName = name

    def getProductModuleName(self):
        return self.getProduct().getModuleName()

    def isSubPackageOf(self, parent):
        o = self
        while o:
            if o == parent:
                return True
            o = o.getParent()
        return False

    def getQualifiedName(self, ref, includeRoot=True):
        """Returns the qualified name of that package.

        Depending of the reference package 'ref' it generates an absolute
        path or a relative path if the pack(self) is a subpack of 'ref'.
        """
        path = self.getPath(includeRoot=includeRoot, parent=ref)
        return ".".join([p.getName() for p in path])


class XMIModel(XMIPackage):
    implements(IPackage)
    isroot = 1
    parent = None
    diagrams = {}
    diagramsByModel = {}

    def __init__(self, doc):
        self.document = doc
        self.content = XMI.getContent(doc)
        self.model = XMI.getModel(doc)
        XMIPackage.__init__(self, self.model)

    def findStateMachines(self):
        statemachines = getElementsByTagName(self.content, XMI.STATEMACHINE, 1)
        log.debug("Found the following state machines: %r.", statemachines)
        return statemachines

    def getAllStateMachines(self):
        res = []
        res.extend(self.getStateMachines())
        for p in self.getPackages():
            res.extend(p.getStateMachines())
        return res

class XMIStateMachine(XMIElement):
    
    def __init__(self, *args, **kwargs):        
        self.states = []    
        self.transitions = []
        self.classes = []
        XMIElement.__init__(self, *args, **kwargs)
        self.setParent(kwargs.get('parent', None))
        log.debug("Created statemachine '%s'.", self.getId())

    def initFromDOM(self, domElement=None):
        XMIElement.initFromDOM(self, domElement)
        self.buildTransitions()
        self.buildStates()
        #self.associateClasses()

    def addState(self, state):
        self.states.append(state)
        state.setParent(self)

    def getStates(self, no_duplicates=None):
        ret = []
        for s in self.states:
            if no_duplicates:
                flag_exists = 0
                for r in ret:
                    if s.getName() == r.getName():
                        flag_exists = 1
                        break
                if flag_exists:
                    continue
            ret.append(s)
        return ret

    def getStateNames(self, no_duplicates=None):
        return [s.getName() for s in
                self.getStates(no_duplicates=no_duplicates) if s.getName()]

    def getCleanStateNames(self, no_duplicates=None):
        return [s.getCleanName() for s in
                self.getStates(no_duplicates=no_duplicates) if s.getName()]

    def addTransition(self, transition):
        self.transitions.append(transition)
        transition.setParent(self)

    def getTransitions(self, no_duplicates=None):
        if not no_duplicates:
            return self.transitions
        tran = {}
        for t in self.transitions:
            if not t.getCleanName():
                continue
            if not t.getCleanName() in tran.keys():
                tran.update({t.getCleanName():t})
                log.debug("Added transition '%s' with properties %r.",
                          t.getCleanName(), t.getProps())
                continue
            for tname in tran:
                if t.getCleanName() == tname and t.hasStereoType('primary'):
                    tran.update({tname:t})

        return [tran[tname] for tname in tran]

    def getTransitionNames(self, no_duplicates=None):
        return [t.getName() for t in
                self.getTransitions(no_duplicates=no_duplicates)
                if t.getName()]


    def buildStates(self):
        def getStates(states_type):
            sels = getElementsByTagName(self.domElement, states_type, recursive=1)		
            return  [sel for sel in sels \
                if sel.parentNode.tagName not in ['UML:Transition.source', 'UML:Transition.target', 'UML:StateMachine.submachineState']] # removing RefNodes that exist in XMI produced by ArgoUML (Peter Bulychev)
        log.debug("Building states...")

        sels = getStates(XMI.PSEUDOSTATE)
        log.debug("Found %s pseudo states (like initial states).", len(sels))
        for sel in sels:	
            state = {'initial':          XMIInitialState, 
	    	     'junction':         XMIJunctionState, 
		         'choice':           XMIChoiceState, 
		         'fork':             XMIForkState, 
		         'join':             XMIJoinState, 
		         'shallowHistory':   XMIShallowHistoryState,
		         'deepHistory':      XMIDeepHistoryState,
		    }[sel.getAttribute('kind')](sel) # storing state type (Peter Bulychev)
            if getAttributeValue(sel, XMI.PSEUDOSTATE_KIND, None) == 'initial' \
               or sel.getAttribute('kind') == 'initial':
                log.debug("Initial state: '%s'.", state.getCleanName())
                state.isinitial = 1
            self.addState(state)
            
        sels  = getStates(XMI.SIMPLESTATE)
        sels += getStates(XMI.FINALSTATE)
        sels += getStates(XMI.COMPOSITESTATE)
        sels += getStates(XMI.SUBMACHINESTATE)
        sels += getStates(XMI.STUBSTATE)
        for sel in sels:
            if sel.nodeName == XMI.COMPOSITESTATE:
                #TODO: insert assert
                if sel.getAttribute('isConcurrent') == 'true':
                    state_type = XMIConcurrentCompositeState
                elif sel.parentNode.parentNode.getAttribute('isConcurrent') == 'true':
                    state_type = XMIConcurrentRegion
                else:
                    state_type = XMICompositeState
            else:
                state_type = {  XMI.SIMPLESTATE     : XMISimpleState,
                                XMI.FINALSTATE      : XMIFinalState,
                                XMI.SUBMACHINESTATE : XMISubMachineState,
                                XMI.STUBSTATE       : XMIStubState }[sel.nodeName]
            state = state_type(sel)
            self.addState(state)
        #sel.getAttribute('isConcurrent') == 'true'
        #XMIConcurrentCompositeState

    def buildTransitions(self):
        tels = getElementsByTagName(self.domElement, XMI.TRANSITION,
                                    recursive=1)
        for tel in tels:
            if tel.parentNode.nodeName in ['UML:StateVertex.outgoing', 'UML:StateVertex.incoming']:
                continue
            tran = XMIStateTransition(tel)
            self.addTransition(tran)

    def getInitialState(self):
        states = self.getStates()
        for s in states:
            if s.isInitial():
                return s
        for s in states:
            for k, v in s.getTaggedValues().items():
                # XXX eeek, this is very specific and need to move to generator
                if k == 'initial_state':
                    return s
        return states[0]

    def getAllTransitionActions(self):
        res = []
        for t in self.getTransitions():
            if t.getAction():
                res.append(t.getAction())
        return res

    def getTransitionActionByName(self, name):
        for t in self.getTransitions():
            if t.getAction():
                if t.getAction().getBeforeActionName() == name or \
                   t.getAction().getAfterActionName() == name:
                    return t.getAction()
        return None

    def getAllTransitionActionNames(self, before=True, after=True):
        actionnames = set()
        actions = self.getAllTransitionActions()
        for action in actions:
            if before and action.getBeforeActionName():
                actionnames.add(action.getBeforeActionName())
            if after and action.getAfterActionName():
                actionnames.add(action.getAfterActionName())
        return list(actionnames)

class XMIComment:
    def __init__(self, annotated_element_id, body):
        self.annotated_element_id = annotated_element_id
        self.body = body

class XMITrigger:
    pass

class XMITimeTrigger(XMITrigger):
    def __init__(self, name, expression, id):
        self.name = name
        self.expression = expression
        self.id = id

class XMISignalTrigger(XMITrigger):
    def __init__(self, name, id):
        self.name= name 
        if not re.search('^\s*\w[\w\s]*\s*$', name):
            log.error('Can\'t parse signal trigger \"%s\"'%(name))
        self.id = id

class XMIStateTransition(XMIElement):
    def __init__(self, tel):
        XMIElement.__init__(self, tel)
        source = getElementByTagName(tel, 'UML:Transition.source', recursive=0)
        source = getElementByTagName(source, XMI.STATES, recursive=0)
        self.source_state_id = source.getAttribute('xmi.idref')
        target = getElementByTagName(tel, 'UML:Transition.target', recursive=0)
        target = getElementByTagName(target, XMI.STATES, recursive=0)
        self.target_state_id = target.getAttribute('xmi.idref')
        effectl = getElementsByTagName(tel, 'UML:Transition.effect', recursive=0)
        effect = ''
        if effectl:
            assert(len(effectl) == 1)
            effect = getElementByTagName(effectl[0], 'UML:ActionExpression', recursive=1)
            if effect.getAttribute('language'):
                log.error('Language ignored for transition with xmi-id %s ' % (tel.getAttribute('xmi.id'))) 
            effect = effect.getAttribute('body').replace('&#10;', '\n')
        self.effect = effect
        guardl = getElementsByTagName(tel, 'UML:Guard.expression', recursive=1)
        guard = ''
        if guardl:
            guardl = getElementsByTagName(tel, 'UML:BooleanExpression', recursive=1)
            if guardl:
                assert(len(guardl)==1)
                guard = guardl[0].getAttribute('body')
            else:
                log.error('No BooleanExpression found for transition with xmi-id %s' % (tel.getAttribute('xmi.id')))
        self.guard = guard
        self.trigger_id = None
        triggerl = getElementsByTagName(tel, 'UML:Transition.trigger', recursive=0)
        if triggerl:            
            triggerl = getElementsByTagName(tel, ('UML:SignalEvent', 'UML:TimeEvent'), recursive=1)
            if triggerl:
                assert(len(triggerl) == 1)
                self.trigger_id = triggerl[0].getAttribute('xmi.idref')
            else:                
                log.error('Unknown trigger type for transition with xmi-id %s' % (tel.getAttribute('xmi.id')))

class XMIState(XMIElement):
    def __init__(self, dom):
        self.incomingTransitions = []
        self.outgoingTransitions = []
        assert(dom.parentNode.nodeName in ['UML:CompositeState.subvertex', 'UML:StateMachine.top'])
        self.parent_state_id = dom.parentNode.parentNode.getAttribute('xmi.id')
        
        effectl = getElementsByTagName(dom, 'UML:State.doActivity', recursive=0)
        effect = None
        if effectl:
            assert(len(effectl) == 1)
            effect = getElementByTagName(effectl[0], 'UML:ActionExpression', recursive=1)
            if effect.getAttribute('language'):
                log.error('Language ignored for transition with xmi-id %s ' % (dom.getAttribute('xmi.id'))) 
            effect = effect.getAttribute('body').replace('&#10;', '\n')
        
        self.invariant = effect

        effectl = getElementsByTagName(dom, 'UML:State.entry', recursive=0)
        effect = None
        if effectl:
            assert(len(effectl) == 1)
            effect = getElementByTagName(effectl[0], 'UML:ActionExpression', recursive=1)
            if effect.getAttribute('language'):
                log.error('Language ignored for transition with xmi-id %s ' % (dom.getAttribute('xmi.id'))) 
            effect = effect.getAttribute('body').replace('&#10;', '\n')
        
        self.code = effect
        
        try:
            if dom.parentNode.parentNode.parentNode.parentNode.getAttribute('isConcurrent') == 'true':
                self.name_container_id = dom.parentNode.parentNode.parentNode.parentNode.getAttribute('xmi.id')
            else:
                self.name_container_id = self.parent_state_id    
        except Exception:
            pass        
        
        XMIElement.__init__(self, dom)

class XMICompositeState(XMIState):
    def __init__(self, sel):
        XMIState.__init__(self, sel)
        #self.isconcurrent = sel.getAttribute('isConcurrent') == 'true'
        sels = getElementsByTagName(sel, XMI.STATES, recursive=1)
        self.child_states_id = []
        for sel in sels:
            self.child_states_id.append(sel.getAttribute('xmi.id'))

class XMIConcurrentCompositeState(XMIState):
    def __init__(self, sel):
        XMIState.__init__(self, sel)
        sels = getElementsByTagName(sel, XMI.STATES, recursive=1)
        self.child_states_id = []
        for sel in sels:
            self.child_states_id.append(sel.getAttribute('xmi.id'))
            
class XMIConcurrentRegion(XMICompositeState):
    pass        

class XMISimpleState(XMIState):
    pass
    
class XMIForkState(XMIState):
    pass

class XMIJoinState(XMIState):
	pass

class XMIInitialState(XMIState):
	pass

class XMIFinalState(XMIState):
	pass
	
class XMIStubState(XMIState):
    def __init__(self, sel):
        XMIState.__init__(self, sel)
        parent = sel.parentNode.parentNode
        try:
            subref = getElementByTagName(parent, XMI.SUBMACHINESTATEREF, recursive = 0)
            smref =  getElementByTagName(subref, XMI.STATEMACHINE, recursive = 0)
            self.reference_state_name = sel.getAttribute('referenceState')
        except IndexError:            
            log.error("No reference state is given for stub state \"%s\" (xmi.id = %s, submachine \"%s\")"
                %(sel.getAttribute('name'), sel.getAttribute('xmi.id'), sel.parentNode.parentNode.getAttribute("name")))

class XMISubMachineState(XMIState):
    def __init__(self, sel):
        XMIState.__init__(self, sel)
        try:
            subref = getElementByTagName(sel, XMI.SUBMACHINESTATEREF, recursive = 0)
            smref =  getElementByTagName(subref, XMI.STATEMACHINE, recursive = 0)
            self.reference_statemachine_id = smref.getAttribute('xmi.idref')
        except IndexError:
            log.error("No reference state machine is given for submachine \"%s\" (xmi.id = %s)"%(sel.getAttribute('name'), sel.getAttribute('xmi.id')))

class XMIJunctionState(XMIState):
	pass

class XMIChoiceState(XMIState):
	pass

class XMIShallowHistoryState(XMIState):
	pass

class XMIDeepHistoryState(XMIState):
	pass

def buildHierarchy(doc, packagenames, profile_docs=None):
    """Builds Hierarchy out of the doc."""


def parse(xschemaFileName=None, xschema=None):
    log.info("Parsing...")
    if xschemaFileName:
        suff = os.path.splitext(xschemaFileName)[1].lower()
        if suff in ('.zargo', '.zuml', '.zip'):
            log.debug("Opening %s ..." % suff)
            zf = ZipFile(xschemaFileName)
            xmis = [n for n in zf.namelist() \
                    if os.path.splitext(n)[1].lower() in ('.xmi','.xml')]
            assert(len(xmis)==1)

            # search for profiles includes in *.zargo zipfile
            profile_files = {}
            profiles = [n for n in zf.namelist() if os.path.splitext(n)[1].lower() in ('.profile',)]
            if profiles:
                assert(len(profiles)==1)
                for fn in zargoparser.getProfileFilenames(zf.read(profiles[0])):
                    found = False
                    for profile_directory in profiles_directories:
                        profile_path = os.path.join(profile_directory, fn)
                        if os.path.exists(profile_path):
                            profile_files[fn] = profile_path
                            found = True
                            break
                    if not found:
                        raise IOError("Profile %s not found" % fn)
                log.info("Profile files: '%s'" % str(profile_files))
                for f, content in profile_files.items():
                    profile_docs[f] = minidom.parse(content)

            buf = zf.read(xmis[0])
            doc = minidom.parseString(buf)
        elif suff in ('.xmi', '.xml', '.uml'):
            log.debug("Opening %s ..." % suff)
            doc = minidom.parse(xschemaFileName)
        else:
            raise TypeError('Input file not of the following types: .xmi, .xml, .uml, .zargo, .zuml, .zip')
    else:
        doc = minidom.parseString(xschema)

        
    res = XMIModel(doc)
    res.buildStateMachines()
    log.debug("Created a root XMI parser.")

    return res