# What's in The Box?

BPMN Tools (currently) consists of:

## An Object Model

The base object model mimicks the XML structure of BPMN. It allows for creating BPMN models and consists of the following modules and classes:

* notation
  * Definitions
* collaboration
  * Participant
  * Collaboration
* flow
  * Flow and MessageFlow
  * Start and End
  * Task, UserTask, ServiceTask, SendTask, ReceiveTask, ManualTask, BusinessRuleTask, ScriptTask
  * ExclusiveGateway, InclusiveGateway, ParallelGateway
  * Process
* diagrams
  * Diagram
  * Plane
  * Shape and Edge
  
Most other XML tags are also available. BPMN Tools tries to remove as much of the clutter as possible and follows some conventions to allow you to focus on the essencials/bare minimum.

## Simple Layouting

A first, simple layout function allows for automatically arranging shapes and edges:

![Hello With Laneset](hello-with-laneset.png)

## A Directed Acyclic Graph-like Process Builder

If your processes adhere to [DAG-like flows](https://en.wikipedia.org/wiki/Directed_acyclic_graph), you can also use a (first) process builder. It provides an alternative object model (which in its turn uses the base object model) and allows you to specify the bare minimum, with a compact and fluid API:

```python
Process([
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
```

And this produces the following result:

![Hello With Laneset](dag-process.png)


More to come...
