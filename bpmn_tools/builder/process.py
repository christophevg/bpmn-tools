"""

Process builder builds single-process, forward branching-flow-like structures:


                           | -> [ Task ] ------------------- |
  S -> [ Task ] -> < Branch >                               < > -> [ Task ] -> S
                           | -> < Branch > ----------- < > - | 
                                        | -> [ Task ] - |   
""" 

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from bpmn_tools.builder import Builder

@dataclass
class Step(Builder):
  label : str = None

  @property
  def height(self):
    raise NotImplementedError

@dataclass
class Task(Step):
  name : str = ""

@dataclass
class Process(Step):
  starts : bool = False
  stops  : bool = False
  steps  : List[Step] = field(default_factory=list)
  
  @property
  def height(self):
    return max([ step.height for step in self.steps ])

  def add(self, step):
    self.steps.append(step)
    return self

class BranchKind(Enum):
  OR  = "inclusive"
  XOR = "exclusive"
  AND = "parallel"

@dataclass
class Branch(Step):
  default  : str = None
  kind     : BranchKind = BranchKind.XOR
  branches : List[Step] = field(default_factory=list)

  def add(self, branch):
    self.branches.append(branch)
    return self
