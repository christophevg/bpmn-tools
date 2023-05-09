"""
  Classes representing the different parts of a BPMN file.
"""

from .util import prune

class Shape():
  def __init__(self, element, id=None, label=None):
    self._id = id
    self.element = element
    self.label = label

  @property
  def id(self):
    if self.id: return self.id
    return f"shape_{self.element.id}"

  @property
  def bounds(self):
    return {
      "x" : self.element.x,
      "y" : self.element.y,
      "width" : self.element.__width__,
      "height": self.element.__height__
    }

  def as_dict(self):
    base = {
      "@id": f"shape_{self.element.id}",
      "@bpmnElement": self.element.id,
      "dc:Bounds": {
        "@x": str(self.bounds["x"]),
        "@y": str(self.bounds["y"]),
        "@width": str(self.bounds["width"]),
        "@height": str(self.bounds["height"])
      }
    }
    
    if self.element.__labeled__:
      base["bpmndi:BPMNLabel"] = self.label

    base.update(self.element.shape_properties)

    return {
      "bpmndi:BPMNShape" : base
    }

class Edge():
  def __init__(self, flow):
    self.flow = flow
  
  def as_dict(self):
    return {
      "bpmndi:BPMNEdge" : {
        "@id": f"edge_{self.flow.id}",
        "@bpmnElement": self.flow.id,
        "di:waypoint": [
          {
            "@x": str(self.flow.source.x + self.flow.source.__width__),
            "@y": str(self.flow.source.y + int(self.flow.source.__height__/2))
          },
          {
            "@x": str(self.flow.target.x),
            "@y": str(self.flow.target.y + int(self.flow.target.__height__/2))
          }
        ]
      }
    }

class Plane():
  def __init__(self, id="plane", element=None):
    self._id     = id
    self.element = element

  @property
  def id(self):
    if self.element:
      return f"plane_{self.element.id}"
    else:
      return self._id

  def as_dict(self):
    base = { "@id" : self.id }
    if self.element:
      base["@bpmnElement"] = self.element.id
      shapes = [ Shape(element).as_dict()["bpmndi:BPMNShape"] for element in self.element.elements ]
      if shapes:
        base["bpmndi:BPMNShape"] = prune(shapes)
      edges = [ Edge(flow).as_dict()["bpmndi:BPMNEdge"] for flow in self.element.flows ]
      if edges:
        base["bpmndi:BPMNEdge"] = prune(edges)
    return { "bpmndi:BPMNPlane" : base }

class Diagram():
  def __init__(self, id="diagram", plane=None):
    self.id      = id
    self.plane   = plane if plane else Plane()

  def as_dict(self):
    base = { "@id" : self.id }
    base.update(self.plane.as_dict())
    return { "bpmndi:BPMNDiagram" : base }
