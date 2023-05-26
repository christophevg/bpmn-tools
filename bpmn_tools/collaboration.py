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

  def __init__(self, name="participant", process=None, id="participant", **kwargs):
    self.name = name
    self.process = process
    kwargs["@id"] = id
    super().__init__(**kwargs)
    self.x = 0
    self.y = 0
  
  @property
  def _more_attributes(self):
    return {
      "name" : self.name,
      "processRef" : self.process.id
    }

class Collaboration(xml.Element):
  __tag__ = "bpmn:collaboration"

  def __init__(self, id="collaboration", **kwargs):
    kwargs["@id"] = id
    super().__init__(**kwargs)
