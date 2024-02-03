"""

All (Process)Flow related classes.

"""

from dataclasses import dataclass, field
from typing import List, Optional

from bpmn_tools.future import xml

@dataclass
class ProcessBound(xml.Element):
  @property
  def process(self):
    return self._parent.process
  
@dataclass
class FlowNode(xml.IdentifiedElement):
  pass

@dataclass
class FlowNodeRef(ProcessBound):
  """
  Refers to a FlowNode, which can be passed to the constructor as an element.
  This will be the main source. The actual reference is stored in the text
  of the XML tag. Access to that text is intercepted and used to keep the
  element "in sync".
  """
  _tag                = "bpmn:flowNodeRef"
  _catch_all_children = False

  element  : FlowNode           = field(default=None)
  _element : Optional[FlowNode] = field(init=False) # Optional?
  _text    : Optional[str]      = field(init=False)

  @property
  def element(self):
    if self._element:
      return self._element
    # no actual element, try to find it
    try:
      self._element = self.process.element(self._text)
      return self._element
    except (TypeError, AttributeError):
      raise ValueError(f"could not resolve reference {self._text}")

  @element.setter
  def element(self, new_element):
    if type(new_element) is property:
      new_element = None
    self._element = new_element
    # keep text up2date
    if new_element:
      self._text = new_element.id

  @property
  def text(self):
    try:
      return self._element.id # if we have a FlowNode
    except AttributeError:
      return self._text      # else use the textual version

  @text.setter
  def text(self, new_text):
    if type(new_text) is property:
      new_text = None
    self._text = new_text

    # at least reset our reference
    self._element = None
    # and try to resolve it and store as an element
    try:
      self._element = self.process.element(new_text)
    except (TypeError, AttributeError):
      pass

@dataclass
class Lane(xml.IdentifiedElement, ProcessBound):
  """
  A lane holds references to the flow nodes that are depicted inside it.
  The object model allows for specifying these as elements. This class will
  accept them as such, but wrap them in a FlowNodeRef and always work with
  these references.
  """
  _tag                = "bpmn:lane"
  _catch_all_children = False
  
  elements : List[FlowNode]    = field(default_factory=list)
  _refs    : List[FlowNodeRef] = field(init=False, metadata={"child": True})

  # horizontal : bool = True  # is part of the shape (TODO)

  @property
  def elements(self):
    return [ ref.element for ref in self._refs ]
  
  @elements.setter
  def elements(self, new_elements):
    if type(new_elements) is property:
      new_elements = []
    self._refs = [ FlowNodeRef(element=element) for element in new_elements ]

  def append(self, child):
    if isinstance(child, FlowNode):
      wrapped = FlowNodeRef(element=child)
      child._parent = wrapped
      wrapped._parent = self
      self._refs.append(wrapped)  # wrap it
    else:
      return super().append(child)
    return self    

  def has_child(self, child):
    for ref in self._refs:
      if ref.element is child:
        return True
    return False

@dataclass
class LaneSet(xml.IdentifiedElement, ProcessBound):
  """
  LaneSet keeps one or more Lanes together.
  """
  __tag__             = "bpmn:laneSet"
  _catch_all_children = False

  lanes : List[Lane] = field(**xml.children)

  def lane_of(self, child):
    for lane in self.lanes:
      if lane.has_child(child):
        return lane
    return None

@dataclass
class Process(xml.IdentifiedElement, ProcessBound):
  """
  
  """
  _tag = "bpmn:process"
  
  elements : List[xml.Element] = field(**xml.children)
  # laneset  : "LaneSet"     = None
  isExecutable : str = field(**xml.attribute, default="true")
  
  @property
  def process(self):
    return self
  
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
