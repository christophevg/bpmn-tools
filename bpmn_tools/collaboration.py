"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

from .flow import Element

class Participant(Element):
  def __init__(self, name="", process=None, id="participant", **kwargs):
    super().__init__(id, **kwargs)
    self.name       = name
    self.process    = process
    self.__width__  = 600
    self.__height__ = 125

  @property
  def elements(self):
    if not self.process: return []
    return self.process.elements

  @property
  def flows(self):
    if not self.process: return []
    return self.process.flows

  @property
  def shape_properties(self):
    return {
      "@isHorizontal" : "true"
    }

  def as_dict(self):
    return {
      "@id"        : self.id, 
      "@name"      : self.name,
      "@processRef": self.process.id
    }

class Collaboration():
  __tag__ = "collaboration"

  def __init__(self, id="process"):
    self.id = id
    self.participants = []
  
  @property
  def elements(self):
    l = self.participants.copy()
    for participant in self.participants:
      l.extend(participant.elements)
    return l

  @property
  def flows(self):
    l = []
    for participant in self.participants:
      l.extend(participant.flows)
    return l

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
