"""
  Initial tests to drive development entirely from tests ;-)
  TDD rules 💪
"""

from bpmn_tools.diagrams import Definitions
from bpmn_tools.diagrams import Process, Start, End, Task, Flow
from bpmn_tools.diagrams import Collaboration, Participant
from bpmn_tools.diagrams import Shape, Edge

import json

def test_create_single_step_process():
  """
    Create a single-step process.
    (start) -> (task: Say "Hello!") -> (end)
  """
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ])

  assert process.as_dict() == {
    "bpmn:process": {
      "@id": "process",
      "bpmn:startEvent": {
        "@id": "start",
        "bpmn:outgoing": "flow_start_hello"
      },
      "bpmn:task": {
        "@id": "hello",
        "@name": "Say \"Hello!\"",
        "bpmn:incoming": "flow_start_hello",
        "bpmn:outgoing": "flow_hello_end"
      },
      "bpmn:endEvent": {
        "@id": "end",
        "bpmn:incoming": "flow_hello_end"
      },
      "bpmn:sequenceFlow": [
        {
          "@id": "flow_start_hello",
          "@sourceRef": "start",
          "@targetRef": "hello"
        },
        {
          "@id": "flow_hello_end",
          "@sourceRef": "hello",
          "@targetRef": "end"
        }
      ]
    }
  }

def test_create_single_participant_collaboration():
  """
    Create a single participant collaboration for Process(id="process")
  """
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", Process(id="process"), id="participant")
  )
  
  assert collaboration.as_dict() == {
    "bpmn:collaboration": {
      "@id": "collaboration",
      "bpmn:participant": {
        "@id": "participant",
        "@name": "participant",
        "@processRef": "process"
      }
    }
  }

def test_create_definitions_with_process_and_collaboration():
  """
    Create Definitions with both a single-step process and collaboration.
  """
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ])
  
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", process, id="participant")
  )
  
  definitions = Definitions(id="definitions").extend([
    process,
    collaboration
  ])
  
  assert definitions.as_dict() == {
    "bpmn:definitions": {
      "@xmlns:bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "@xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
      "@xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
      "@xmlns:di": "http://www.omg.org/spec/DD/20100524/DI",
      "@id": "definitions",
      "bpmn:process": {
        "@id": "process",
        "bpmn:startEvent": {
          "@id": "start",
          "bpmn:outgoing": "flow_start_hello"
        },
        "bpmn:task": {
          "@id": "hello",
          "@name": "Say \"Hello!\"",
          "bpmn:incoming": "flow_start_hello",
          "bpmn:outgoing": "flow_hello_end"
        },
        "bpmn:endEvent": {
          "@id": "end",
          "bpmn:incoming": "flow_hello_end"
        },
        "bpmn:sequenceFlow": [
          {
            "@id": "flow_start_hello",
            "@sourceRef": "start",
            "@targetRef": "hello"
          },
          {
            "@id": "flow_hello_end",
            "@sourceRef": "hello",
            "@targetRef": "end"
          }
        ]
      },
      "bpmn:collaboration": {
        "@id": "collaboration",
        "bpmn:participant": {
          "@id": "participant",
          "@name": "participant",
          "@processRef": "process"
        }
      }
    }
  }

def test_create_start_shape():
  """
    Create a shape for a Start element, with default bounds
  """

  shape = Shape(Start(id="start"))
  
  assert shape.as_dict() == {
    "bpmndi:BPMNShape": {
      "@id": "shape_start",
      "@bpmnElement": "start",
      "dc:Bounds": {
        "@x": "0",
        "@y": "0",
        "@width": "36",
        "@height": "36"
      }
    }
  }

def test_create_task_shape():
  """
    Create a shape for a Task element, with default bounds
  """

  shape = Shape(Task(id="hello"))
  
  assert shape.as_dict() == {
    "bpmndi:BPMNShape": {
      "@id": "shape_hello",
      "@bpmnElement": "hello",
      "dc:Bounds": {
        "@x": "0",
        "@y": "0",
        "@width": "100",
        "@height": "80"
      },
      "bpmndi:BPMNLabel": None
    }
  }

def test_create_edge():
  """
    Create an edge for a flow between start and end
  """

  flow = Flow(source=Start(id="start"), target=End(id="end"))
  edge = Edge(flow)
  
  result = edge.as_dict()
  print(json.dumps(result, indent=2))
  
  assert result == {
    "bpmndi:BPMNEdge": {
      "@id": "edge_flow_start_end",
      "@bpmnElement": "flow_start_end",
      "di:waypoint": [
        {
          "@x": "36",
          "@y": "18"
        },
        {
          "@x": "0",
          "@y": "18"
        }
      ]
    }
  }
