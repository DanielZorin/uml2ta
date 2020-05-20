
import pdb
import string
import os.path
import logging
import re
from zipfile import ZipFile
from xml.dom import minidom
from zope.interface import implements
from utils import mapName
from utils import toBoolean
from utils import wrap as doWrap
from interfaces import IPackage
import zargoparser

log = logging.getLogger('XMIparser')

has_stripogram = 1
try:
    from stripogram import html2text
except ImportError:
    has_stripogram = 0
    def html2text(s, *args, **kwargs):
        return s

# Set default wrap width
default_wrap_width = 64

# Tag constants
clean_trans = string.maketrans(':-. /$', '______')


class XMI1_0(object):
    XMI_CONTENT = "XMI.content"
    OWNED_ELEMENT = "Foundation.Core.Namespace.ownedElement"

    # XMI version specific stuff goes there
    STATEMACHINE = 'Behavioral_Elements.State_Machines.StateMachine'
    STATE = 'Behavioral_Elements.State_Machines.State'
    TRANSITION = 'Behavioral_Elements.State_Machines.Transition'
    # each TRANSITION has (in its defn) a TRIGGER which is an EVENT
    EVENT = 'Behavioral_Elements.State_Machines.SignalEvent'
    # and a TARGET (and its SOURCE) which has a STATE
    SOURCE = 'Behavioral_Elements.State_Machines.Transition.source'
    TARGET = 'Behavioral_Elements.State_Machines.Transition.target'
    # ACTIONBODY gives us the rate of the transition
    ACTIONBODY = 'Foundation.Data_Types.Expression.body'

    # STATEs and EVENTs both have NAMEs
    NAME = 'Foundation.Core.ModelElement.name'

    #Collaboration stuff: a
    COLLAB = 'Behavioral_Elements.Collaborations.Collaboration'
    # has some
    CR = 'Behavioral_Elements.Collaborations.ClassifierRole'
    # each of which has a
    BASE = 'Behavioral_Elements.Collaborations.ClassifierRole.base'
    # which we will assume to be a CLASS, collapsing otherwise
    CLASS = 'Foundation.Core.Class'
    PACKAGE = 'Model_Management.Package'
    # To match up a CR with the right start state, we look out for the context
    CONTEXT = 'Behavioral_Elements.State_Machines.StateMachine.context'
    MODEL = 'Model_Management.Model'
    MULTIPLICITY = 'Foundation.Core.StructuralFeature.multiplicity'
    MULT_MIN = 'Foundation.Data_Types.MultiplicityRange.lower'
    MULT_MAX = 'Foundation.Data_Types.MultiplicityRange.upper'
    ATTRIBUTE = 'Foundation.Core.Attribute'
    DATATYPE = 'Foundation.Core.DataType'
    FEATURE = 'Foundation.Core.Classifier.feature'
    TYPE = 'Foundation.Core.StructuralFeature.type'
    ASSOCEND_PARTICIPANT = CLASSIFIER = 'Foundation.Core.Classifier'
    ASSOCIATION = 'Foundation.Core.Association'
    ASSOCIATION_CLASS = 'Foundation.Core.AssociationClass'
    AGGREGATION = 'Foundation.Core.AssociationEnd.aggregation'
    ASSOCEND = 'Foundation.Core.AssociationEnd'
    ASSOCENDTYPE = 'Foundation.Core.AssociationEnd.type'

    METHOD = "Foundation.Core.Operation"
    METHODPARAMETER = "Foundation.Core.Parameter"
    PARAM_DEFAULT = "Foundation.Core.Parameter.defaultValue"
    EXPRESSION = "Foundation.Data_Types.Expression"
    EXPRESSION_BODY = "Foundation.Data_Types.Expression.body"

    GENERALIZATION = "Foundation.Core.Generalization"
    GEN_CHILD = "Foundation.Core.Generalization.child"
    GEN_PARENT = "Foundation.Core.Generalization.parent"
    GEN_ELEMENT = "Foundation.Core.GeneralizableElement"

    TAGGED_VALUE_MODEL = "Foundation.Core.ModelElement.taggedValue"
    TAGGED_VALUE = "Foundation.Extension_Mechanisms.TaggedValue"
    TAGGED_VALUE_TAG = "Foundation.Extension_Mechanisms.TaggedValue.tag"
    TAGGED_VALUE_VALUE = "Foundation.Extension_Mechanisms.TaggedValue.value"

    ATTRIBUTE_INIT_VALUE = "Foundation.Core.Attribute.initialValue"
    STEREOTYPE = "Foundation.Extension_Mechanisms.Stereotype"
    STEREOTYPE_MODELELEMENT = "Foundation.Extension_Mechanisms.Stereotype.extendedElement"
    MODELELEMENT = "Foundation.Core.ModelElement"
    ISABSTRACT = "Foundation.Core.GeneralizableElement.isAbstract"
    INTERFACE = "Foundation.Core.Interface"
    ABSTRACTION = "Foundation.Core.Abstraction"
    DEPENDENCY = "Foundation.Core.Dependency"
    DEP_CLIENT = "Foundation.Core.Dependency.client"
    DEP_SUPPLIER = "Foundation.Core.Dependency.supplier"

    BOOLEAN_EXPRESSION = "Foundation.Data_Types.BooleanExpression"
    #State Machine

    STATEMACHINE = 'Behavioral_Elements.State_Machines.StateMachine'
    STATEMACHINE_CONTEXT = "Behavioral_Elements.State_Machines.StateMachine.context"
    STATEMACHINE_TOP = "Behavioral_Elements.State_Machines.StateMachine.top"
    COMPOSITESTATE = "Behavioral_Elements.State_Machines.CompositeState"
    COMPOSITESTATE_SUBVERTEX = "Behavioral_Elements.State_Machines.CompositeState.subvertex"
    SIMPLESTATE = "Behavioral_Elements.State_Machines.State"
    PSEUDOSTATE = "Behavioral_Elements.State_Machines.Pseudostate"
    PSEUDOSTATE_KIND = "Behavioral_Elements.State_Machines.Pseudostate.kind"
    FINALSTATE = "Behavioral_Elements.State_Machines.Finalstate"
    STATEVERTEX_OUTGOING = "Behavioral_Elements.State_Machines.StateVertex.outgoing"
    STATEVERTEX_INCOMING = "Behavioral_Elements.State_Machines.StateVertex.incoming"
    TRANSITION = "Behavioral_Elements.State_Machines.Transition"
    STATEMACHINE_TRANSITIONS = "Behavioral_Elements.State_Machines.StateMachine.transitions"
    TRANSITON_TARGET = "Behavioral_Elements.State_Machines.Transition.target"
    TRANSITION_SOURCE = "Behavioral_Elements.State_Machines.Transition.source"
    TRANSITION_EFFECT = "Behavioral_Elements.State_Machines.Transition.effect"
    TRANSITION_GUARD = "Behavioral_Elements.State_Machines.Transition.guard"

    ACTION_SCRIPT = "Behavioral_Elements.Common_Behavior.Action.script"
    ACTION_EXPRESSION = "Foundation.Data_Types.ActionExpression"
    ACTION_EXPRESSION_BODY = "Foundation.Data_Types.Expression.body"

    DIAGRAM = "UML:Diagram"
    DIAGRAM_OWNER = "UML:Diagram.owner"
    DIAGRAM_SEMANTICMODEL_BRIDGE = "UML:Uml1SemanticModelBridge"
    DIAGRAM_SEMANTICMODEL_BRIDGE_ELEMENT = "UML:Uml1SemanticModelBridge.element"
    ACTOR = "Behavioral_Elements.Use_Cases.Actor"

    aggregates = ['composite', 'aggregate']

    generate_datatypes=['field','compound_field']

    def __init__(self,**kw):
        self.__dict__.update(kw)

    def getName(self, domElement, doReplace=False):
        return getAttributeValue(domElement, self.NAME)

    def getId(self, domElement):
        return domElement.getAttribute('xmi.id').strip()

    def getIdRef(self, domElement):
        return domElement.getAttribute('xmi.idref').strip()

    def getHrefId(self, domElement):
        href = domElement.getAttribute('href').strip()
        splitted = href.rsplit('/', 1)
        if not len(splitted) == 2:
            return ''
        return splitted[1]
    
    def getIdRefOrHrefId(self, domElement):
        return self.getIdRef(domElement) or self.getHrefId(domElement)

    def getAssocEndParticipantId(self, el):
        assocend = getElementByTagName(el, self.ASSOCEND_PARTICIPANT, None)

        if not assocend:
            assocend = getElementByTagName(el, self.ASSOCENDTYPE, None)

        if not assocend:
            return None

        classifier = getSubElement(assocend)

        if not classifier:
            log.warn("No assocEnd participant found  for '%s'.",
                     XMI.getId(el))
            return None

        return classifier.getAttribute('xmi.idref')

    def isAssocEndAggregation(self, el):
        aggs = el.getElementsByTagName(XMI.AGGREGATION)
        # Sig: AFAIK non-folderish items can't be turned into folderish items at run time (e.g. via an adapter)
        # therefore, if an assocEnd ends at a flavor, it should never be considered as an aggregation end
        # unless we know how to let ContentFlavor folderize that item
        isFlavorEnd = False
        if hasattr(el,"hasStereotype"):
            isFlavorEnd = el.hasStereotype('flavor')
        return aggs \
               and aggs[0].getAttribute('xmi.value') in self.aggregates \
               and not isFlavorEnd

    def getAssocEndAggregation(self, el):
        aggs = el.getElementsByTagName(XMI.AGGREGATION)
        if not aggs:
            return None
        return aggs[0].getAttribute('xmi.value')

    def getMultiplicity(self, el, multmin=0, multmax=-1):
        mult_min = int(getAttributeValue(el, self.MULT_MIN, default=multmin,
                                         recursive=1))
        mult_max = int(getAttributeValue(el, self.MULT_MAX, default=multmax,
                                         recursive=1))
        return (mult_min, mult_max)

    def buildRelations(self, doc, objects):
        #XXX: needs refactoring
        rels = doc.getElementsByTagName(XMI.ASSOCIATION) + \
               doc.getElementsByTagName(XMI.ASSOCIATION_CLASS)
        for rel in rels:
            master = None
            detail = None
            ends = rel.getElementsByTagName(XMI.ASSOCEND)

            if len(ends) != 2:
                log.debug('association with != 2 ends found.')
                continue
            # will it be a plain Association or an AssociationClass?
            if rel.nodeName == XMI.ASSOCIATION_CLASS:
                associationXMIClass = XMIAssociationClass
            else:
                associationXMIClass = XMIAssociation

            if self.isAssocEndAggregation(ends[0]):
                master = ends[0]
                detail = ends[1]
            if self.isAssocEndAggregation(ends[1]):
                master = ends[1]
                detail = ends[0]

            if master:
                log.debug("Ok, weve found an aggregation.")
                log.debug("It's an %s", associationXMIClass)
                masterid = self.getAssocEndParticipantId(master)
                detailid = self.getAssocEndParticipantId(detail)

                log.debug("Master '%s', detail '%s'.", master, detail)
                m = objects.get(masterid, None)
                d = objects.get(detailid, None)
                log.debug("In other words: Master id = '%s', Master name = '%s'.", XMI.getId(master), m.getName())

                if not m:
                    log.warn("Master Object not found for aggregation "
                             "relation id='%s'.", XMI.getId(master))
                    continue

                if not d:
                    log.warn("Child Object not found for aggregation "
                             "relation: parent='%s'.", m.getName())
                    continue

                try:
                    m.addSubType(d)
                except KeyError:
                    log.warn("Child Object not found for aggregation "
                             "relation: Child=%s(%s), parent=%s.",
                             d.getId(), d.getName(), XMI.getName(m))
                    continue

                # check whether this association already exists or we have to instantiate it
                relid = self.getId(rel)
                if allObjects.has_key(relid):
                    assoc = allObjects[relid]
                else:
                    assoc = associationXMIClass(rel)
                assoc.fromEnd.obj.addAssocFrom(assoc)
                assoc.toEnd.obj.addAssocTo(assoc)

            else:
                log.debug("It's an assoc, lets model it as association or an association class.")
                try:
                    #check if an association class already exists
                    relid = self.getId(rel)
                    if allObjects.has_key(relid):
                        assoc = allObjects[relid]
                        assoc.calcEnds()
                    else:
                        assoc = associationXMIClass(rel)
                except KeyError:
                    log.warn("Child Object not found for aggregation "
                             "'%s', parent='%s'.",
                             XMI.getId(rel), XMI.getName(master))
                    continue

                if getattr(assoc.fromEnd, 'obj', None) and \
                   getattr(assoc.toEnd, 'obj', None):
                    assoc.fromEnd.obj.addAssocFrom(assoc)
                    assoc.toEnd.obj.addAssocTo(assoc)
                else:
                    log.warn("Association has no ends: '%s'.",
                             assoc.getId())

    def buildGeneralizations(self, doc, objects):
        gens = doc.getElementsByTagName(XMI.GENERALIZATION)

        for gen in gens:
            if not self.getId(gen):continue
            try:
                par0 = getElementByTagName(gen, self.GEN_PARENT, recursive=1)
                child0 = getElementByTagName(gen, self.GEN_CHILD, recursive=1)
                try:
                    par = objects[getSubElement(par0).getAttribute('xmi.idref')]
                except KeyError:
                    log.warn("Parent Object not found for generalization "
                             "relation '%s', parent=%s'.",
                             XMI.getId(gen), XMI.getName(par0))
                    continue

                child = objects[getSubElement(child0).getAttribute('xmi.idref')]

                par.addGenChild(child)
                child.addGenParent(par)
            except IndexError:
                log.error("Gen: index error for generalization '%s'.",
                          self.getId(gen))
                raise

    def buildRealizations(self, doc, objects):
        abs = doc.getElementsByTagName(XMI.ABSTRACTION)

        for ab in abs:
            if not self.getId(ab):continue
            abstraction = XMIAbstraction(ab)
            if not abstraction.hasStereoType('realize') and \
               not abstraction.hasStereoType('adapts'):
                log.debug("Skipping dep: %s", abstraction.getStereoType())
                continue
            try:
                try:
                    par0 = getElementByTagName(ab, self.DEP_SUPPLIER,
                                               recursive=1)
                    sub = getSubElement(par0, ignoremult=1)
                    par = objects[sub.getAttribute('xmi.idref')]
                except (KeyError, IndexError):
                    log.warn("Parent Object not found for realization or adaptation "
                             "relation:%s, parent %s.",
                             XMI.getId(ab), XMI.getName(par0))
                    continue

                try:
                    child0 = getElementByTagName(ab, self.DEP_CLIENT,
                                                 recursive=1)
                    sub = getSubElement(child0, ignoremult=1)
                    child_xmid = sub.getAttribute('xmi.idref')
                    child = objects[child_xmid]
                except (KeyError, IndexError):
                    log.warn("Child element for realization or adaptation relation not found. "
                             "Parent name = '%s' relation xmi_id = '%s'.",
                             par.getName(), XMI.getId(ab))

                if abstraction.hasStereoType('realize'):
                    par.addRealizationChild(child)
                    child.addRealizationParent(par)
                if abstraction.hasStereoType('adapts'):
                    par.addAdaptationChild(child)
                    child.addAdaptationParent(par)
            except IndexError:
                log.error("ab: index error for dependencies; %s",
                          self.getId(ab))
                raise

    def buildDependencies(self, doc, objects):
        deps = doc.getElementsByTagName(XMI.DEPENDENCY)
        for dep in deps:
            if not self.getId(dep):continue
            try:
                depencency = XMIDependency(dep, allObjects=objects)
            except KeyError:
                log.warn('couldnt resolve dependency relation %s',
                         dep.getAttribute('xmi.id'))

    def getExpressionBody(self, element, tagname = None):
        if not tagname:
            tagname = XMI.EXPRESSION
        exp = getElementByTagName(element, XMI.EXPRESSION_BODY,
                                  recursive=1, default=None)
        if exp and exp.firstChild:
            return exp.firstChild.nodeValue
        else:
            return None

    def getTaggedValue(self, el, doReplace=False):
        log.debug("Getting tagged value for element '%s'. Not recursive.",
                  self.getId(el))
        tagname = getAttributeValue(el, XMI.TAGGED_VALUE_TAG,
                                              recursive=0, default=None)                           
        if not tagname:
            raise TypeError, 'element %s has empty taggedValue' % self.getId(el)
        tagvalue = getAttributeValue(el, XMI.TAGGED_VALUE_VALUE,
                                               recursive=0, default=None)                            
        return tagname, tagvalue

    def collectTagDefinitions(self, el):
        """Dummy function, only needed in xmi >=1.1"""
        pass

    def calculateStereoType(self, o):
        #in xmi its weird, because all objects to which a
        #stereotype applies are stored in the stereotype
        #while in xmi 1.2 its opposite
        for k in stereotypes.keys():
            st = stereotypes[k]
            els = st.getElementsByTagName(self.MODELELEMENT)
            for el in els:
                if el.getAttribute('xmi.idref') == o.getId():
                    name = self.getName(st)
                    log.debug("Stereotype found: %s.",
                              name)
                    o.setStereoType(name)

    def calcClassAbstract(self, o):
        abs = getElementByTagName(o.domElement, XMI.ISABSTRACT, None)
        if abs:
            o.isabstract = abs.getAttribute('xmi.value') == 'true'
        else:
            o.isabstract = 0

    def calcVisibility(self, o):
        # visibility detection unimplemented for XMI 1.0
        o.visibility = None

    def calcOwnerScope(self, o):
        # ownerScope detection unimplemented for XMI 1.0
        o.ownerScope = None

    def calcDatatype(self, att):
        global datatypes
        typeinfos = att.domElement.getElementsByTagName(XMI.TYPE)
        if len(typeinfos):
            classifiers = typeinfos[0].getElementsByTagName(XMI.CLASSIFIER)
            if len(classifiers):
                typeid = str(self.getIdRefOrHrefId(classifiers[0]))
                typeElement = datatypes[typeid]
                att.type = XMI.getName(typeElement)
                # Collects all datatype names (to prevent pure datatype
                # classes from being generated)
                if att.type not in datatypenames:
                    datatypenames.append(att.type)

    def getPackageElements(self, el):
        """Gets all package nodes below the current node (only one level)."""
        res = []
        #in case the el is a document we have to crawl down until we have ownedElements
        ownedElements = getElementByTagName(el, self.OWNED_ELEMENT, default=None)
        if not ownedElements:
            if el.tagName == self.PACKAGE:
                return []
            el = getElementByTagName(el, self.MODEL, recursive=1)
        ownedElements = getElementByTagName(el, self.OWNED_ELEMENT)
        res = getElementsByTagName(ownedElements, self.PACKAGE)
        return res

    def getOwnedElement(self, el):
        return getElementByTagName(el, self.OWNED_ELEMENT, default=None)

    def getContent(self, doc):
        content = getElementByTagName(doc, XMI.XMI_CONTENT, recursive=1)
        return content

    def getModel(self, doc):
        content = self.getContent(doc)
        model = getElementByTagName(content, XMI.MODEL, recursive=0)
        return model

    def getGenerator(self):
        return getattr(self, 'generator', None)

    def getGenerationOption(self, opt):
        return getattr(self.getGenerator(), opt, None)


