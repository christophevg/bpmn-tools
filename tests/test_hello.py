"""
  Initial tests to drive development entirely from tests ;-)
  TDD rules 💪
"""

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
