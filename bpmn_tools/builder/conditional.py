"""

the conditional builder allows for defining a process as a sequence of tasks, 
each with a number of conditions that should be met before executing the task

the builder can construct a process flow, using the process builder, that
represents a flow diagram for that sequence of tasks with branching gates for
all conditions.

"""

import logging

from dataclasses import dataclass, field
from typing import List, Type, Union, Callable

from bpmn_tools.builder import process
from bpmn_tools import flow

logger = logging.getLogger(__name__)

ConditionKind = process.BranchKind

@dataclass
class Condition():
  name  : str
  kind  : ConditionKind = ConditionKind.XOR

  def __eq__(self, other):
    return self.name == other.name and self.kind == other.kind

  def __str__(self):
    return f"{self.name}({self.kind.name})"

@dataclass
class ConditionSet():
  conditions : List[Condition] = field(default_factory=list)
  values     : List[List[str]] = field(default_factory=list)

  def __post_init__(self):
    for values in self.values:
      if len(values) != len(self.conditions):
        raise ValueError("each set of values should a value for each condition")

  def prune(self):
    # if all first values of a condition are None, it can be pruned  
    needs_pruning = True
    while needs_pruning:
      if not self.values:
        needs_pruning = False
      for values in self.values:
        if not values or values[0] is not None:
          needs_pruning = False
      if needs_pruning:
        self.conditions = self.conditions[1:]
        for index, values in enumerate(self.values):
          self.values[index] = values[1:]

  def __len__(self):
    return len(self.conditions)

  def __bool__(self):
    return len(self.conditions) > 0

  def __getitem__(self, index):
    return self.conditions[0]

  @property
  def first_non_none_values(self):
    return [
      values[0] for values in self.values if values[0] is not None
    ]

  def with_value(self, value):
    """
    return a clone with only value-sets of which the first value matches "value"
    """
    return ConditionSet(
      self.conditions.copy(),
      [ values for values in self.values if values[0] == value or values[0] is None ]
    )

  def without_first(self):
    """
    return a clone without first condition and its values
    """
    return ConditionSet(
      self.conditions[1:],
      [ values[1:] for values in self.values ]
    )

@dataclass
class Item():
  name       : str
  conditions : ConditionSet = field(default_factory=ConditionSet)
  cls        : Type[flow.Task] = flow.Task
  boundary   : Type[flow.EventDefinition] = None
  id         : Union[str, Callable] = None

  def to_dict(self):
    return self.name

  def to_process(self):
    return process.Task(
      name=self.name,
      id=self.id,
      cls=self.cls,
      boundary=self.boundary
    )

  def __eq__(self, other):
    return self.name == other.name

  def copy(self):
    return Item(self.name, self.conditions, self.cls, self.boundary, self.id)

  def with_value(self, value):
    item = self.copy()
    item.conditions = self.conditions.with_value(value)
    return item

  def without_first_condition(self):
    item = self.copy()
    item.conditions = self.conditions.without_first()
    return item

@dataclass
class Sequence():
  items : List[Item] = field(default_factory=list)
  
  def to_dict(self):
    return [ item.to_dict() for item in self.items ]

  def to_process(self, **kwargs):
    return process.Process([ item.to_process() for item in self.items ], **kwargs)

  def __eq__(self, other):
    try:
      return len(self.items) == len(other.items) and \
             all([ left == right for left, right in zip(self.items,other.items) ])
    except AttributeError:
      return False

  def __len__(self):
    return len(self.items)
  
  def __getitem__(self, index):
    return self.items[index]
  
  def append(self, item):
    self.items.append(item)

  def expand(self, *items):
    """
    takes a list of items and returns a list of expanded items
    items without conditions are simply returned
    items with conditions are wrapped in branches
    """
    self.items      = []          # reset
    items           = list(items) # ensure list
    prev_first_item = None        # track progress (avoid endless loop ;-))

    # prune all items' conditions -> remove all None-conditions up to first 
    # actual condition
    for item in items:
      item.conditions.prune()

    logger.debug(f"creating sequence from {[item.name for item in items]}")
    while len(items) and items[0] is not prev_first_item:
      prev_first_item = items[0]

      # simply add condition-less items without further expansion
      while len(items) and not len(items[0].conditions):
        logger.debug(f"adding {items[0].name} to sequence")
        self.append(items.pop(0))
      
      # we encountered an item with a condition
      # collect leading sub-list of items that have the same first condition
      # and create a BranchedItem from them
      if len(items):
        branched_item  = BranchedItem(items[0].conditions[0])
        branched_items = []
        
        while len(items) and items[0].conditions \
              and items[0].conditions[0].name == branched_item.name \
              and items[0].conditions.first_non_none_values:
          branched_items.append(items.pop(0))
        branched_item.expand(*branched_items)
        self.append(branched_item)
    return self

