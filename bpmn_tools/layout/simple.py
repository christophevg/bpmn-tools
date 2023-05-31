"""
  A simple lay-out-er.
  Supports processes looking like: 
    start -> task (-> task)* -> end
"""

import logging
logger = logging.getLogger(__name__)

import json

from bpmn_tools.flow          import Process, Start, End
from bpmn_tools.flow          import Task, UserTask, ServiceTask, ScriptTask
from bpmn_tools.collaboration import Participant
from bpmn_tools.visitor       import Visitor, visiting

class LayoutVisitor(Visitor):
  def __init__(self):
    super().__init__()
    self.processes = {}
    self.process_participant = {}
    self._current_process = None
  
  def analyze(self, model):
    model.accept(self)
    return self
    
  @visiting(Process)
  def visit(self, process):
    logger.info(f"detecting elements in process: {process}")
    self.current_process = process

  @visiting(Participant)
  def visit(self, participant):
    logger.info(f"found participant: {participant}")
    self.process_participant[participant.process.id] = participant
  
  @visiting(Start)
  def visit(self, event):
    self.current_process["start"] = event
    self._analyse_element(event)

  @visiting(End)
  def visit(self, event):
    self.current_process["end"] = event
    self._analyse_element (event)

  @visiting(Task, UserTask, ServiceTask, ScriptTask)
  def visit(self, task):
    self._analyse_element(task)

  @property
  def current_process(self):
    return self.processes[self._current_process.id]

  @current_process.setter
  def current_process(self, process):
    self._current_process = process
    if not self._current_process.id in self.processes:
      self.processes[self._current_process.id] = {
        "process"     : self._current_process,
        "height"      : 0,
        "elements"    : {},
        "start"       : None,
        "steps"       : {},
        "end"         : None
      }

  def _analyse_element(self, element):
    # keep index of all elements
    self.current_process["elements"][element.id] = element
    # record steps
    self.current_process["steps"][element.id] = [
      outgoing.target.id for outgoing in element.outgoing
    ]
    # track heighest element
    self.current_process["height"] = max([
      self.current_process["height"],
      element.height
    ])

  def layout(self):
    """
      start -> task (-> task)* -> end

      participant(x,y) = 160,80
      start(x,y) = (160+15+25,                     80+25+((80-36)/2)  (width,height=36)
      task(x,y)  = (160+15+25+36+50,               80+25)             (width=100, height=80)
      task(x,y)  = (160+15+25+36+50+100+50,        80+25)             (width=100, height=80)
      start(x,y) = (160+15+25+36+50+100+50+100+50, 80+25+((80-36)/2)  (width,height=36)
    """
    START   = 160
    HEADER  = 30
    PADDING = 25
    SPACING = 30

    top = 80
    for process, analysis in self.processes.items():
      left = START
      self.process_participant[process].x = left
      self.process_participant[process].y = top
      for lane in analysis["process"].laneset.lanes:
        lane.x = left + HEADER
        lane.y = top
        
      left += HEADER + PADDING
      top += PADDING
      for step in self._order(analysis):
        step.x = left
        step.y = top + (analysis["height"]-step.height) / 2
        left += step.width + SPACING
      width = left - START
      self.process_participant[process].width = width
      for lane in analysis["process"].laneset.lanes:
        lane.width  = width - HEADER
      top += self.process_participant[process].height

  def _order(self, analysis):
    if analysis["start"] and analysis["end"]:
      # follow from start to end
      step = analysis["start"]
      end  = analysis["end"]
      yield step
      while step != end:
        step = analysis["elements"][analysis["steps"][step.id][0]]
        yield step
    else:
      # just return the elements
      if analysis["start"]:
        yield analysis["start"]
      for element in analysis["elements"].values():
        yield element
      if analysis["end"]:
        yield analysis["end"]

  @property
  def report(self):
    return self.processes
    return {
      process : list(self._order(analysis)) \
      for process, analysis in self.processes.items()
    }

def layout(model):
  visitor = LayoutVisitor()
  
  visitor.analyze(model)
  # print(json.dumps(visitor.report, indent=2, default=str))
  logger.debug(json.dumps(visitor.report, indent=2, default=str))
  visitor.layout()
