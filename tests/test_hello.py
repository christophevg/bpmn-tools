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
    Task('Say "Hello!"', ref="hello"),
    End()
  ]

  process = Process(ref="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ]).as_dict()

  assert process == {
    "bpmn:process": {
      "@ref": "process",
      "bpmn:startEvent": {
        "@ref": "start",
        "bpmn:outgoing": "flow_start_hello"
      },
      "bpmn:task": {
        "@ref": "hello",
        "@name": "Say \"Hello!\"",
        "bpmn:incoming": "flow_start_hello",
        "bpmn:outgoing": "flow_hello_end"
      },
      "bpmn:endEvent": {
        "@ref": "end",
        "bpmn:incoming": "flow_hello_end"
      },
      "bpmn:sequenceFlow": [
        {
          "@ref": "flow_start_hello",
          "@sourceRef": "start",
          "@targetRef": "hello"
        },
        {
          "@ref": "flow_hello_end",
          "@sourceRef": "hello",
          "@targetRef": "end"
        }
      ]
    }
  }

def test_create_single_participant_collaboration():
  """
    Create a single participant collaboration for Process(ref="process")
  """
  collaboration = Collaboration(ref="collaboration").append(
    Participant("participant", Process(ref="process"), ref="participant")
  ).as_dict()
  
  assert collaboration == {
    "bpmn:collaboration": {
      "@ref": "collaboration",
      "bpmn:participant": {
        "@ref": "participant",
        "@name": "participant",
        "@processRef": "process"
      }
    }
  }
