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
    self.source = source
    self.target = target
    self.source.outgoing.append(self)
    self.target.incoming.append(self)

  def __getitem__(self, name):
    if name == "id":
      return f"flow_{self.source['id']}_{self.target['id']}"
    return super()[name]

  @property
  def attributes(self):
    attributes = super().attributes
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
  __width__   = 100
  __height__  = 80
  __labeled__ = True

  def __init__(self, id=None):
    super().__init__()
    if id is None:
      id = self.__class__.__name__.lower()
    self["id"] = id
    self.incoming = []
    self.outgoing = []
    self.x = 0
    self.y = 0

  @property
  def children(self):
    children = []
    if self.incoming:
      children.extend([ Incoming(flow) for flow in self.incoming ])
    if self.outgoing:
      children.extend([ Outgoing(flow) for flow in self.outgoing ])
    return children

class Event(Element):
  __width__  = 36
  __height__ = 36
  __labeled__ = False

class Start(Event):
  __tag__    = "bpmn:startEvent"

class End(Event):
  __tag__ = "bpmn:endEvent"

class Task(Element):
  __tag__     = "bpmn:task"

  def __init__(self, name="", **kwargs):
    super().__init__(**kwargs)
    self["name"] = name
