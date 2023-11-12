"""

Process builder builds single-process, forward branching-flow-like structures:


                           | -> [ Task ] ------------------- |
  S -> [ Task ] -> < Branch >                               < > -> [ Task ] -> S
                           | -> < Branch > ----------- < > - | 
                                        | -> [ Task ] - |   
""" 

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Type

from bpmn_tools import flow

from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.notation      import Definitions
from bpmn_tools.colors        import Red, Green, Orange, Blue

"""

TODO
 - [ ] labels

"""

PADDING = 20

def NoColor(bpmn):
  return bpmn

class Color(Enum):
  NONE   : NoColor
  RED    : Red
  GREEN  : Green
  ORANGE : Orange
  BLUE   : Blue

@dataclass
class Step():
  label   : str   = None
  # color   : Color = NoColor
  
  @property
  def height(self):
    raise NotImplementedError

  @property
  def width(self):
    raise NotImplementedError

  def render(self, x=0, y=0):
    raise NotImplementedError

tasks = 0

@dataclass
class Task(Step):
  name  : str = ""
  cls   : Type[flow.Task] = flow.Task
  args  : Dict = field(default_factory=dict)
  
  def __post_init__(self):
    global tasks
    self.args["name"] = self.name
    self.element = self.cls(id=f"task_{tasks}", **self.args)
    tasks += 1
  
  @property
  def height(self):
    return self.element.height + PADDING * 2

  @property
  def width(self):
    return self.element.width + PADDING * 2

  def render(self, x=0, y=0):
    self.element.x = x + PADDING
    self.element.y = y + PADDING
    return ( [ self.element ], [] )
    
  @property
  def root(self):
    return self.element

  @property
  def tail(self):
    return self.element

def connect(source, target):
  return flow.Flow(id=f"flow_{source.id}_{target.id}", source=source, target=target)

@dataclass
class Process(Step):
  name   : str  = ""
  starts : bool = False
  ends  : bool = False
  steps  : List[Step] = field(default_factory=list)

  def __post_init__(self):
    if self.starts:
      self._root = flow.Start(id="start")
    if self.ends:
      self._tail = flow.End(id="end")

  def add(self, step):
    self.steps.append(step)
    return self

  @property
  def height(self):
    return max([ step.height for step in self.steps ])

  @property
  def width(self):
    total_width = sum([ step.width for step in self.steps ])
    if self.starts:
      total_width += self.root.width
    if self.ends:
      total_width += self.tail.width
    return total_width 

  def render(self, x=None, y=None):
    # if we're called without positioning, we're adding diagram boilerplate
    wrap = x is None or y is None
    if wrap:
      x = 50 # header of participant
      y = 0
    
    shapes = []
    flows  = []
    prev = None

    # add optional start event
    if self.starts:
      self.root.x = x
      x += self.root.width
      self.root.y = y + int(self.steps[0].height/2) - int(self.root.height/2)
      shapes.append(self.root)

    # add steps
    for step in self.steps:
      more_shapes, more_flows = step.render(x=x, y=y)
      shapes.extend(more_shapes)
      flows.extend(more_flows)
      x += step.width
      if prev:
        flows.append(connect(source=prev.tail, target=step.root))
      else:
        flows.append(connect(source=self.root, target=step.root))        
      prev = step

    # add optional end event
    if self.ends:
      self.tail.x = x
      self.tail.y = self.root.y
      shapes.append(self.tail)
      flows.append(connect(source=shapes[-2], target=self.tail))

    # optinally wrap it all
    if wrap:
      process = flow.Process(id="process").extend(shapes).extend(flows)
      participant = Participant(self.name, process, id="participant")
      # participant shapes the lane
      participant.x = 0
      participant.y = 0
      participant.width  = self.width + 50 + PADDING
      participant.height = self.height
      collaboration = Collaboration(id="collaboration").append(participant)
      return Definitions(id="definitions").extend([
        process,
        collaboration,
        Diagram(
          id="diagram",
          plane=Plane(id="plane", element=collaboration)
        )
      ])
    return (shapes, flows)

  @property
  def root(self):
    if self._root:
      return self._root
    return self.steps[0].root

  @property
  def tail(self):
    if self._tail:
      return self._tail
    return self.steps[-1].tail

class BranchKind(Enum):
  XOR = flow.ExclusiveGateway
  OR  = flow.InclusiveGateway
  AND = flow.ParallelGateway

gws = 0

@dataclass
class Branch(Step):
  default  : str = None
  kind     : BranchKind = BranchKind.XOR
  branches : List[Step] = field(default_factory=list)

  def __post_init__(self):
    global gws
    self.root = self.kind.value(id=f"gateway_start_{gws}")
    self.tail = self.kind.value(id=f"gateway_end_{gws}")
    gws += 1

  def add(self, branch):
    self.branches.append(branch)
    return self

  @property
  def height(self):
    return sum([ branch.height for branch in self.branches ])

  @property
  def width(self):
    return max([ branch.width for branch in self.branches ]) + self.root.width + self.tail.width

  def render(self, x=0, y=0):
    shapes = []
    flows  = []
    self.root.x = x
    self.root.y = y + int(self.branches[0].height/2) - (self.root.height/2)
    shapes.append(self.root)
    shapes.append(self.tail)
    self.tail.x = x + self.width - self.tail.width
    self.tail.y = self.root.y
    x += self.root.width
    for branch in self.branches:
      more_shapes, more_flows = branch.render(x=x, y=y)
      shapes.extend(more_shapes)
      flows.extend(more_flows)
      y += branch.height
      flows.append(connect(source=self.root,   target=branch.root))
      flows.append(connect(source=branch.tail, target=self.tail))
    return shapes, flows
