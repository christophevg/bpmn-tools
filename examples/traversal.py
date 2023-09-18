from pathlib import Path
import xmltodict

from colorama import init as colorama_init

from bpmn_tools.notation import Definitions
from bpmn_tools.visitor  import Visitor, visiting
from bpmn_tools.flow     import Task, UserTask, ScriptTask, ServiceTask

colorama_init()

folder = Path(__file__).resolve().parent / ".." / "examples" 
with open( folder / "hello-with-lanes.bpmn") as fp:
  xml = xmltodict.parse(fp.read())
  tree = Definitions.from_dict(xml)
  
  class TaskVisitor(Visitor):
    @visiting(Task, UserTask, ScriptTask, ServiceTask)
    def visit(self, task):
      print(task)
      print("  ", task.process)
      print("  ", task.process.participant)
      print("  ", task.lane)

  tree.accept(TaskVisitor())
