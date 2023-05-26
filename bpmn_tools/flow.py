"""
  Classes representing the different parts of a BPMN file.
"""

from . import xml

from .util import prune

class Process(xml.Element):
  __tag__ = "bpmn:process"
  
  def __init__(self, id="process", **kwargs):
    if not "@id" in kwargs:
      kwargs["@id"] = "process"
    super().__init__(**kwargs)

class Flow(xml.Element):
  __tag__ = "bpmn:sequenceFlow"
  __labeled__ = False

  def __init__(self, source=None, target=None):
    self.source = source
    self.target = target
    self.source.outgoing.append(self)
    self.target.incoming.append(self)

  @property
  def id(self):
    return f"flow_{self.source.id}_{self.target.id}"

  def as_dict(self):
    return {
      "@id"       : self.id,
      "@sourceRef": self.source.id,
      "@targetRef": self.target.id
    }

class Incoming(xml.Element):
  __tag__ = "bpmn:incoming"
  
  def __init__(self, flow=None, **kwargs):
    super().__init__(**kwargs)
    self.flow = flow
    if self.flow:
      self.text = self.flow.id

class Outgoing(xml.Element):
  __tag__ = "bpmn:outgoing"

  def __init__(self, flow=None, **kwargs):
    super().__init__(**kwargs)
    self.flow = flow
    if self.flow:
      self.text = self.flow.id

class Element(xml.Element):
  __width__   = 100
  __height__  = 80
  __labeled__ = True

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.incoming = []
    self.outgoing = []
    self.x = 0
    self.y = 0

  @property
  def _more_children(self):
    more = []
    if self.incoming:
      more.extend([ Incoming(flow) for flow in self.incoming ])
    if self.outgoing:
      more.extend([ Outgoing(flow) for flow in self.outgoing ])
    return more

class Event(Element):
  __width__  = 36
  __height__ = 36
  __labeled__ = False

class Start(Event):
  __tag__    = "bpmn:startEvent"

  def __init__(self, id="start", **kwargs):
    if not "@id" in kwargs:
      kwargs["@id"] = id
    super().__init__(**kwargs)

class End(Event):
  __tag__ = "bpmn:endEvent"

  def __init__(self, id="end", **kwargs):
    if not "@id" in kwargs:
      kwargs["@id"] = "end"
    super().__init__(**kwargs)

class Task(Element):
  __tag__     = "bpmn:task"

  def __init__(self, name="", id="task", **kwargs):
    if not "@id" in kwargs:
      kwargs["@id"] = id
    if not "@name" in kwargs:
      kwargs["@name"] = name
    super().__init__(**kwargs)
