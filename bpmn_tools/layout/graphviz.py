"""
  A lay-out-er that uses Graphviz as a layout engine to layout activities in a
  process. If multiple processes are part of the model, each is laid out.
"""
 
import logging
 
import json
 
import graphviz
 
from bpmn_tools.flow          import Process
from bpmn_tools.flow          import Tasks
from bpmn_tools.collaboration import Participant

from bpmn_tools.visitor       import Visitor, visiting

from bpmn_tools.layout        import routing
 
logger = logging.getLogger(__name__)
 
class LayoutVisitor(Visitor):
  def __init__(self, g=None):
    super().__init__()
    self.processes = {}
    self.process_participant = {}
    self._current_process = None
    self.g = g if g else graphviz.Graph("", engine="sfdp", graph_attr={"repulsiveforce" : "10"})
 
  def analyze(self, model):
    model.accept(self)
    logger.debug(json.dumps(self.processes, indent=2, default=str))
    return self
   
  @visiting(Process)
  def visit(self, process): # noqa
    logger.debug(f"detecting elements in process: {process}")
    self.current_process = process
 
  @visiting(Participant)
  def visit(self, participant): # noqa
    logger.debug(f"found participant: {participant}")
    self.process_participant[participant.process.id] = participant
 
  @visiting(*Tasks)
  def visit(self, task): # noqa
    self._analyse_element(task)
 
  @property
  def current_process(self):
    return self.processes[self._current_process.id]
 
  @current_process.setter
  def current_process(self, process):
    self._current_process = process
    if self._current_process.id not in self.processes:
      self.processes[self._current_process.id] = {
        "process"      : self._current_process,
        "elements"     : {},
        "interactions" : []
      }
 
  def _analyse_element(self, element):
    self.current_process["elements"][element.id] = element
    self.current_process["interactions"].extend([
      (element.id, outgoing.target.id) for outgoing in element.outgoing
    ])
 
  def layout(self):
    START   = 160
    HEADER  = 30
    PADDING = 25
    SPACING = 30
 
    top = 80
    for process_id, analysis in self.processes.items():
      # apply process positions
      self.process_participant[process_id].x = START
      self.process_participant[process_id].y = top
 
      # activity offsets
      left = START + HEADER + PADDING
      top += PADDING
 
      positions = self._make_gv(analysis)
      logger.debug(json.dumps(positions, indent=2, default=str))
     
      width  = 0
      height = 0
      for element_id, x, y in positions:
        width  = max([width, x + analysis["elements"][element_id].width])
        height = max([height, y + analysis["elements"][element_id].height])
        analysis["elements"][element_id].x = x + left
        analysis["elements"][element_id].y = y + top
 
      self.process_participant[process_id].width  = width + HEADER + PADDING * 2
      self.process_participant[process_id].height = height + PADDING * 2
     
      top += height + PADDING + SPACING
 
  def _make_gv(self, process):
    for element in process["elements"].keys():
      self.g.node(element)
 
    for source, target in process["interactions"]:
      self.g.edge(source, target)
 
    self.g.render()
    gv = json.loads(self.g.pipe("json").decode())
 
    positions = [
      (obj["name"],) + tuple([int(float(pos)) for pos in obj["pos"].split(",")])
      for obj in gv["objects"]
    ]
   
    # normalize
    min_x = min([position[1] for position in positions])
    min_y = min([position[2] for position in positions])
 
    return [
      (position[0], position[1] - min_x, position[2] - min_y)
      for position in positions
    ]

def layout(model, g=None):
  LayoutVisitor(g=g).analyze(model).layout()
  model.apply(routing.Direct())
