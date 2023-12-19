"""

the conditional builder allows for defining a process as a sequence of tasks, 
each with a number of conditions that should be met before executing the task

the builder can construct a process flow, using the process builder, that
represents a flow diagram for that sequence of tasks with branching gates for
all conditions.

"""

import logging

from dataclasses import dataclass, field
from typing import List

from bpmn_tools.builder.process import BranchKind

logger = logging.getLogger(__name__)

ConditionKind = BranchKind

@dataclass
class Condition():
  name  : str
  kind  : ConditionKind = ConditionKind.XOR

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

  def __len__(self):
    return len(self.conditions)

  def __bool__(self):
    return len(self.conditions) > 0

  def __getitem__(self, index):
    return self.conditions[0]

  def with_value(self, value):
    """
    return a clone with only value-sets of which the first value matches "value"
    or is None (meaning we don't care, so it matches everything)
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

  def to_dict(self):
    return self.name

  def with_value(self, value):
    return Item(
      self.name,
      self.conditions.with_value(value)
    )

  def without_first_condition(self):
    return Item(
      self.name,
      self.conditions.without_first()
    )

@dataclass
class Sequence():
  items : List[Item] = field(default_factory=list)
  
  def to_dict(self):
    return [ item.to_dict() for item in self.items ]
    
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

    while len(items) and items[0] is not prev_first_item:
      prev_first_item = items[0]

      # simply add condition-less items without further expansion
      while len(items) and len(items[0].conditions) == 0:
        self.append(items.pop(0))

      # we encountered an item with conditions
      # collect leading sub-list of items that have the same first conditionname
      # and create a BranchedItem from them
      if len(items):
        branched_item  = BranchedItem(items[0].conditions[0])
        branched_items = []
        while len(items) and items[0].conditions \
              and items[0].conditions[0].name == branched_item.name:
          branched_items.append(items.pop(0))
        branched_item.expand(*branched_items)
        self.append(branched_item)
  
    if len(items):
      raise ValueError(f"could not process all items. remaining: {items}")

    return self

@dataclass
class Branch():
  value : str
  sequence : Sequence = field(default_factory=list)

  def to_dict(self):
    return { self.value : self.sequence.to_dict() }

  def __len__(self):
    return len(self.sequence)

  def expand(self, *items):
    # only accept items with our condition
    for item in items:
      for values in item.conditions.values:
        if values[0] != self.value and values[0] is not None:
          raise ValueError(f"{self.value} != {values[0]}")
    # create a sequence for the items, without the first condition, which 
    # already brought us here (condition reduction up to no conditions left)
    self.sequence = Sequence().expand(
      *[ item.without_first_condition() for item in items ]
    )

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

    # create a set of the possible values for conditions
    values = sorted(set([
      values[0] for item in items for values in item.conditions.values 
      if values[0] is not None
    ]))
    # create branches for each possible value
    for value in values:
      branch = Branch(value)
      branch_items = []
      for item in items:
        branch_item = item.with_value(value)
        if branch_item.conditions.values:
          branch_items.append(branch_item)
      branch.expand(*branch_items)
      self.branches.append(branch)
