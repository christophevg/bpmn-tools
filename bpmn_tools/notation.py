"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

class Definitions():
  def __init__(self, id="definitions"):
    self.id = id
    self._definitions = {}
    self.diagrams = []
  
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
    # add diagrams
    diagrams = [ diagram.as_dict()["bpmndi:BPMNDiagram"] for diagram in self.diagrams ]
    if diagrams:
      base["bpmndi:BPMNDiagram"] = prune(diagrams)

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
