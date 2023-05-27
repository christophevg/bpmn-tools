"""
  Classes representing the different parts of a BPMN file.
"""

from .xml import Element

class Definitions(Element):
  __tag__ = "bpmn:definitions"

  def __init__(self, id="definitions"):
    super().__init__()
    self["id"] = id

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    attributes.update({
      "xmlns:bpmn"  : "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
      "xmlns:dc"    : "http://www.omg.org/spec/DD/20100524/DC",
      "xmlns:di"    : "http://www.omg.org/spec/DD/20100524/DI"
    })
    return attributes
