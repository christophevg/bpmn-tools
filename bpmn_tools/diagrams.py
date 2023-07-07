"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

from . import xml

from .collaboration import Participant
from .flow          import Process, Element, Flow, MessageFlow

class Bounds(xml.Element):
  __tag__ = "dc:Bounds"
  
  def __init__(self, x=0, y=0, height=0, width=0):
    super().__init__()
    self["x"]      = str(int(x))
    self["y"]      = str(int(y))
    self["height"] = str(int(height))
    self["width"]  = str(int(width))

class Label(xml.Element):
  __tag__ = "bpmndi:BPMNLabel"
  
  def __init__(self, label=None):
    super().__init__()
    self.text = label

class Shape(xml.Element):
  __tag__ = "bpmndi:BPMNShape"

  def __init__(self, element=None, id=None):
    super().__init__()
    self._element = element
    self.label    = None
    self._bounds  = None

  def append(self, child):
    if isinstance(child, Bounds):
      self._bounds = child
      child._parent = self
    else:
      super().append(child)
    return self

  @property
  def id(self):
    return f"shape_{self.element['id']}"

  @property
  def element(self):
    if self._element:
      return self._element
    if self["bpmnElement"]:
      return self.root.find("id", self["bpmnElement"], skip=self)
    return None

  @property
  def attributes(self):
    attributes = {}
    if self.element:
      attributes.update({
        "id"          : self.id,
        "bpmnElement" : self.element["id"]
      })
      if self.element.__horizontal__:
        attributes["isHorizontal"] = "true"
      if self.element.__color_scheme__:
        attributes.update(self.element.__color_scheme__)
    return attributes

  @property
  def children(self):
    children = []
    if self.element:
      children = [
        Bounds(
          x      = self.element.x,
          y      = self.element.y,
          height = self.element.height,
          width  = self.element.width
        )
      ]
      if self.element.__labeled__:
        children.append(Label(self.label))
    return children

class WayPoint(xml.Element):
  __tag__ = "di:waypoint"
  
  def __init__(self, x=0, y=0):
    super().__init__()
    self["x"] = str(int(x))
    self["y"] = str(int(y))

class Edge(xml.Element):
  __tag__ = "bpmndi:BPMNEdge"

  def __init__(self, flow=None, id=None):
    super().__init__()
    self._flow = flow

  @property
  def flow(self):
    if self._flow:
      return self._flow
    if self["bpmnElement"]:
      return self.root.find("id", self["bpmnElement"], skip=self)
    return None

  def __getitem__(self, name):
    if name == "id":
      return f"edge_{self.flow['id']}"
    return super().__getitem__(name)

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    if self.flow:
      attributes.update({
        "id"          : self["id"],
        "bpmnElement" : self.flow["id"]
      })
    return attributes

  @property
  def children(self):
    children = super().children.copy()
    if self.flow:
      below = self.flow.target.y > (self.flow.source.y + self.flow.source.height)
      above = (self.flow.target.y + self.flow.target.height) < self.flow.source.y
      if not (above or below): 
        children = [
          WayPoint(
            x=self.flow.source.x + self.flow.source.width,
            y=self.flow.source.y + int(self.flow.source.height/2)
          ),
          WayPoint(
            x=self.flow.target.x,
            y=self.flow.target.y + int(self.flow.target.height/2)
          )
        ]
      else:
        if self.flow.source.y < self.flow.target.y:
          top     = self.flow.source
          bottom  = self.flow.target
          reverse = False
        else:
          top     = self.flow.target
          bottom  = self.flow.source
          reverse = True
        half_way_dist = int((top.y + top.height - bottom.y) / 2)
        children = [
          WayPoint(
            x=top.x + int(top.width/2),
            y=top.y + top.height
          ),
          WayPoint(
            x=top.x + int(top.width/2),
            y=top.y + top.height - half_way_dist
          ),
          WayPoint(
            x=bottom.x + int(bottom.width/2),
            y=bottom.y + half_way_dist
          ),
          WayPoint(
            x=bottom.x + int(bottom.width/2),
            y=bottom.y
          )
        ]
        if reverse:
          children.reverse()
    return children

class Plane(xml.Element):
  __tag__ = "bpmndi:BPMNPlane"

  def __init__(self, id="plane", element=None):
    super().__init__()
    self._element = element
    self["id"] = id
    self._shapes = []
    self._edges  = []

  @property
  def element(self):
    if self._element:
      return self._element
    if self["bpmnElement"]:
      return self.root.find("id", self["bpmnElement"], skip=self)
    return None

  @property
  def attributes(self):
    attributes = super().attributes.copy()
    if self.element:
      attributes.update({
        "bpmnElement" : self.element["id"],
        "id" : f"plane_{self.element['id']}"
      })
    return attributes

  def append(self, child):
    if isinstance(child, Shape):
      self._shapes.append(child)
      child._parent = self
    elif isinstance(child, Edge):
      self._edges.append(child)
      child._parent = self
    else:
      super().append(child)
    return self

  @property
  def children(self):
    children = super().children.copy()
    if self.element:
      for participant in self.element.children_oftype(Participant):
        children.append(Shape(participant))
        if participant.process:
          for lane in participant.process.laneset.lanes:
            children.append(Shape(lane))
          for element in participant.process.children_oftype(Element):
            children.append(Shape(element))
          for flow in participant.process.children_oftype(Flow):
            children.append(Edge(flow))
      for flow in self.element.children_oftype(MessageFlow):
        children.append(Edge(flow))
    return children

class Diagram(xml.Element):
  __tag__ = "bpmndi:BPMNDiagram"

  def __init__(self, id="diagram", plane=None):
    super().__init__()
    self._plane = plane
    self["id"]  = id

  @property
  def plane(self):
    if self._plane:
      return self._plane
    if self._children:
      return self._children[0]
    return Plane()

  @property
  def children(self):
    return [ self.plane ]
