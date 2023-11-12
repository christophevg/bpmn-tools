# import dataclasses

from pathlib import Path

from bpmn_tools.builder.process import Process, Task, Branch, BranchKind

def test_basic_process_building(compare_model_to_file):
  """
  

                        | -> [ Task 2 ] -------------- |
  S -> [ Task 1 ] -> < + >                            < > -> [ Task 4 ] -> S
                        | -> < x > ------------- < > - | 
                                | -> [ Task 3 ] - |
  
  """
  process = Process(name="main", starts=True, ends=True).add(
    Task(name="Task 1")
  ).add(
    Branch(kind=BranchKind.AND).add(
      Task(name="Task 2")
    ).add(
      Branch(default=True).add(
        Task(name="Task 3")
      )
    )
  ).add(
    Task(name="Task 4")
  )

  model = process.render()
  
  folder = Path(__file__).resolve().parent / "models"
  filepath = folder / "hello-process-builder.bpmn"
  
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-latest.bpmn")
