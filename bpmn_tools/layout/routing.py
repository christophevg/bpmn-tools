import logging

import math

from bpmn_tools.flow import Gateway, Flow

from bpmn_tools import xml

logger = logging.getLogger(__name__)

class WayPoint(xml.Element):
  __tag__ = "di:waypoint"
  
  def __init__(self, x=0, y=0):
    super().__init__()
    self["x"] = str(int(x))
    self["y"] = str(int(y))

  @property
  def x(self):
    return int(self["x"])

  @property
  def y(self):
    return int(self["y"])

  @property
  def xy(self):
    return (self.x, self.y)

class Routable():
  def __init__(self, element=None):
    self.element = element

  @property
  def left(self):
    return self.element.x

  @property
  def center(self):
    return self.element.x + int(self.element.width/2)

  @property
  def right(self):
    return self.element.x + self.element.width

  @property
  def top(self):
    return self.element.y

  @property
  def middle(self):
    return self.element.y + int(self.element.height/2)

  @property
  def bottom(self):
    return self.element.y + self.element.height
  
  @property
  def north(self):
    return WayPoint(x=self.center, y=self.top)

  @property
  def east(self):
    return WayPoint(x=self.right, y=self.middle)

  @property
  def south(self):
    return WayPoint(x=self.center, y=self.bottom)

  @property
  def west(self):
    return WayPoint(x=self.left, y=self.middle)

  @property
  def gates(self):
    return [ self.north, self.east, self.south, self.west ]

class EdgeRoutingStrategy():
  """
  Base class for Edge Routing Strategies. Holds several routing supporting
  functions.
  """
  def __init__(self, flow=None):
    self.source = None
    self.target = None
    self.flow   = None
    self.given(flow)
    
  def given(self, new_flow=None):
    self.flow = new_flow
    if self.flow:
      self.source = Routable(self.flow.source)
      self.target = Routable(self.flow.target)
    return self

class Direct(EdgeRoutingStrategy):
  def route(self, flow):
    """
    slightly brute-force approach, computing distance between all src/trg gates
    selecting the shortest
    """
    self.given(flow)
    _, src, trg = min([
      ( math.dist(src.xy, trg.xy), src, trg )
      for src in self.source.gates
      for trg in self.target.gates
    ], key=lambda p: p[0])
    return [ src, trg ]

class Default(EdgeRoutingStrategy):
  """
  Default Edge Routing distinguishes between activities and gateways.
  Activities routes from side to side, while gateways are routed bottom to top
  
  TODO: reuse EdgeRoutingStrategy Routables
  """
  def route(self, flow):
    if isinstance(flow.source, Flow):
      logger.warning(f"routing is not supported for source Flow: {flow}")
      return []
    if isinstance(flow.target, Flow):
      logger.warning(f"routing is not supported for targer Flow: {flow}")
      return []
    self.given(flow)
    if isinstance(self.flow.source, Gateway) or isinstance(self.flow.target, Gateway):
      return self._route_gateway()
    return self._route_default()
  
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
      Gateway routing routes directly from the right/middle exit of the source
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