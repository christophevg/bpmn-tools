import dataclasses

from bpmn_tools.builder.process import Process, Task, Branch, BranchKind

def test_basic_process_building():
  """
  

                        | -> [ Task 2 ] -------------- |
  S -> [ Task 1 ] -> < + >                            < > -> [ Task 4 ] -> S
                        | -> < x > ------------- < > - | 
                                | -> [ Task 3 ] - |
  
  """
  process = Process(label="main", starts=True, stops=True).add(
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

  assert dataclasses.asdict(process) == {
    "label": "main",
    "starts": True,
    "stops": True,
    "steps": [
      {
        "label": None,
        "name": "Task 1"
      },
      {
        "label": None,
        "default": None,
        "kind": BranchKind.AND,
        "branches": [
          {
            "label": None,
            "name": "Task 2"
          },
          {
            "label": None,
            "default": True,
            "kind": BranchKind.XOR,
            "branches": [
              {
                "label": None,
                "name": "Task 3"
              }
            ]
          }
        ]
      },
      {
        "label": None,
        "name": "Task 4"
      }
    ]
  }
