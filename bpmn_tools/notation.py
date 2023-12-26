"""
  Classes representing the different parts of a BPMN file.
"""

import sys
import inspect

from bpmn_tools.collaboration import Collaboration
from bpmn_tools.flow          import Process
from bpmn_tools.diagrams      import Diagram

from bpmn_tools.xml import Element, IdentifiedElement

def get_classes(module):
  return [
    c[1] for c in inspect.getmembers(sys.modules[module], inspect.isclass)
  ]

class Definitions(IdentifiedElement):
  __tag__ = "bpmn:definitions"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.processes      = []
    self.collaborations = []
    self.diagrams       = []

  @classmethod
  def from_dict(cls, d, raise_unmapped=False):
    classes = get_classes("bpmn_tools.notation") + \
              get_classes("bpmn_tools.collaboration") + \
              get_classes("bpmn_tools.flow") + \
              get_classes("bpmn_tools.diagrams") + \
              get_classes("bpmn_tools.extensions")
    definitions = Element.from_dict(d, classes=classes, raise_unmapped=raise_unmapped)
    if isinstance(definitions, Definitions):
      for diagram in definitions.diagrams:
        for shape in diagram.plane._shapes:
          if shape._bounds:
            element = definitions.find("id", shape["bpmnElement"])
            if element:
              element.x      = int(float(shape._bounds.x))
              element.y      = int(float(shape._bounds.y))
              element.width  = int(float(shape._bounds.width))
              element.height = int(float(shape._bounds.height))
              color_scheme   = {}
              for k, v in shape._attributes.items():
                if k in [
                  "bioc:stroke",
                  "bioc:fill",
                  "color:background-color",
                  "color:border-color"
                ]:
                  color_scheme[k] = v
              if color_scheme:
                element.__color_scheme__ = color_scheme
            else:
              raise ValueError(f"diagram shape ({shape}) has no element")
    return definitions

  def append(self, child):
    if isinstance(child, Process):
      self.processes.append(child)
      child._parent = self
    elif isinstance(child, Collaboration):
      self.collaborations.append(child)
      child._parent = self
    elif isinstance(child, Diagram):
      self.diagrams.append(child)
      child._parent = self
    else:
      raise ValueError(f"unsupported child for Definitions: {child}")
    return self
    return self

  def element(self, id):
    for process in self.processes:
      match = process.find("id", id)
      if match:
        return match
    return None
    
  @property
  def children(self):
    return super().children + self.processes + self.collaborations + self.diagrams

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    attributes.update({
      "xmlns:bpmn"  : "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
      "xmlns:dc"    : "http://www.omg.org/spec/DD/20100524/DC",
      "xmlns:di"    : "http://www.omg.org/spec/DD/20100524/DI",
      "xmlns:bioc"  : "http://bpmn.io/schema/bpmn/biocolor/1.0",
      "xmlns:color" : "http://www.omg.org/spec/BPMN/non-normative/color/1.0",
      "xmlns:zeebe" : "http://camunda.org/schema/zeebe/1.0",
      "xmlns:xsi"   : "http://www.w3.org/2001/XMLSchema-instance"
    })
    return attributes
