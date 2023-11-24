from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Start, End, Task
from bpmn_tools.flow          import Flow, FlowNodeRef, Lane, LaneSet
from bpmn_tools.diagrams      import Diagram, Plane

from bpmn_tools.layout        import simple

from tests.conftest import compare

def compare_with_roundtrip(obj1, expected):
  # obj -> xml
  d1 = obj1.as_dict(with_tag=True)
  print("*" * 20, "round 1" , "*" * 20)
  compare(d1, expected)
  
  # xml -> obj
  
  obj2 = Definitions.from_dict(d1)
  
  d2 = obj2.as_dict(with_tag=True)
  print("*" * 20, "round 2" , "*" * 20)
  compare(d2, expected)
  
  return obj2

def test_flow_node_ref():
  a = Task("Some task")
  r1 = FlowNodeRef(a)

  assert r1.ref  == a
  assert r1.text == a.id

  r2 = compare_with_roundtrip(r1, { "bpmn:flowNodeRef" : a.id })
  
  assert r2.ref  is None
  assert r2.text == a.id

def test_lane():
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  l1 = Lane("some lane", id="testlane").extend(activities)

  compare_with_roundtrip(l1, {
    "bpmn:lane": {
      "@id": "testlane",
      "@name": "some lane",
      "bpmn:flowNodeRef": [
        "start",
        "hello",
        "end"
      ]
    }
  })

def test_laneset():
  l1 = Lane("lane 1", id="lane1").append(Task("task 1", id="task1"))
  l2 = Lane("lane 2", id="lane2").append(Task("task 2", id="task2"))
  ls = LaneSet(id="laneset").extend([l1, l2])
  
  assert len(ls) == 2

  compare_with_roundtrip(ls,{
    "bpmn:laneSet": {
      "@id": "laneset",
      "bpmn:lane": [
        {
          "@id": "lane1",
          "@name": "lane 1",
          "bpmn:flowNodeRef": "task1"
        },
        {
          "@id": "lane2",
          "@name": "lane 2",
          "bpmn:flowNodeRef": "task2"
        }
      ]
    }
  })

def test_process_with_default_laneset():
  l1 = Lane("lane 1", id="lane1").append(Task("task 1", id="task1"))
  l2 = Lane("lane 2", id="lane2").append(Task("task 2", id="task2"))
  ls = LaneSet(id="laneset").extend([l1, l2])

  process = Process(id="process").append(ls)
  
  compare_with_roundtrip(process, {
    "bpmn:process": {
      "@id": "process",
      "bpmn:task": [
        {
          "@id": "task1",
          "@name": "task 1"
        },
        {
          "@id": "task2",
          "@name": "task 2"
        }
      ],
      "bpmn:laneSet": {
        "@id": "laneset",
        "bpmn:lane": [
          {
            "@id": "lane1",
            "@name": "lane 1",
            "bpmn:flowNodeRef": "task1"
          },
          {
            "@id": "lane2",
            "@name": "lane 2",
            "bpmn:flowNodeRef": "task2"
          }
        ]
      }
    }
  })

def test_diagram_with_lane(compare_model_to_file):
  activities_lane1 = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  activities_lane2 = [
    Task('Hear "Hello!"', id="hear")
  ]

  lane2 = Lane("lane 2", id="lane2").extend(activities_lane2)

  process_lane1 = Process(id="process1").extend(activities_lane1).extend([
    Flow(id="flow_start_hello", source=activities_lane1[0], target=activities_lane1[1]),
    Flow(id="flow_hello_end",   source=activities_lane1[1], target=activities_lane1[2])
  ])

  process_lane2 = Process(id="process2").append(lane2)

  collaboration = Collaboration(id="collaboration").extend([
    Participant("participant1", process_lane1, id="participant1"),
    Participant("participant2", process_lane2, id="participant2")
  ])

  definitions = Definitions(id="definitions").extend([
    process_lane1,
    process_lane2,
    collaboration
  ])

  definitions.append(
    Diagram(
      id="diagram",
      plane=Plane(id="plane", element=collaboration)
    )
  )

  simple.layout(definitions)

  compare_model_to_file(definitions, "hello-lanes.bpmn", save_to="hello-lanes-test.bpmn")

def test_process_of_element_in_lane():
  """
    tests if a task in a lane's process is actually the process
  """
  task = Task("task")
  process = Process().append(task)
  assert task.process == process

  task = Task("task")
  lane = Lane("lane").append(task)
  process = Process().append(lane)
  assert task.process == process
