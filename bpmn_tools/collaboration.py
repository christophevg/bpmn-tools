"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

from . import xml

class Participant(xml.Element):
  __tag__        = "bpmn:participant"
  __horizontal__ = True

  def __init__(self, name="participant", process=None, id="participant"):
    super().__init__()
    self["id"]   = id
    self["name"] = name
    self._process = process
    self.x      = 0
    self.y      = 0
    self.height = 125
    self.width  = 600
  
  @property
  def process(self):
    if self._process:
      return self._process
    elif self["processRef"]:
      return self.root.find("id", self["processRef"])
    return None
  
  @property
  def attributes(self):
    attributes = super().attributes.copy()
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
