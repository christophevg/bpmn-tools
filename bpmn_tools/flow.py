"""
  Classes representing the different parts of a BPMN file.
"""

import logging

from enum import Enum 

from .    import xml
from .xml import IdentifiedElement

logger = logging.getLogger(__name__)

class Flow(IdentifiedElement):
  __tag__ = "bpmn:sequenceFlow"
  __labeled__ = False

  def __init__(self, source=None, target=None):
    super().__init__()
    self._source = source
    self._target = target
    if self._source:
      self._source.outgoing.append(Outgoing(self))
    if self._target:
      self._target.incoming.append(Incoming(self))
    self._resolving_source = False
    self._resolving_target = False

  @property
  def source(self):
    if self._source:
      return self._source
    elif self["sourceRef"]:
      if not self._resolving_source:
        self._resolving_source = True
        obj = self.root.find("id", self["sourceRef"])
        if obj:
          self._resolving_source = False
          return obj
      logger.warning(f"sourceRef {self['sourceRef']} not found.")
    else:
      logger.warning("no source available.")
    return None

  @property
  def target(self):
    if self._target:
      return self._target
    elif self["targetRef"]:
      if not self._resolving_target:
        self._resolving_target = True
        obj = self.root.find("id", self["targetRef"])
        if obj:
          self._resolving_target = False
          return obj
        logger.warning(f"targetRef {self['targetRef']} not found.")
    else:
      logger.warning("no target available.")
    return None

  def _get_flow_ids(self, default=None):
    try:
      source_id = self.source["id"]
    except Exception:
      source_id = default
    try:
      target_id = self.target["id"]
    except Exception:
      target_id = default
    return (source_id, target_id)

  def __getitem__(self, name):
    if name == "id":
      source_id, target_id = self._get_flow_ids(default="unknown")
      return f"flow_{source_id}_{target_id}"
    return super().__getitem__(name)

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    attributes["id"] = self["id"]
    source_id, target_id = self._get_flow_ids()
    if source_id:
      attributes["sourceRef"] = source_id
    if target_id:
      attributes["targetRef"] = target_id
    return attributes

class MessageFlow(Flow):
  __tag__ = "bpmn:messageFlow"

class Incoming(xml.Element):
  __tag__ = "bpmn:incoming"
  
  def __init__(self, flow=None):
    super().__init__()
    self.flow = flow
    if self.flow:
      self.text = self.flow["id"]

class Outgoing(xml.Element):
  __tag__ = "bpmn:outgoing"

  def __init__(self, flow=None):
    super().__init__()
    self.flow = flow
    if self.flow:
      self.text = self.flow["id"]

  @property
  def target(self):
    return self.flow.target

class Element(IdentifiedElement):
  __labeled__ = True

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.incoming = []
    self.outgoing = []
    self.x      = 0
    self.y      = 0
    self.width  = 100
    self.height = 80

  @property
  def process(self):
    if isinstance(self._parent, Process):
      return self._parent
    if isinstance(self._parent, FlowNodeRef):
      # process -> (laneset) -> lane -> FlowNodeRef -> self
      return self._parent._parent._parent
    raise Exception("this should not happen ;-)")

  @property
  def lane(self):
    for lane in self.process.laneset.lanes:
      for ref in lane.refs:
        if ref.ref == self:
          return lane
    return None

  def append(self, child):
    if type(child) == Incoming:
      self.incoming.append(child)
    elif type(child) == Outgoing:
      self.outgoing.append(child)
    else:
      raise ValueError("Element expects only incoming or outgoing flows")
    child._parent = self
    return self

  @property
  def children(self):
    children = []
    if self.incoming:
      children.extend([ flow for flow in self.incoming ])
    if self.outgoing:
      children.extend([ flow for flow in self.outgoing ])
    return children

class MessageEventDefinition(IdentifiedElement):
  __tag__ = "bpmn:messageEventDefinition"

class TimerEventDefinition(IdentifiedElement):
  __tag__ = "bpmn:timerEventDefinition"

class SignalEventDefinition(IdentifiedElement):
  __tag__ = "bpmn:signalEventDefinition"

class EventDefinitions(Enum):
  MESSAGE = MessageEventDefinition
  TIMER   = TimerEventDefinition
  SIGNAL  = SignalEventDefinition

class Event(Element):
  __labeled__ = False

  def __init__(self, name=None, definition=None, **kwargs):
    super().__init__(**kwargs)
    self.width   = 36
    self.height  = 36
    if name:
      self["name"] = name
    self.definition = definition

  def append(self, child):
    try:
      self.definition = EventDefinitions(child.__class__)
    except Exception:
      super().append(child) # something else
    return self

  @property
  def children(self):
    children = super().children
    if self.definition:
      cls = self.definition.value
      children.append(cls(id=f"{cls.__name__}_{self['id']}"))
    return children