@dataclass
class Branch():
  value : tuple
  sequence : Sequence = field(default_factory=list)

  def to_dict(self):
    return { ','.join(map(str,self.value)) : self.sequence.to_dict() }

  def to_process(self):
    return process.If(','.join(map(str,self.value)), self.sequence.to_process())

  def __eq__(self, other):
    return self.value == other.value and self.sequence == other.sequence

  def expand(self, *items):
    # only accept items with our condition
    for item in items:
      for values in item.conditions.values:
        if values[0] not in self.value and values[0] is not None:
          raise ValueError(f"{self.value} != {values[0]}")
    # create a sequence for the items, without the first condition, which 
    # already brought us here (condition reduction up to no conditions left)
    items = [ item.without_first_condition() for item in items ]
    self.sequence = Sequence().expand(*items)

@dataclass
class BranchedItem():
  condition : Condition
  branches  : List[Branch] = field(default_factory=list)

  @property
  def name(self):
    return self.condition.name

  def to_dict(self):
    return {
      str(self.condition) : [ branch.to_dict() for branch in self.branches ]
    }

  def to_process(self):
    return process.Branch(
      [ branch.to_process() for branch in self.branches ],
      label=self.condition.name,
      kind=self.condition.kind,
      default=self.condition.kind == ConditionKind.XOR
    )

  def __eq__(self, other):
    return self.condition == other.condition and \
           all([ left == right for left, right in zip(self.branches, other.branches) ])

  def __len__(self):
    return len(self.branches)
  
  def __getitem__(self, index):
    return self.branches[index]

  def expand(self, *items):
    """
    create branch for each condition-value
    expand matching items into branch
    """
    # only accept items with our condition
    for item in items:
      if item.conditions[0].name != self.name:
        raise ValueError(f"{self} only accepts items with condition {self.name}")

    logger.debug(f"creating branched item for {self.condition.name} from {[item.name for item in items]}")
    # create a set of the possible values for conditions
    values = sorted(set([
      values[0] for item in items for values in item.conditions.values 
      if values[0] is not None
    ]))
    logger.debug(f"  with possible branch values: {values}")

    # create branches for each possible value
    for value in values:
      branch = Branch((value,))
      branch_items = []
      for item in items:
        branch_item = item.with_value(value)
        if branch_item.conditions.values:
          branch_items.append(branch_item)
      logger.debug(f"    - {value} : {[ item.name for item in branch_items ]}")
      branch.expand(*branch_items)
      self.branches.append(branch)

    # collapse branches that are the same (except for their value)
    collapsed_branches = []
    for index, branch in enumerate(self.branches):
      if index not in collapsed_branches:
        for other_index, other_branch in enumerate(self.branches[index+1:]):
          if branch != other_branch:
            if branch.sequence == other_branch.sequence:
              collapsed_branches.append(index+other_index+1)
              branch.value = branch.value + other_branch.value
    self.branches = [
      branch for index, branch in enumerate(self.branches)
      if index not in collapsed_branches
    ]