class XMI1_1 (XMI1_0):
    # XMI version specific stuff goes there

    tagDefinitions = None

    NAME = 'UML:ModelElement.name'
    OWNED_ELEMENT = "UML:Namespace.ownedElement"

    MODEL = 'UML:Model'

    # Collaboration
    COLLAB = 'Behavioral_Elements.Collaborations.Collaboration'
    CLASS = 'UML:Class'
    PACKAGE = 'UML:Package'

    # To match up a CR with the right start state, we look out for the context
    MULTIPLICITY = 'UML:StructuralFeature.multiplicity'
    ATTRIBUTE = 'UML:Attribute'
    DATATYPE = 'UML:DataType'
    FEATURE = 'UML:Classifier.feature'
    TYPE = 'UML:StructuralFeature.type'
    CLASSIFIER = 'UML:Classifier'
    ASSOCIATION = 'UML:Association'
    AGGREGATION = 'UML:AssociationEnd.aggregation'
    ASSOCEND = 'UML:AssociationEnd'
    ASSOCENDTYPE = 'UML:AssociationEnd.type'
    ASSOCEND_PARTICIPANT = 'UML:AssociationEnd.participant'
    METHOD = "UML:Operation"
    METHODPARAMETER = "UML:Parameter"
    MULTRANGE = 'UML:MultiplicityRange'

    MULT_MIN = 'UML:MultiplicityRange.lower'
    MULT_MAX = 'UML:MultiplicityRange.upper'

    GENERALIZATION = "UML:Generalization"
    GEN_CHILD = "UML:Generalization.child"
    GEN_PARENT = "UML:Generalization.parent"
    GEN_ELEMENT = "UML:Class"

    ATTRIBUTE_INIT_VALUE = "UML:Attribute.initialValue"
    EXPRESSION = ["UML:Expression","UML2:OpaqueExpression"]
    PARAM_DEFAULT = "UML:Parameter.defaultValue"

    TAG_DEFINITION = "UML:TagDefinition"

    TAGGED_VALUE_MODEL = "UML:ModelElement.taggedValue"
    TAGGED_VALUE = "UML:TaggedValue"
    TAGGED_VALUE_TAG = "UML:TaggedValue.tag"
    TAGGED_VALUE_VALUE = "UML:TaggedValue.value"

    MODELELEMENT = "UML:ModelElement"
    STEREOTYPE_MODELELEMENT = "UML:ModelElement.stereotype"

    STEREOTYPE = "UML:Stereotype"
    ISABSTRACT = "UML:GeneralizableElement.isAbstract"
    INTERFACE = "UML:Interface"

    ABSTRACTION = "UML:Abstraction"

    DEPENDENCY = "UML:Dependency"
    DEP_CLIENT = "UML:Dependency.client"
    DEP_SUPPLIER = "UML:Dependency.supplier"

    ASSOCIATION_CLASS = 'UML:AssociationClass'
    BOOLEAN_EXPRESSION = ["UML:BooleanExpression","UML2:OpaqueExpression"]

    #State Machine

    STATEMACHINE = "UML:StateMachine"
    STATEMACHINE_CONTEXT = "UML:StateMachine.context"
    STATEMACHINE_TOP = "UML:StateMachine.top"
    COMPOSITESTATE = "UML:CompositeState"    
    COMPOSITESTATE_SUBVERTEX = "UML:CompositeState.subvertex"
    SIMPLESTATE = "UML:SimpleState"
    PSEUDOSTATE = "UML:Pseudostate"
    PSEUDOSTATE_KIND = "kind"
    FINALSTATE = "UML:FinalState"
    STUBSTATE = "UML:StubState"
    SUBMACHINESTATE = "UML:SubmachineState"
    SUBMACHINESTATEREF = "UML:SubmachineState.submachine"
    STATEVERTEX_OUTGOING = "UML:StateVertex.outgoing"
    STATEVERTEX_INCOMING = "UML:StateVertex.incoming"
    TRANSITION = "UML:Transition","UML2:Transition"
    STATEMACHINE_TRANSITIONS = "UML:StateMachine.transitions"
    TRANSITON_TARGET = "UML:Transition.target"
    TRANSITION_SOURCE = "UML:Transition.source"
    TRANSITION_EFFECT = "UML:Transition.effect"
    TRANSITION_GUARD = "UML:Transition.guard"
    OWNED_BEHAVIOR = "UML2:BehavioredClassifier.ownedBehavior"

    STATES = [COMPOSITESTATE, SIMPLESTATE, PSEUDOSTATE, FINALSTATE, STUBSTATE, SUBMACHINESTATE]

    ACTION_SCRIPT = "UML:Action.script"
    ACTION_EXPRESSION = "UML:ActionExpression"
    ACTION_EXPRESSION_BODY = "UML:ActionExpression.body"
    DIAGRAM = "UML:Diagram"
    DIAGRAM_OWNER = "UML:Diagram.owner"
    DIAGRAM_SEMANTICMODEL_BRIDGE = "UML:Uml1SemanticModelBridge"
    DIAGRAM_SEMANTICMODEL_BRIDGE_ELEMENT = "UML:Uml1SemanticModelBridge.element"
    ACTOR = "UML:Actor"

    UML2TYPE = 'UML2:TypedElement.type'

    def getName(self, domElement, doReplace=False):
        name = ''
        if domElement:
            name = domElement.getAttribute('name')
        return name

    def getExpressionBody(self, element, tagname=None):
        if not tagname:
            tagname = XMI.EXPRESSION
        exp = getElementByTagName(element, tagname, recursive=1, default=None)
        if exp:
            return exp.getAttribute('body')
        else:
            return None


