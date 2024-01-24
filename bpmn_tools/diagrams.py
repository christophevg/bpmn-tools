"""
  Classes representing the different parts of a BPMN file.
"""

from . import xml

from bpmn_tools.collaboration import Participant
from bpmn_tools.flow          import Element, Flow, MessageFlow
from bpmn_tools.flow          import Annotation, Association

from bpmn_tools.layout         import routing

class Bounds(xml.Element):
  __tag__ = "dc:Bounds"
  
  def __init__(self, x=0, y=0, width=0, height=0):
    super().__init__()
    self["x"]      = str(int(x))
    self["y"]      = str(int(y))
    self["width"]  = str(int(width))
    self["height"] = str(int(height))

class Label(xml.Element):
  __tag__ = "bpmndi:BPMNLabel"
  
  def __init__(self, x=0, y=0):
    super().__init__()
    self.x = x - 50         # add offset from target point x,y
    self.y = y + 5

  @property
  def children(self):
    return [
      Bounds(
        x=self.x,
        y=self.y,
        width=0,
        height=14
      )
    ]

class Shape(xml.Element):
  __tag__ = "bpmndi:BPMNShape"

  def __init__(self, element=None, id=None):
    super().__init__()
    self._element = element
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
      if self.element.__marker__:
        attributes["isMarkerVisible"] = "true"
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
    return children

class Edge(xml.Element):
  __tag__ = "bpmndi:BPMNEdge"

  def __init__(self, flow=None, id=None, strategy=None):
    super().__init__()
    self._flow = flow
    self.strategy = routing.Default() if strategy is None else strategy

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

    if not self.flow or not self.flow.source or not self.flow.target:
      return children

    children = self.strategy.route(self.flow)

    if self.flow["name"]:
      x = self.flow.target.x
      y = self.flow.target.y + self.flow.target.height/2
      children.append(Label(x, y))
    return children

class Plane(xml.Element):
  __tag__ = "bpmndi:BPMNPlane"

  def __init__(self, id="plane", element=None, strategy=None):
    super().__init__()
    self._element = element
    self["id"]    = id
    self._shapes  = []
    self._edges   = []
    self.strategy = strategy

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
          for element in participant.process.children_oftype(Annotation):
            children.append(Shape(element))
          for element in participant.process.children_oftype(Association):
            children.append(self.edge(element))
          for flow in participant.process.children_oftype(Flow):
            children.append(self.edge(flow))
      for flow in self.element.children_oftype(MessageFlow):
        children.append(self.edge(flow))
    return sorted(children, key=lambda k: k.id)

  def edge(self, flow):
    return Edge(flow, strategy=self.strategy)
    
class Diagram(xml.Element):
  __tag__ = "bpmndi:BPMNDiagram"

  def __init__(self, id="diagram", plane=None):
    super().__init__()
    self._plane   = plane
    self["id"]    = id
    self.strategy = routing.Default()

  @property
  def plane(self):
    if self._plane:
      plane = self._plane
    elif self._children:
      plane = self._children[0]
    else:
      plane = Plane()
    plane.strategy = self.strategy
    return plane

  @property
  def children(self):
    return [ self.plane ]
