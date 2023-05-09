"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

class Process():
  __tag__ = "process"

  def __init__(self, id="process"):
    self.id = id
    self._elements = {}

  @property
  def elements(self):
    l = []
    for es in self._elements.values():
      l +=  es
    return list(filter(lambda e: isinstance(e, Element), l )) 

  @property
  def flows(self):
    l = []
    for es in self._elements.values():
      l +=  es
    return list(filter(lambda e: isinstance(e, Flow), l))
  
  def append(self, element):
    try:
      self._elements[element.__tag__].append(element)
    except KeyError:
      self._elements[element.__tag__] = [ element ]
    return self

  def extend(self, elements):
    for element in elements:
      self.append(element)
    return self

  def as_dict(self):
    # compile elements
    base = {
      f"bpmn:{name}" : prune([
        element.as_dict() for element in elements
      ]) for name, elements in self._elements.items()
    }
    # add properties
    base["@id"] = self.id
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Flow():
  __tag__ = "sequenceFlow"

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

class Element():
  __labeled__ = False

  def __init__(self, id, x=0, y=0):
    self.id = id
    self.x = x
    self.y = y
    self.incoming = []
    self.outgoing = []

  @property
  def shape_properties(self):
    return {}
  
  def flow_to(self, next_element):
    Flow(self, next_element)
    return self
  
  def as_dict(self):
    base = {
      "@id": self.id
    }
    if self.outgoing:
      base["bpmn:outgoing"] = prune([ flow.id for flow in self.outgoing ])
    if self.incoming:
      base["bpmn:incoming"] = prune([ flow.id for flow in self.incoming ])
    return base

class Start(Element):
  __tag__    = "startEvent"
  __width__  = 36
  __height__ = 36

  def __init__(self, id="start", **kwargs):
    super().__init__(id, **kwargs)

class End(Element):
  __tag__ = "endEvent"
  __width__  = 36
  __height__ = 36

  def __init__(self, id="end", **kwargs):
    super().__init__(id, **kwargs)

class Task(Element):
  __tag__     = "task"
  __width__   = 100
  __height__  = 80
  __labeled__ = True

  def __init__(self, name="", id="task", **kwargs):
    super().__init__(id, **kwargs)
    self.name = name

  def as_dict(self):
    base = super().as_dict()
    base["@name"] = self.name
    return base