class XMI1_2 (XMI1_1):
    TAGGED_VALUE_VALUE = "UML:TaggedValue.dataValue"
    # XMI version specific stuff goes there

    def isAssocEndAggregation(self, el):
        # Sig: AFAIK non-folderish items can't be turned into folderish items at run time (e.g. via an adapter)
        # therefore, if an assocEnd ends at a flavor, it should never be considered as an aggregation end
        # unless we know how to let ContentFlavor folderize that item
        isFlavorEnd = False
        if hasattr(el,"hasStereotype"):
            isFlavorEnd = el.hasStereotype('flavor')
        return str(el.getAttribute('aggregation')) in self.aggregates \
               and not isFlavorEnd

    def getAssocEndAggregation(self, el):
        return str(el.getAttribute('aggregation'))

    def getMultiplicity(self, el, multmin=0,multmax=-1):
        min = getElementByTagName(el, self.MULTRANGE, default=None, recursive=1)
        max = getElementByTagName(el, self.MULTRANGE, default=None, recursive=1)
        if min:
            mult_min = int(min.getAttribute('lower'))
        else:
            mult_min = multmin
        if max:
            mult_max = int(max.getAttribute('upper'))
        else:
            mult_max = multmax
        return (mult_min, mult_max)

    def getTaggedValue(self, el):
        log.debug("Getting tagname/tagvalue pair from tag. "
                  "Looking recursively for that taggedvalue.")
        tdef = getElementByTagName(el, self.TAG_DEFINITION, default=None,
                                   recursive=1)
        if tdef is None:
            # Fix for http://plone.org/products/archgenxml/issues/62
            return None, None 
        # Fetch the name from the global tagDefinitions (weird)
        id = self.getIdRefOrHrefId(tdef)
        tagname = self.tagDefinitions[id].getAttribute('name')
        tagvalue = getAttributeValue(el, self.TAGGED_VALUE_VALUE,
                                               default=None)
        return tagname, tagvalue

    def collectTagDefinitions(self, el, prefix=''):
        tagdefs = el.getElementsByTagName(self.TAG_DEFINITION)
        if self.tagDefinitions is None:
            self.tagDefinitions = {}
        for t in tagdefs:
            if t.hasAttribute('name'):
                self.tagDefinitions[prefix + t.getAttribute('xmi.id')] = t

    def calculateStereoType(self, o):
        # In xmi its weird, because all objects to which a stereotype
        # applies are stored in the stereotype while in xmi 1.2 its opposite

        sts = getElementsByTagName(o.domElement, self.STEREOTYPE_MODELELEMENT,
                                   recursive=0)
        for st in sts:
            strefs = getSubElements(st)
            for stref in strefs:
                id = self.getIdRefOrHrefId(stref)
                if id:
                    st = stereotypes[id]
                    o.addStereoType(self.getName(st).strip())
                    log.debug("Stereotype found: id='%s', name='%s'.",
                              id, self.getName(st))
                else:
                    log.warn("Empty stereotype id='%s' for class '%s'",
                             o.getId(), o.getName())

    def calcClassAbstract(self, o):
        o.isabstract = o.domElement.hasAttribute('isAbstract') and \
                       o.domElement.getAttribute('isAbstract') == 'true'

    def calcVisibility(self, o):
        o.visibility = o.domElement.hasAttribute('visibility') and \
                       o.domElement.getAttribute('visibility')

    def calcOwnerScope(self, o):
        o.ownerScope = o.domElement.hasAttribute('ownerScope') and \
                       o.domElement.getAttribute('ownerScope')

    def calcDatatype(self, att):
        global datatypes
        typeinfos = att.domElement.getElementsByTagName(XMI.TYPE) + \
                    att.domElement.getElementsByTagName(XMI.UML2TYPE)
        if len(typeinfos):
            classifiers = [cn for cn in typeinfos[0].childNodes
                           if cn.nodeType == cn.ELEMENT_NODE]
            if len(classifiers):
                typeid = self.getIdRefOrHrefId(classifiers[0])
                try:
                    typeElement = datatypes[typeid]
                except KeyError:
                    raise ValueError, 'datatype %s not defined' % typeid
                att.type = XMI.getName(typeElement)
                # Collect all datatype names (to prevent pure datatype
                # classes from being generated)
                if att.type not in datatypenames:
                    datatypenames.append(att.type)


