"""
  Initial tests to drive development entirely from tests ;-)
  TDD rules 💪
"""

from bpmn_tools.diagrams import Definitions
from bpmn_tools.diagrams import Process, Start, End, Task, Flow
from bpmn_tools.diagrams import Collaboration, Participant

def test_create_single_step_process():
  """
    Create a single-step process.
    (start) -> (task: Say "Hello!") -> (end)
  """
  activities = [
    Start(),
    Task('Say "Hello!"', id="hello"),
    End()
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ]).as_dict()

  assert process == {
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
  ).as_dict()
  
  assert collaboration == {
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
    Start(),
    Task('Say "Hello!"', id="hello"),
    End()
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
  ]).as_dict()
  
  assert definitions == {
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