class Start(Event):
  __tag__    = "bpmn:startEvent"

class IntermediateThrow(Event):
  __tag__ = "bpmn:intermediateThrowEvent"

class IntermediateCatch(Event):
  __tag__ = "bpmn:intermediateCatchEvent"

class End(Event):
  __tag__ = "bpmn:endEvent"

# Tasks

class Task(Element):
  __tag__     = "bpmn:task"

  def __init__(self, name="", **kwargs):
    super().__init__(**kwargs)
    self["name"] = name

class UserTask(Task):
  __tag__ = "bpmn:userTask"

class ServiceTask(Task):
  __tag__ = "bpmn:serviceTask"

class SendTask(Task):
  __tag__ = "bpmn:sendTask"

class ReceiveTask(Task):
  __tag__ = "bpmn:receiveTask"

class ManualTask(Task):
  __tag__ = "bpmn:manualTask"

class BusinessRuleTask(Task):
  __tag__ = "bpmn:businessRuleTask"

class ScriptTask(Task):
  __tag__ = "bpmn:scriptTask"


class FlowNodeRef(xml.Element):
  __tag__ = "bpmn:flowNodeRef"

  def __init__(self, ref=None, **kwargs):
    super().__init__(**kwargs)
    self._ref = ref

  @property
  def process(self):
    return self._parent.process

  @property
  def ref(self):
    if self._ref:
      return self._ref
    try:
      return self.process.element(super().text)
    except TypeError:
      pass
    return None
    
  @xml.Element.text.getter
  def text(self):
    # if we have referenced object (possibly resolved from #text)
    if self.ref:
      ref = self.ref.id
    else:
      ref = super().text    # else we should have a textual
    return ref

class Lane(IdentifiedElement):
  __tag__ = "bpmn:lane"
  __horizontal__ = True

  def __init__(self, name=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if name:
      self["name"] = name
    self.refs    = []
    self.x      = 30
    self.y      = 0
    self.height = 125
    self.width  = 570

  @property
  def process(self):
    return self._parent.process

  @property
  def elements(self):
    # deref references
    return [ ref.ref for ref in self.refs if ref.ref ] # FIXME: ref.ref is None

  def append(self, child):
    if isinstance(child, FlowNodeRef):       # "native" ref
      self.refs.append(child)
      child._parent = self
    elif isinstance(child, Element):
      wrapped = FlowNodeRef(child)
      child._parent = wrapped
      wrapped._parent = self
      self.refs.append(wrapped)  # wrap it
    else:
      super().append(child) # something else
    return self

  @property
  def children(self):
    return super().children + self.refs

  def has_child(self, child):
    for ref in self.refs:
      if ref.ref == child:
        return True
    return False

class LaneSet(IdentifiedElement):
  __tag__ = "bpmn:laneSet"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.lanes = []
  
  @property
  def process(self):
    return self._parent
  
  def append(self, child):
    if isinstance(child, Lane):
      self.lanes.append(child)
      child._parent = self
    else:
      super().append(child)
    return self
  
  def __len__(self):
    return len(self.lanes)

  @property
  def children(self):
    return super().children + self.lanes

  def lane_of(self, child):
    for lane in self.lanes:
      if lane.has_child(child):
        return lane
    return None

class Process(IdentifiedElement):
  __tag__ = "bpmn:process"
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.laneset = LaneSet(id=f"LaneSet_{self['id']}")
    self._elements = []
  
  def element(self, id):
    for element in self._elements:
      if element["id"] == id:
        return element
    return None
  
  @property
  def participant(self):
    for collaboration in self._parent.collaborations:
      participant = collaboration.find("processRef", self.id)
      if participant:
        return participant
    return None
  
  @property
  def elements(self):
    elems = self._elements  # direct elements
    # add elements that are "hidden" in lanes
    if len(self.laneset) > 0:
      for lane in self.laneset.lanes:
        for element in lane.elements:
          if element not in elems:
            elems.append(element)
    return elems
  
  def append(self, child):
    if isinstance(child, Element):
      self._elements.append(child)
      child._parent = self
    elif isinstance(child, LaneSet):
      self.laneset = child
      child._parent = self
    elif isinstance(child, Lane):
      self.laneset.append(child)
      child._parent = self
    else:
      super().append(child) # generic child handling
    return self

  @property
  def children(self):
    children = super().children.copy()
    children.extend(self.elements)
    if len(self.laneset) > 0:
      children.append(self.laneset)
    return children
