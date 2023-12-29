"""
  A simple lay-out-er.
  Supports processes looking like: 
    start -> task (-> task)* -> end
"""

import logging

import json

from bpmn_tools.flow          import Process, Start, End
from bpmn_tools.flow          import IntermediateCatch, IntermediateThrow
from bpmn_tools.flow          import Tasks, Gateways
from bpmn_tools.collaboration import Participant
from bpmn_tools.visitor       import Visitor, visiting

logger = logging.getLogger(__name__)

class LayoutVisitor(Visitor):
  def __init__(self):
    super().__init__()
    self.processes = {}
    self.process_participant = {}
    self._current_process = None
  
  def analyze(self, model):
    model.accept(self)
    logger.debug(json.dumps(self.processes, indent=2, default=str))
    return self
    
  @visiting(Process)
  def visit(self, process): # noqa
    logger.info(f"detecting elements in process: {process}")
    self.current_process = process

  @visiting(Participant) 
  def visit(self, participant): # noqa
    logger.info(f"found participant: {participant}")
    self.process_participant[participant.process.id] = participant
  
  @visiting(Start)
  def visit(self, event): # noqa
    self.current_process["start"] = event
    self._analyse_element(event)

  @visiting(IntermediateThrow, IntermediateCatch)
  def visit(self, event): # noqa
    self._analyse_element(event)

  @visiting(End)
  def visit(self, event): # noqa
    self.current_process["end"] = event
    self._analyse_element (event)

  @visiting(*Tasks)
  def visit(self, task): # noqa
    self._analyse_element(task)

  @visiting(*Gateways)
  def visit(self, gateway): # noqa
    self._analyse_element(gateway)

  @property
  def current_process(self):
    return self.processes[self._current_process.id]

  @current_process.setter
  def current_process(self, process):
    self._current_process = process
    if self._current_process.id not in self.processes:
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
    """ # noqa
    START   = 160
    HEADER  = 30
    PADDING = 25
    SPACING = 30

    top = 80
    for process, analysis in self.processes.items():
      left = START
      self.process_participant[process].x = left
      self.process_participant[process].y = top

      if analysis["process"].laneset.lanes:
        lanes_height = 0
        for lane in analysis["process"].laneset.lanes:
          lane.x = left + HEADER
          lane.y = top + lanes_height
          lanes_height += lane.height
        self.process_participant[process].height = lanes_height
      else:
        pass

      left += HEADER + PADDING
      top += PADDING

      for step in self._order(analysis):
        step.x = left
        lane = analysis["process"].laneset.lane_of(step)
        if lane:
          step.y = PADDING + lane.y + (analysis["height"]-step.height) / 2
        else:
          step.y = top + (analysis["height"]-step.height) / 2
        left += step.width + SPACING

      width = left - START
      self.process_participant[process].width = width
      for lane in analysis["process"].laneset.lanes:
        lane.width  = width - HEADER
      top += self.process_participant[process].height

  def _order(self, analysis):
    """
    yield all elements in order:
      - start with any start element and recurse
      - loop over _all_ elements and recurse
      - only yielding each element once
    """
    handled = []
    def recurse(step):
      nonlocal handled
      if step in handled:
          return
      handled.append(step)
      yield step
      for next_step in analysis["steps"][step.id]:
        try:
          yield from recurse(analysis["elements"][next_step])
        except KeyError:
          pass

    # give priority to start-driven processes
    if analysis["start"]:
      yield from recurse(analysis["start"])

    # re-iterate all elements to cover loose ends
    for element in analysis["elements"].values():
      yield from recurse(element)

def layout(model):
  LayoutVisitor().analyze(model).layout()
