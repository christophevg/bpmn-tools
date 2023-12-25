from pathlib import Path

from bpmn_tools.builder.process import Process, Task, Branch, BranchKind, If
from bpmn_tools.builder.process import connect

from bpmn_tools import flow
from bpmn_tools.colors import Green, Blue, Red, Orange

folder = Path(__file__).resolve().parent / "models"

def test_basic_process_building(compare_model_to_file):
  """
                        | -> [ Task 2 ] -------------- |
  S -> [ Task 1 ] -> < + >                            < > -> [ Task 4 ] -> S
                        | -> < x > ------------- < > - | 
                                | -> [ Task 3 ] - |
  """
  process = Process(name="main", starts=True, ends=True, color=Red).extend([
    Task(name="Task 1", color=Green),
    Branch(kind=BranchKind.AND, label="AND").add(
      Task(name="Task 2"), "with task 2"
    ).add(
      Branch(default=True, label="OR", color=Blue).add(
        Task(name="Task 3", color=Orange), "only task 3"
      ), "with task 3"
    ),
    Task(name="Task 4")
  ])

  model = process.render()
  
  filepath = folder / "hello-process-builder.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_complex_process_building(compare_model_to_file):
  process = Process([
    Task(name="Task 1"),
    Branch([
      Process([
        Branch([
          Task(name="Task 1b"),
          Task(name="Task 1c"),
          Task(name="Task 1d")
        ]),
        Task(name="Task 2a")
      ]),
      Task(name="Task 2b"),
      Process([
        Branch([
          Task(name="Task 2c-1"),
          Task(name="Task 2c-2"),
          Task(name="Task 2c-3")
        ]),
        Branch([
          Task(name="Task 2d-1"),
          Task(name="Task 2d-2"),
          Task(name="Task 2d-3")
        ])
      ]),
      Branch([
        Task(name="Task 3")
      ], default=True)
    ], kind=BranchKind.AND),
    Task(name="Task 4")
  ], name="complex", starts=True, ends=True)

  model = process.render()
  
  filepath = folder / "process-builder-complex-process-builder.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_bug_process_events_with_intial_branch(compare_model_to_file):
  process = Process([
    Branch([
      Task(name="Task 1"),
      Task(name="Task 2"),
      Task(name="Task 3")
    ]),
    Task(name="Task 4")
  ], name="bug start/end event with branch height", starts=True, ends=True)

  model = process.render()
  
  filepath = folder / "process-builder-bug_start_before_branch.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_branch_conditions_and_labels(compare_model_to_file):
  process = Process([
    Branch([
      If("long condition task 1", Task(name="Task 1")),
      If("medium task 2", Task(name="Task 2")),
      If("task 3", Task(name="Task 3"))
    ], default=True, label="conditions"),
    Task(name="Task 4")
  ], name="conditions and labels", starts=True, ends=True)

  model = process.render()
  
  filepath = folder / "process-builder-conditions_and_labels.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_boundary_event(compare_model_to_file):
  process = Process([
    Task(name="Task 1", boundary=flow.MessageEventDefinition)
  ], name="task with boundary event")

  model = process.render()
  
  filepath = folder / "process-builder-based-boundary-events.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_bug_flow_from_boundary_event_to_end(compare_model_to_file):
  process = Process([
    Branch([
      Task(name="Task 1", boundary=flow.MessageEventDefinition)
    ], default=True)
  ], name="task with boundary event", ends=True)

  model = process.render()
  
  filepath = folder / "process-builder-bug_flow_from_boundary_event_to_end.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_task_id():
  task = Task()                             # task_0
  assert task.id == "task_0"
  assert task.element.id == "task_0"

  task = Task(id="test_task")               # task_1
  assert task.id == "test_task"
  assert task.element.id == "test_task"

  task = Task(id=lambda d: f"prefixed_{d}") # task_2
  assert task.id == "prefixed_task_2"
  assert task.element.id == "prefixed_task_2"

def test_connect_only_accepts_different_source_and_target_shapes():
  task = flow.Task(name="task")
  try:
    connect(task, task)
    assert False, "connect should not accept same source and target"
  except ValueError:
    pass
