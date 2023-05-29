"""
  A simple lay-out-er.
  Supports processes looking like: 
    start -> task (-> task)* -> end
"""

import logging
logger = logging.getLogger(__name__)

import json

from bpmn_tools.flow          import Process, Start, End, Task
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

  @visiting(Task)
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
        "start"       : None,
        "elements"    : {},
        "end"         : None
      }

  def _analyse_element(self, element):
    logger.info(f"analysing element: {element}")
    if element.outgoing:
      self.current_process["elements"][element.id] = [
        outgoing.target for outgoing in element.outgoing
      ]

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
      left += HEADER + PADDING
      max_heigth = max([step[0].height for step in analysis["elements"].values()])
      top += PADDING
      for step in self._order(analysis):
        step.x = left
        step.y = top + (max_heigth-step.height) / 2
        left += step.width + SPACING
      self.process_participant[process].width = left - START

  def _order(self, analysis):
    step = analysis["start"]
    end  = analysis["end"]
    yield step
    while step != end:
      step = analysis["elements"][step.id][0]
      yield step

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
  logger.debug(json.dumps(visitor.report, indent=2, default=str))
  visitor.layout()
