"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

from . import xml

from .collaboration import Participant
from .flow          import Process, Element, Flow

class Bounds(xml.Element):
  __tag__ = "dc:Bounds"
  
  def __init__(self, x=0, y=0, height=0, width=0, **kwargs):
    if not "@x" in kwargs:
      kwargs["@x"]      = str(x)
    if not "@y" in kwargs:
      kwargs["@y"]      = str(y)
    if not "@height" in kwargs:
      kwargs["@height"] = str(height)
    if not "@width" in kwargs:
      kwargs["@width"]  = str(width)
    super().__init__(**kwargs)

class Label(xml.Element):
  __tag__ = "bpmndi:BPMNLabel"
  
  def __init__(self, label=None, **kwargs):
    self.text = label
    super().__init__(**kwargs)

class Shape(xml.Element):
  __tag__ = "bpmndi:BPMNShape"

  def __init__(self, element=None, id=None, **kwargs):
    self.element = element
    self.label   = None
    super().__init__(**kwargs)

  @property
  def id(self):
    return f"shape_{self.element.id}"

  @property
  def _more_attributes(self):
    more = {}
    if self.element:
      more.update({
        "id"          : self.id,
        "bpmnElement" : self.element.id
      })
      if self.element.__horizontal__:
        more["isHorizontal"] = "true"
    return more

  @property
  def _more_children(self):
    more = []
    if self.element:
      more.append(
        Bounds(
          x=self.element.x,
          y=self.element.y,
          height=self.element.__height__,
          width=self.element.__width__
        )
      )
      if self.element.__labeled__:
        more.append(Label(self.label))
    return more

class WayPoint(xml.Element):
  __tag__ = "di:waypoint"
  
  def __init__(self, x=0, y=0, **kwargs):
    if not "@x" in kwargs:
      kwargs["@x"] = str(x)
    if not "@y" in kwargs:
      kwargs["@y"] = str(y)
    super().__init__(**kwargs)

class Edge(xml.Element):
  __tag__ = "bpmndi:BPMNEdge"

  def __init__(self, flow=None, id=None, **kwargs):
    self.flow = flow
    super().__init__(**kwargs)

  @property
  def id(self):
    return f"edge_{self.flow.id}"

  @property
  def _more_attributes(self):
    if self.flow:
      return {
        "id"          : self.id,
        "bpmnElement" : self.flow.id
      }
    return {}

  @property
  def _more_children(self):
    more = []
    if self.flow:
      more.extend([
        WayPoint(
          x=self.flow.source.x + self.flow.source.__width__,
          y=self.flow.source.y + int(self.flow.source.__height__/2)
        ),
        WayPoint(
          x=self.flow.target.x,
          y=self.flow.target.y + int(self.flow.target.__height__/2)
        )
      ])
    return more

class Plane(xml.Element):
  __tag__ = "bpmndi:BPMNPlane"

  def __init__(self, id="plane", element=None, **kwargs):
    self._element = element
    if self._element and "@bpmnElement" in kwargs:
      if self._element.id != kwargs["@bpmnElement"]:
        raise ValueError("got element and bpmnElement, with different ids")
    if not "@id" in kwargs:
      kwargs["@id"] = id
    super().__init__(**kwargs)

  @property
  def element(self):
    if self._element:
      return self._element
    if self.bpmnElement:
      return self.find("id", self.bpmnElement)
    return None

  @property
  def _more_attributes(self):
    more = {}
    if self.element:
      more["bpmnElement"] = self.element.id
      more["id"] = f"plane_{self.element.id}"
    return more

  @property
  def _more_children(self):
    more = []
    if self.element:
      for participant in self.element.children_oftype(Participant):
        more.append(Shape(participant))
        if participant.process:
          for element in participant.process.children_oftype(Element):
            more.append(Shape(element))
          for flow in participant.process.children_oftype(Flow):
            more.append(Edge(flow))
    return more

class Diagram(xml.Element):
  __tag__ = "bpmndi:BPMNDiagram"

  def __init__(self, id="diagram", plane=None, **kwargs):
    self.plane = plane
    kwargs["@id"] = id
    super().__init__(**kwargs)

  @property
  def _more_children(self):
    if self.plane:
      return [ self.plane ]
    else:
      return [ Plane() ]
