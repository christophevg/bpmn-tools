"""
  Classes representing the different parts of a BPMN file.
"""

from .    import xml
from .xml import IdentifiedElement

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

  @property
  def source(self):
    if self._source:
      return self._source
    elif self["sourceRef"]:
      obj = self.root.find("id", self["sourceRef"])
      if obj: return obj
    raise Exception(f"no source found on {self}")

  @property
  def target(self):
    if self._target:
      return self._target
    elif self["targetRef"]:
      obj = self.root.find("id", self["targetRef"])
      if obj: return obj
    raise Exception(f"no target found on {self}")

  def __getitem__(self, name):
    if name == "id":
      return f"flow_{self.source['id']}_{self.target['id']}"
    return super().__getitem__(name)

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    attributes.update({
      "id"       : self["id"],
      "sourceRef": self.source["id"],
      "targetRef": self.target["id"]      
    })
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

class Event(Element):
  __labeled__ = False
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.width  = 36
    self.height = 36

class Start(Event):
  __tag__    = "bpmn:startEvent"

class End(Event):
  __tag__ = "bpmn:endEvent"

class Task(Element):
  __tag__     = "bpmn:task"

  def __init__(self, name="", **kwargs):
    super().__init__(**kwargs)
    self["name"] = name

class UserTask(Task):
  __tag__ = "bpmn:userTask"

class ScriptTask(Task):
  __tag__ = "bpmn:scriptTask"

class ServiceTask(Task):
  __tag__ = "bpmn:serviceTask"

class FlowNodeRef(xml.Element):
  __tag__ = "bpmn:flowNodeRef"

  def __init__(self, ref=None, **kwargs):
    super().__init__(**kwargs)
    self._ref = ref

  @property
  def ref(self):
    if self._ref:
      return self._ref
    return self.root.find("id", super().text)
    
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
  def elements(self):
    # deref references
    return [ ref.ref for ref in self.refs if ref.ref ] # FIXME: ref.ref is None

  def append(self, child):
    if isinstance(child, FlowNodeRef):       # "native" ref
      self.refs.append(child)
    elif isinstance(child, Element):
      self.refs .append(FlowNodeRef(child))  # wrap it
    else:
      super().append(child) # something else
    return self

  @property
  def children(self):
    return super().children + self.refs

class LaneSet(IdentifiedElement):
  __tag__ = "bpmn:laneSet"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.lanes = []
  
  def append(self, child):
    if isinstance(child, Lane):
      self.lanes.append(child)
    else:
      super().append(child)
    return self
  
  def __len__(self):
    return len(self.lanes)

  @property
  def children(self):
    return super().children + self.lanes

class Process(IdentifiedElement):
  __tag__ = "bpmn:process"
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.laneset = LaneSet(id=f"LaneSet_{self['id']}")
    self._elements = []
  
  @property
  def elements(self):
    elems = self._elements  # direct elements
    # add elements that are "hidden" in lanes
    if len(self.laneset) > 0:
      for lane in self.laneset.lanes:
        for element in lane.elements:
          if not element in elems:
            elems.append(element)
    return elems
  
  def append(self, child):
    if isinstance(child, Element):
      self._elements.append(child)
    elif isinstance(child, LaneSet):
      self.laneset = child
    elif isinstance(child, Lane):
      self.laneset.append(child)
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
