"""

Process builder builds single-process, forward branching-flow-like structures:


                           | -> [ Task ] ------------------- |
  S -> [ Task ] -> < Branch >                               < > -> [ Task ] -> S
                           | -> < Branch > ----------- < > - | 
                                        | -> [ Task ] - |   
""" 

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Type, Union, Callable

from bpmn_tools import flow

from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.notation      import Definitions
from bpmn_tools.colors        import Red, Green, Orange, Blue

from bpmn_tools.util import slugify

PADDING               =  10
FLOW_SPACE            =  20
MODEL_OFFSET_X        = 150
MODEL_OFFSET_Y        =  80
DEFAULT_BRANCH_HEIGHT =  75
STANDARD_TASK_HEIGHT  =  80

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
  children: List["Step"] = field(default_factory=list)
  label   : str   = None
  color   : Color = NoColor
  
  @property
  def height(self):
    raise NotImplementedError # pragma: no cover

  @property
  def width(self):
    raise NotImplementedError # pragma: no cover

  def render(self, x=0, y=0):
    raise NotImplementedError # pragma: no cover

  def shape(self, cls, **kwargs):
    return self.color(cls(**kwargs))

@dataclass
class Task(Step):
  name    : str = ""
  cls     : Type[flow.Task] = flow.Task
  args    : Dict = field(default_factory=dict)
  boundary: Type[flow.EventDefinition] = None
  id      : Union[str, Callable] = None
  _id     : Union[str, Callable] = field(init=False, repr=False, default=None)
  _std_id : str = field(init=False, repr=False, default=None)

  tasks = 0 # class

  @classmethod
  def reset(cls):
    cls.tasks = 0

  @property
  def id(self):
    if self._id:
      if callable(self._id):
        return self._id(self._std_id)
      else:
        return self._id
    return self._std_id
  
  @id.setter
  def id(self, new_id):
    # courtesy: https://stackoverflow.com/a/61480946
    if type(new_id) is property:
      # initial value not specified, use default
      new_id = Task._id
    self._id = new_id

  def __post_init__(self):
    self.args["name"] = self.name
    self._std_id = f"task_{self.tasks}"
    self.__class__.tasks += 1
    self.element = self.shape(self.cls, id=self.id, **self.args)
  
  @property
  def height(self):
    return self.element.height + PADDING * 2

  @property
  def width(self):
    return self.element.width + PADDING * 2

  def render(self, x=0, y=0):
    self.element.x = x + PADDING
    self.element.y = y + PADDING
    shapes = [ self.element ]
    if self.boundary:
      shapes.append(flow.BoundaryEvent(
        id=f"boundary-event-{self.element.id}",
        definition=self.boundary(id=f"{slugify(self.boundary.__name__)}-{self.element.id}"),
        on=self.element
      ))
    return (shapes, [])

  @property
  def root(self):
    return self.element

  @property
  def tail(self):
    return self.element

def connect(source, target, label=None):
  if source == target:
    raise ValueError("connect: {source} == {target}")
  return flow.Flow(id=f"flow_{source.id}_{target.id}", source=source, target=target, name=label)

