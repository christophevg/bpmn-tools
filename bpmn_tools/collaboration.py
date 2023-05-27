"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

from . import xml

class Participant(xml.Element):
  __tag__        = "bpmn:participant"
  __height__     = 125
  __width__      = 600
  __horizontal__ = True

  def __init__(self, name="participant", process=None, id="participant"):
    super().__init__()
    self["id"]   = id
    self["name"] = name
    self.process = process
    self.x = 0
    self.y = 0
  
  @property
  def attributes(self):
    attributes = super().attributes
    if self.process:
      attributes.update({
        "processRef" : self.process["id"]
      })
    return attributes

class Collaboration(xml.Element):
  __tag__ = "bpmn:collaboration"

  def __init__(self, id="collaboration"):
    super().__init__()
    self["id"] = id
