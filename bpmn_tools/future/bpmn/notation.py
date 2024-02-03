"""
  Top-level Definitions class is the root of a BPMN model.
"""

import sys
from inspect import getmembers, isclass

from dataclasses import dataclass, field
from typing import List

# TODO: replace with future
from bpmn_tools.collaboration import Collaboration
from bpmn_tools.flow          import Process
from bpmn_tools.diagrams      import Diagram

from bpmn_tools.future import xml

BPMN_NS = {
  "xmlns:bpmn"  : "http://www.omg.org/spec/BPMN/20100524/MODEL",
  "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
  "xmlns:dc"    : "http://www.omg.org/spec/DD/20100524/DC",
  "xmlns:di"    : "http://www.omg.org/spec/DD/20100524/DI",
  "xmlns:bioc"  : "http://bpmn.io/schema/bpmn/biocolor/1.0",
  "xmlns:color" : "http://www.omg.org/spec/BPMN/non-normative/color/1.0",
  "xmlns:zeebe" : "http://camunda.org/schema/zeebe/1.0",
  "xmlns:xsi"   : "http://www.w3.org/2001/XMLSchema-instance"
}

@dataclass
class Definitions(xml.IdentifiedElement):
  _tag = "bpmn:definitions"
  processes      : List[Process]       = field(**xml.list_of_children)
  collaborations : List[Collaboration] = field(**xml.list_of_children)
  diagrams       : List[Diagram]       = field(**xml.list_of_children)

  def __post_init__(self):
    self. attributes = BPMN_NS

  def element(self, id):
    for process in self.processes:
      match = process.find("id", id)
      if match:
        return match
    return None

  @classmethod
  def from_dict(cls, d, raise_unmapped=False):
    # load xml elements using all known BPMN classes
    return xml.Element.from_dict(
      d,
      classes=[
        c[1] for c in getmembers(sys.modules["bpmn_tools.future.bpmn"], isclass)
      ],
      raise_unmapped=raise_unmapped
    )

    # TODO: see if this can be done dynamically from the element, finding its
    #       shape and use it

    # # adopt shape's position, size, color onto element
    # if isinstance(definitions, Definitions):
    #   for diagram in definitions.diagrams:
    #     for shape in diagram.plane._shapes:
    #
    #       if shape._bounds:
    #         element = definitions.find("id", shape["bpmnElement"])
    #
    #         if element:
    #           element.x      = int(float(shape._bounds.x))
    #           element.y      = int(float(shape._bounds.y))
    #           element.width  = int(float(shape._bounds.width))
    #           element.height = int(float(shape._bounds.height))
    #           color_scheme   = {}
    #
    #           for k, v in shape._attributes.items():
    #             if k in [
    #               "bioc:stroke",
    #               "bioc:fill",
    #               "color:background-color",
    #               "color:border-color"
    #             ]:
    #               color_scheme[k] = v
    #           if color_scheme:
    #             element.__color_scheme__ = color_scheme
    #         else:
    #           raise ValueError(f"diagram shape ({shape}) has no element")
    # return definitions