class NoObject(object):
    pass


_marker = NoObject()
allObjects = {}

def getSubElements(domElement):
    return [e for e in domElement.childNodes if e.nodeType == e.ELEMENT_NODE]

def getSubElement(domElement, default=_marker, ignoremult=0):
    els = getSubElements(domElement)
    if len(els) > 1 and not ignoremult:
        raise TypeError, 'more than 1 element found'
    try:
        return els[0]
    except IndexError:
        if default == _marker:
            raise
        else:
            return default

def getAttributeValue(domElement, tagName=None, default=_marker, recursive=0, doReplace=False):
    el = domElement
    #el.normalize()
    if tagName:
        try:
            el = getElementByTagName(domElement, tagName, recursive=recursive)
        except IndexError:
            if default == _marker:
                raise
            else:
                return default
    if el.hasAttribute('xmi.value'):
        return el.getAttribute('xmi.value')
    if not el.firstChild and default != _marker:
        return default
    return el.firstChild.nodeValue

def getAttributeOrElement(domElement, name, default=_marker, recursive=0):
    """Tries to get the value from an attribute, if not found, it tries
    to get it from a subelement that has the name {element.name}.{name}.
    """
    val = domElement.getAttribute(name)
    if not val:
        val = getAttributeValue(domElement, domElement.tagName+'.'+name,
                                default, recursive)
    return val

def getElementsByTagName(domElement, tagName, recursive=0):
    """Returns elements by tag name.

    The only difference from the original getElementsByTagName is
    the optional recursive parameter.
    """
    if isinstance(tagName, basestring):
        tagNames = [tagName]
    else:
        tagNames = tagName
    if recursive:
        els = []
        for tag in tagNames:
            els.extend(domElement.getElementsByTagName(tag))
    else:
        els = [el for el in domElement.childNodes
               if str(getattr(el, 'tagName', None)) in tagNames]
    return els

def getElementByTagName(domElement, tagName, default=_marker, recursive=0):
    """Returns a single element by name and throws an error if more
    than one exists.
    """
    els = getElementsByTagName(domElement, tagName, recursive=recursive)
    if len(els) > 1:
        raise TypeError, 'more than 1 element found'
    try:
        return els[0]
    except IndexError:
        if default == _marker:
            raise
        else:
            return default

def hasClassFeatures(domClass):
    return len(domClass.getElementsByTagName(XMI.FEATURE)) or \
                len(domClass.getElementsByTagName(XMI.ATTRIBUTE)) or \
                len(domClass.getElementsByTagName(XMI.METHOD))
                
XMI = XMI1_2()