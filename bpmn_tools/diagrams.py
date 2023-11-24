"""
  Classes representing the different parts of a BPMN file.
"""

from . import xml

from bpmn_tools.collaboration import Participant
from bpmn_tools.flow          import Element, Flow, MessageFlow, Gateway
from bpmn_tools.flow          import Annotation, Association

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
    if not self.flow or not self.flow.source or not self.flow.target:
      return children
    if isinstance(self.flow.source, Gateway) or isinstance(self.flow.target, Gateway):
      children = self._route_gateway()
    else:
      children = self._route_default()
    if self.flow["name"]:
      x = self.flow.target.x
      y = self.flow.target.y + self.flow.target.height/2
      children.append(Label(x, y))
    return children

  def _route_default(self):
    """
      Default routing routes directly from the right/middel exit of the source
      to the left/middle of the target.
    
      Unless the target lies completely above or below the source, then routing
      starts from the bottom/top to the top/bottom.

                                    T (above)
      0,0 --->                      ^
       |    X       S --> T     +---+
       | Y                      |
       v                        S
    """
    # determine position of target vs source
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
      if below:
        top     = self.flow.source
        bottom  = self.flow.target
        reverse = False
      else:
        top     = self.flow.target
        bottom  = self.flow.source
        reverse = True
      children = [
        WayPoint(                               # bottom middle exit 
          x=top.x + int(top.width/2),
          y=top.y + top.height
        ),
        WayPoint(
          x=top.x + int(top.width/2),           # straight down to 17px
          y=bottom.y - 17
        ),
        WayPoint(                               # left/right to bottom
          x=bottom.x + int(bottom.width/2),
          y=bottom.y - 17
        ),
        WayPoint(
          x=bottom.x + int(bottom.width/2),     # top middle entry
          y=bottom.y
        )
      ]
      if reverse:
        children.reverse()
    return children
      
  def _route_gateway(self):
    """
      Gateway routing routes directly from the right/middel exit of the source
      to the left/middle of the target.
    
      Unless the target's middle lies above or below the gateway, then routing
      starts from the bottom/top to the left/middle.

                                    
      0,0 --->                      
       |    X       G --> T     +---> T
       | Y                      |
       v                        G
    """
    # determine position of target vs source
    below = self.flow.target.y > (self.flow.source.y + int(self.flow.source.height/2))
    above = (self.flow.target.y + int(self.flow.target.height/2)) < self.flow.source.y
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
      if below:
        top     = self.flow.source
        bottom  = self.flow.target
        if isinstance(top, Gateway): # starting from GW?
          children = [
            WayPoint(                               # bottom middle exit 
              x=top.x + int(top.width/2),
              y=top.y + top.height
            ),
            WayPoint(
              x=top.x + int(top.width/2),           # straight down middle
              y=bottom.y + int(bottom.height/2)
            ),
            WayPoint(                               # left/right to left
              x=bottom.x,
              y=bottom.y + int(bottom.height/2)
            )
          ]
        else:
          children = [
            WayPoint(                               # middle right exit 
              x=top.x + top.width,
              y=top.y + int(top.height/2)
            ),
            WayPoint(
              x=bottom.x + int(bottom.width/2),     # right to middle
              y=top.y + int(top.height/2)
            ),
            WayPoint(                               # down to top
              x=bottom.x + int(bottom.width/2),
              y=bottom.y
            )
          ]
      else: # target is above
        top     = self.flow.target
        bottom  = self.flow.source
        # gateways route from top/bottom to side of tasks, but
        # from side to top/bottom of other gws
        if isinstance(bottom, Gateway) and not isinstance(top, Gateway):
          children = [
            WayPoint(                               # top middle exit 
              x=bottom.x + int(bottom.width/2),
              y=bottom.y
            ),
            WayPoint(
              x=bottom.x + int(bottom.width/2),     # straight up to middle
              y=top.y + int(top.height/2)
            ),
            WayPoint(                               # left/right to left
              x=top.x,
              y=top.y + int(top.height/2)
            )
          ]
        else:
          children = [
            WayPoint(                               # middle right exit 
              x=bottom.x + bottom.width,
              y=bottom.y + int(bottom.height/2)
            ),
            WayPoint(                               # right to middle
              x=top.x + int(top.width/2),
              y=bottom.y + int(bottom.height/2)
            ),
            WayPoint(                               # up to bottom
              x=top.x + int(top.width/2),
              y=top.y + top.height
            )
          ]
    return children

class Plane(xml.Element):
  __tag__ = "bpmndi:BPMNPlane"

  def __init__(self, id="plane", element=None):
    super().__init__()
    self._element = element
    self["id"]   = id
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
          for element in participant.process.children_oftype(Annotation):
            children.append(Shape(element))
          for element in participant.process.children_oftype(Association):
            children.append(Edge(element))
          for flow in participant.process.children_oftype(Flow):
            children.append(Edge(flow))
      for flow in self.element.children_oftype(MessageFlow):
        children.append(Edge(flow))
    return sorted(children, key=lambda k: k.id)

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
