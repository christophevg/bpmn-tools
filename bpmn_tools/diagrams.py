"""
  Classes representing the different parts of a BPMN file.
"""

def prune(lst):
  if len(lst) == 1:
    return lst[0]
  return lst

class Definitions():
  def __init__(self, id="definitions"):
    self.id = id
    self._definitions = {}
  
  def append(self, definition):
    try:
      self._definitions[definition.__tag__].append(definition)
    except KeyError:
      self._definitions[definition.__tag__] = [ definition ]
    return self

  def extend(self, definitions):
    for definition in definitions:
      self.append(definition)
    return self

  def as_dict(self):
    # compile definitions
    base = {
      f"bpmn:{name}" : prune([
        definition.as_dict()[f"bpmn:{name}"] for definition in definitions
      ]) for name, definitions in self._definitions.items()
    }
    # add properties
    base["@id"] = self.id
    # add namespaces
    base.update({
      "@xmlns:bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "@xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
      "@xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
      "@xmlns:di": "http://www.omg.org/spec/DD/20100524/DI"
    })
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Process():
  __tag__ = "process"

  def __init__(self, id="process"):
    self.id = id
    self._elements = {}
  
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

class Activity():
  __labeled__ = False

  def __init__(self, id, x=0, y=0):
    self.id = id
    self.x = x
    self.y = y
    self.incoming = []
    self.outgoing = []
  
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

class Start(Activity):
  __tag__    = "startEvent"
  __width__  = 36
  __height__ = 36

  def __init__(self, id="start"):
    super().__init__(id)

class End(Activity):
  __tag__ = "endEvent"
  __width__  = 36
  __height__ = 36

  def __init__(self, id="end"):
    super().__init__(id)

class Task(Activity):
  __tag__     = "task"
  __width__   = 100
  __height__  = 80
  __labeled__ = True

  def __init__(self, name="", id="task"):
    super().__init__(id)
    self.name = name

  def as_dict(self):
    base = super().as_dict()
    base["@name"] = self.name
    return base

class Collaboration():
  __tag__ = "collaboration"

  def __init__(self, id="process"):
    self.id = id
    self.participants = []
  
  def append(self, participant):
    self.participants.append(participant)
    return self

  def extend(self, participants):
    self.participants.extend(participants)
    return self

  def as_dict(self):
    # compile participants
    if self.participants:
      base = {
        f"bpmn:participant" : prune([
          participant.as_dict() for participant in self.participants
        ])
      }

    # add properties
    base["@id"] = self.id
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Participant():
  def __init__(self, name="", process=None, id="participant"):
    self.id     = id
    self.name    = name
    self.process = process

  def as_dict(self):
    return {
      "@id"        : self.id, 
      "@name"      : self.name,
      "@processRef": self.process.id
    }

class Shape():
  def __init__(self, element, id=None, label=None):
    self._id = id
    self.element = element
    self.label = label

  @property
  def id(self):
    if self.id: return self.id
    return f"shape_{self.element.id}"

  @property
  def bounds(self):
    return {
      "x" : self.element.x,
      "y" : self.element.y,
      "width" : self.element.__width__,
      "height": self.element.__height__
    }

  def as_dict(self):
    base = {
      "@id": f"shape_{self.element.id}",
      "@bpmnElement": self.element.id,
      "dc:Bounds": {
        "@x": str(self.bounds["x"]),
        "@y": str(self.bounds["y"]),
        "@width": str(self.bounds["width"]),
        "@height": str(self.bounds["height"])
      }
    }
    
    if self.element.__labeled__:
      base["bpmndi:BPMNLabel"] = self.label

    return {
      "bpmndi:BPMNShape" : base
    }

class Edge():
  def __init__(self, flow):
    self.flow = flow
  
  def as_dict(self):
    return {
      "bpmndi:BPMNEdge" : {
        "@id": f"edge_{self.flow.id}",
        "@bpmnElement": self.flow.id,
        "di:waypoint": [
          {
            "@x": str(self.flow.source.x + self.flow.source.__width__),
            "@y": str(self.flow.source.y + int(self.flow.source.__height__/2))
          },
          {
            "@x": str(self.flow.target.x),
            "@y": str(self.flow.target.y + int(self.flow.target.__height__/2))
          }
        ]
      }
    }