@dataclass
class Process(Step):
  name   : str  = ""
  starts : bool = False
  ends   : bool = False
  _root  = None
  _tail  = None

  def __post_init__(self):
    if self.starts:
      self._root = self.shape(flow.Start, id="start")
    if self.ends:
      self._tail = self.shape(flow.End, id="end")

  def add(self, step):
    self.children.append(step)
    return self

  def extend(self, steps):
    for step in steps:
      self.add(step)
    return self

  @property
  def height(self):
    return max([ step.height for step in self.children ])

  @property
  def width(self):
    total_width = sum([ step.width for step in self.children ])
    total_width += FLOW_SPACE * (len(self.children) - 1)
    if self.starts:
      total_width += self.root.width + FLOW_SPACE
    if self.ends:
      total_width += self.tail.width + FLOW_SPACE
    return total_width 

  def render(self, x=None, y=None):
    # if we're called without positioning, we're adding diagram boilerplate
    wrap = x is None or y is None
    if wrap:
      x = 50 + MODEL_OFFSET_X # header of participant
      y = 0  + MODEL_OFFSET_Y
    
    shapes = []
    flows  = []
    prev = None

    # add optional start event
    if self.starts:
      self.root.x = x
      x += self.root.width
      self.root.y = y + int((STANDARD_TASK_HEIGHT + PADDING * 2)/2) - (self.root.height/2)
      shapes.append(self.root)
      x += FLOW_SPACE

    # add steps
    for step in self.children:
      more_shapes, more_flows = step.render(x=x, y=y)
      shapes.extend(more_shapes)
      flows.extend(more_flows)
      x += step.width + FLOW_SPACE
      if prev:
        flows.append(connect(source=prev.tail, target=step.root))
      elif self.starts:
        flows.append(connect(source=self.root, target=step.root))
      prev = step

    # add optional end event
    if self.ends:
      shapes.append(self.tail)
      # attach to tail of last child
      last_shape = self.children[-1].tail
      self.tail.x = x
      self.tail.y = last_shape.y + (last_shape.height/2) - (self.tail.height/2)
      # add flow to end
      flows.append(connect(source=last_shape, target=self.tail))

    # optinally wrap it all
    if wrap:
      process = flow.Process(id="process").extend(shapes).extend(flows)
      participant = Participant(self.name, process, id="participant")
      # participant shapes the lane
      participant.x = MODEL_OFFSET_X
      participant.y = MODEL_OFFSET_Y
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
    return self.children[0].root

  @property
  def tail(self):
    if self._tail:
      return self._tail
    return self.children[-1].tail

class BranchKind(Enum):
  XOR = flow.ExclusiveGateway
  OR  = flow.InclusiveGateway
  AND = flow.ParallelGateway

# utility wrapper for an even more fluid API ;-)
def If(condition, step):
  return (step, condition)

@dataclass
class Branch(Step):
  default  : str = None
  kind     : BranchKind = BranchKind.XOR

  gws = 0

  def __post_init__(self):
    global gws
    self.root = self.shape(self.kind.value, id=f"gateway_start_{self.gws}", name=self.label)
    self.tail = self.shape(self.kind.value, id=f"gateway_end_{self.gws}")
    self.__class__.gws += 1
    # ensure all children to ensure they are tuples
    self.children = list(map(lambda c: c if type(c) is tuple else (c,None), self.children))

  @classmethod
  def reset(cls):
    cls.gws = 0

  def add(self, branch, condition=None):
    self.children.append((branch, condition))
    return self

  @property
  def height(self):
    total_height = sum([ branch.height for branch, _ in self.children ])
    if self.default:
      total_height += DEFAULT_BRANCH_HEIGHT
    return total_height

  @property
  def width(self):
    total_width = max([ branch.width for branch, _ in self.children ])
    total_width += self.root.width + self.tail.width
    total_width += FLOW_SPACE * 2
    return total_width

  def render(self, x=0, y=0):
    shapes = []
    flows  = []
    self.root.x = x
    self.root.y = y + int((STANDARD_TASK_HEIGHT + PADDING * 2)/2) - (self.root.height/2)
    shapes.append(self.root)
    shapes.append(self.tail)
    x += FLOW_SPACE
    if self.default:
      flows.append(connect(source=self.root, target=self.tail))
      y += DEFAULT_BRANCH_HEIGHT
    self.tail.x = x + self.width - self.tail.width - FLOW_SPACE
    self.tail.y = self.root.y
    x += self.root.width
    for branch, condition in self.children:
      more_shapes, more_flows = branch.render(x=x, y=y)
      shapes.extend(more_shapes)
      flows.extend(more_flows)
      y += branch.height
      flows.append(connect(source=self.root,   target=branch.root, label=condition))
      flows.append(connect(source=branch.tail, target=self.tail))
    return shapes, flows
