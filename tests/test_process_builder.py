# import dataclasses

from pathlib import Path

from bpmn_tools.builder.process import Process, Task, Branch, BranchKind
from bpmn_tools.colors import Green, Blue, Red, Orange

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
  
  folder = Path(__file__).resolve().parent / "models"
  filepath = folder / "hello-process-builder.bpmn"
  
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-latest.bpmn")
