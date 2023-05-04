"""
  Initial tests to drive development entirely from tests ;-)
  TDD rules 💪
  The tests build towards a complete support to construct the hello.bpmn example
"""

from pathlib import Path
import xmltodict
import json
from difflib import unified_diff

from bpmn_tools.diagrams import Definitions
from bpmn_tools.diagrams import Process, Start, End, Task, Flow
from bpmn_tools.diagrams import Collaboration, Participant
from bpmn_tools.diagrams import Diagram, Plane, Shape, Edge

def show_diff(result, expected):
  def as_dict(obj):
    return obj.as_dict()
  result   = json.dumps(expected, indent=2, sort_keys=True, default=as_dict)
  expected = json.dumps(result,   indent=2, sort_keys=True, default=as_dict)
  diff = unified_diff(result.splitlines(keepends=True),
                      expected.splitlines(keepends=True))
  print("".join(diff), end="")

def compare(result, expected):
  show_diff(result, expected)
  assert result == expected

def test_create_single_step_process():
  """
    Create a single-step process.
    (start) -> (task: Say "Hello!") -> (end)
  
    <bpmn:process id="process" isExecutable="true">
      <bpmn:startEvent id="start">
        <bpmn:outgoing>flow_start_hello</bpmn:outgoing>
      </bpmn:startEvent>
      <bpmn:task id="hello" name="Say &#34;Hello!&#34;">
        <bpmn:incoming>flow_start_hello</bpmn:incoming>
        <bpmn:outgoing>flow_hello_end</bpmn:outgoing>
      </bpmn:task>
      <bpmn:endEvent id="end">
        <bpmn:incoming>flow_hello_end</bpmn:incoming>
      </bpmn:endEvent>
      <bpmn:sequenceFlow id="flow_start_hello" sourceRef="start" targetRef="hello" />
      <bpmn:sequenceFlow id="flow_hello_end" sourceRef="hello" targetRef="end" />
    </bpmn:process>
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

  compare(process.as_dict(), {
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
  })

def test_create_single_participant_collaboration():
  """
    Create a single participant collaboration for Process(id="process")
  
    <bpmn:collaboration id="collaboration">
      <bpmn:participant id="participant" name="lane" processRef="process" />
    </bpmn:collaboration>
  """
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", Process(id="process"), id="participant")
  )
  
  compare(collaboration.as_dict(), {
    "bpmn:collaboration": {
      "@id": "collaboration",
      "bpmn:participant": {
        "@id": "participant",
        "@name": "participant",
        "@processRef": "process"
      }
    }
  })

def test_create_definitions_with_process_and_collaboration():
  """
    Create Definitions with both a single-step process and collaboration.
  
    <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                      xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                      xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                      xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                      xmlns:modeler="http://camunda.org/schema/modeler/1.0"
                      id="definitions">
      <bpmn:collaboration id="collaboration">
        <bpmn:participant id="participant" name="lane" processRef="process" />
      </bpmn:collaboration>
      <bpmn:process id="process" isExecutable="true">
        <bpmn:startEvent id="start">
          <bpmn:outgoing>flow_start_hello</bpmn:outgoing>
        </bpmn:startEvent>
        <bpmn:task id="hello" name="Say &#34;Hello!&#34;">
          <bpmn:incoming>flow_start_hello</bpmn:incoming>
          <bpmn:outgoing>flow_hello_end</bpmn:outgoing>
        </bpmn:task>
        <bpmn:endEvent id="end">
          <bpmn:incoming>flow_hello_end</bpmn:incoming>
        </bpmn:endEvent>
        <bpmn:sequenceFlow id="flow_start_hello" sourceRef="start" targetRef="hello" />
        <bpmn:sequenceFlow id="flow_hello_end" sourceRef="hello" targetRef="end" />
      </bpmn:process>
    </bpmn:definitions>
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
  
  compare(definitions.as_dict(), {
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
  })

