"""

All (Process)Flow related classes.

"""

from dataclasses import dataclass, field
from typing import List

from bpmn_tools.future import xml

@dataclass
class Process(xml.IdentifiedElement):
  _tag = "bpmn:process"
  elements : List[xml.Element] = field(**xml.children)
  # laneset  : "LaneSet"     = None

  def __post_init__(self):
    try:
      self.attributes["isExecutable"]
    except KeyError:
      self.attributes["isExecutable"] = "true"
  
  # @property
  # def participant(self):
  #   for collaboration in self._parent.collaborations:
  #     participant = collaboration.find("processRef", self.id)
  #     if participant:
  #       return participant
  #   return None
  
  # @property
  # def elements(self):
  #   elems = self._elements  # direct elements
  #   # add elements that are "hidden" in lanes
  #   if len(self.laneset) > 0:
  #     for lane in self.laneset.lanes:
  #       for element in lane.elements:
  #         if element not in elems:
  #           elems.append(element)
  #   return elems
  
  # def append(self, child):
  #   if isinstance(child, Element):
  #     self._elements.append(child)
  #     child._parent = self
  #   elif isinstance(child, Annotation):
  #     self._elements.append(child)
  #     child._parent = self
  #   elif isinstance(child, LaneSet):
  #     self.laneset = child
  #     child._parent = self
  #   elif isinstance(child, Lane):
  #     self.laneset.append(child)
  #     child._parent = self
  #   else:
  #     super().append(child) # generic child handling
  #   return self
  #
  # @property
  # def children(self):
  #   children = super().children.copy()
  #   children.extend(self.elements)
  #   if len(self.laneset) > 0:
  #     children.append(self.laneset)
  #   return children
