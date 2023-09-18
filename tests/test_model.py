from bpmn_tools.flow          import Process, Start, End, Task
from bpmn_tools.flow          import Flow

def test_create_single_step_process():
  task = Task('Say "Hello!"', id="hello")

  activities = [ Start(id="start"), task, End(id="end") ]

  process = Process(id="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ])

  assert task.process == process
