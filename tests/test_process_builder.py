from pathlib import Path

from bpmn_tools.builder.process import Process, Task, Branch, BranchKind, If
from bpmn_tools.flow import MessageEventDefinition
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
  
  filepath = folder / "complex-process-builder.bpmn"
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
  
  filepath = folder / "bug_start_before_branch.bpmn"
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
  
  filepath = folder / "conditions_and_labels.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_boundary_event(compare_model_to_file):
  process = Process([
    Task(name="Task 1", boundary=MessageEventDefinition)
  ], name="task with boundary event")

  model = process.render()
  
  filepath = folder / "process-builder-based-boundary-events.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")
