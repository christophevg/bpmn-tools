"""
  Classes representing the different parts of a BPMN file.
"""

from . import xml

from .util import prune

class Process(xml.Element):
  __tag__ = "bpmn:process"
  
  def __init__(self, id="process"):
    super().__init__()
    self["id"] = id

class Flow(xml.Element):
  __tag__ = "bpmn:sequenceFlow"
  __labeled__ = False

  def __init__(self, source=None, target=None):
    super().__init__()
    self._source = source
    self._target = target
    if self._source:
      self._source.outgoing.append(self)
    if self._target:
      self._target.incoming.append(self)

  @property
  def source(self):
    if self._source:
      return self._source
    elif self["sourceRef"]:
      return self.root.find("id", self["sourceRef"])
    raise Exception(f"no source found on {self}")

  @property
  def target(self):
    if self._target:
      return self._target
    elif self["targetRef"]:
      return self.root.find("id", self["targetRef"])
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

class Element(xml.Element):
  __labeled__ = True

  def __init__(self, id=None):
    super().__init__()
    if id is None:
      id = self.__class__.__name__.lower()
    self["id"] = id
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
      children.extend([ Incoming(flow) for flow in self.incoming ])
    if self.outgoing:
      children.extend([ Outgoing(flow) for flow in self.outgoing ])
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