def test_create_start_shape():
  """
    Create a shape for a Start element, with default bounds

    <bpmndi:BPMNShape id="shape_start" bpmnElement="start">
      <dc:Bounds x="179" y="99" width="36" height="36" />
    </bpmndi:BPMNShape>
  """

  shape = Shape(Start(id="start"))
  
  compare(shape.as_dict(), {
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
  })

def test_create_task_shape():
  """
    Create a shape for a Task element, with default bounds
  
    <bpmndi:BPMNShape id="shape_hello" bpmnElement="hello">
      <dc:Bounds x="270" y="77" width="100" height="80" />
      <bpmndi:BPMNLabel />
    </bpmndi:BPMNShape>
  """

  shape = Shape(Task(id="hello"))
  
  compare(shape.as_dict(), {
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
  })

def test_create_edge():
  """
    Create an edge for a flow between start and 

    <bpmndi:BPMNEdge id="edge_flow_start_hello" bpmnElement="flow_start_hello">
      <di:waypoint x="215" y="117" />
      <di:waypoint x="270" y="117" />
    </bpmndi:BPMNEdge>
  """

  flow = Flow(source=Start(id="start"), target=Task(id="hello"))
  edge = Edge(flow)
  
  compare(edge.as_dict(), {
    "bpmndi:BPMNEdge": {
      "@id": "edge_flow_start_hello",
      "@bpmnElement": "flow_start_hello",
      "di:waypoint": [
        {
          "@x": "36",
          "@y": "18"
        },
        {
          "@x": "0",
          "@y": "40"
        }
      ]
    }
  })

def test_empty_diagram():
  """
    An empty diagram, always contains a plane.
  
    <bpmndi:BPMNDiagram id="diagram">
      <bpmndi:BPMNPlane id="plane">
      </bpmndi:BPMNPlane>
    </bpmndi:BPMNDiagram>
  """
  
  diagram = Diagram(id="diagram")

  compare(diagram.as_dict(), {
    "bpmndi:BPMNDiagram": {
      "@id": "diagram",
      "bpmndi:BPMNPlane": {
        "@id": "plane"
      }
    }
  })

def test_plane_for_collaboration_with_one_participant_without_a_process():
  """
    A plane for a collaboration with on participant.
  
    <bpmndi:BPMNPlane id="plane_collaboration" bpmnElement="collaboration">
      <bpmndi:BPMNShape id="participant_di" bpmnElement="participant" isHorizontal="true">
        <dc:Bounds x="129" y="57" width="600" height="123" />
        <bpmndi:BPMNLabel />
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  """
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", None, id="participant")
  )
  plane = Plane(id="plane", element=collaboration)

  compare(plane.as_dict(), {
    "bpmndi:BPMNPlane": {
      "@id": "plane_collaboration",
      "@bpmnElement": "collaboration",
      "bpmndi:BPMNShape": {
        "@id": "shape_participant",
        "@bpmnElement": "participant",
        "@isHorizontal": "true",
        "dc:Bounds": {
          "@x": "0",
          "@y": "0",
          "@width": "600",
          "@height": "125"
        }
      }
    }
  })

def test_participants_elements_and_flows():
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]
  
  flows = [
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ]

  process = Process(id="process").extend(activities).extend(flows)

  participant = Participant("participant", process, id="participant")
  
  compare(participant.elements, activities)
  compare(participant.flows, flows)

def test_collaboration_passing_through_elements ():
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]
  
  process = Process(id="process").extend(activities)

  participant = Participant("participant", process, id="participant")
  
  collaboration = Collaboration(id="collaboration").append(participant)
  
  compare(collaboration.elements, [ participant ] + activities)
  
def test_hello():
  with open(Path(__file__).resolve().parent / ".." / "examples" / "hello.bpmn") as fp:
    expected = xmltodict.parse(fp.read())

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
    Participant("lane", process, id="participant")
  )

  definitions = Definitions(id="definitions").extend([
    process,
    collaboration,
  ])

  definitions.diagrams.append(
    Diagram(
      id="diagram",
      plane=Plane(id="plane", element=collaboration)
    )
  )

  compare(definitions.as_dict(), expected)
