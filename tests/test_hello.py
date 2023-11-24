"""
  Initial tests to drive development entirely from tests ;-)
  TDD rules 💪
  The tests build towards a complete support to construct the hello.bpmn example
"""

from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Start, End, Task, Flow
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge

def test_create_single_step_process(compare):
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
    Flow(id="flow_start_hello", source=activities[0], target=activities[1]),
    Flow(id="flow_hello_end",   source=activities[1], target=activities[2])
  ])

  compare(process.as_dict(with_tag=True), {
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

def test_create_single_participant_collaboration(compare):
  """
    Create a single participant collaboration for Process(id="process")

    <bpmn:collaboration id="collaboration">
      <bpmn:participant id="participant" name="lane" processRef="process" />
    </bpmn:collaboration>
  """
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", Process(id="process"), id="participant")
  )

  compare(collaboration.as_dict(with_tag=True), {
    "bpmn:collaboration": {
      "@id": "collaboration",
      "bpmn:participant": {
        "@id": "participant",
        "@name": "participant",
        "@processRef": "process"
      }
    }
  })

def test_create_definitions_with_process_and_collaboration(compare):
  """
    Create Definitions with both a single-step process and collaboration.

    <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                      xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                      xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                      xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                      xmlns:modeler="http://camunda.org/schema/modeler/1.0"
                      id="definitions"
                      xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
                      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
    Flow(id="flow_start_hello", source=activities[0], target=activities[1]),
    Flow(id="flow_hello_end",   source=activities[1], target=activities[2])
  ])

  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", process, id="participant")
  )

  definitions = Definitions(id="definitions").extend([
    process,
    collaboration
  ])

  compare(definitions.as_dict(with_tag=True), {
    "bpmn:definitions": {
      "@xmlns:bioc": "http://bpmn.io/schema/bpmn/biocolor/1.0",
      "@xmlns:color": "http://www.omg.org/spec/BPMN/non-normative/color/1.0",
      "@xmlns:bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
      "@xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
      "@xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
      "@xmlns:di": "http://www.omg.org/spec/DD/20100524/DI",
      "@xmlns:zeebe": "http://camunda.org/schema/zeebe/1.0",
      "@xmlns:xsi" : "http://www.w3.org/2001/XMLSchema-instance",
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

def test_create_start_shape(compare):
  """
    Create a shape for a Start element, with default bounds

    <bpmndi:BPMNShape id="shape_start" bpmnElement="start">
      <dc:Bounds x="179" y="99" width="36" height="36" />
    </bpmndi:BPMNShape>
  """

  shape = Shape(Start(id="start"))

  compare(shape.as_dict(with_tag=True), {
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

def test_create_task_shape(compare):
  """
    Create a shape for a Task element, with default bounds

    <bpmndi:BPMNShape id="shape_hello" bpmnElement="hello">
      <dc:Bounds x="270" y="77" width="100" height="80" />
    </bpmndi:BPMNShape>
  """

  shape = Shape(Task(id="hello"))

  compare(shape.as_dict(with_tag=True), {
    "bpmndi:BPMNShape": {
      "@id": "shape_hello",
      "@bpmnElement": "hello",
      "dc:Bounds": {
        "@x": "0",
        "@y": "0",
        "@width": "100",
        "@height": "80"
      }
    }
  })

def test_create_edge(compare):
  """
    Create an edge for a flow between start and

    <bpmndi:BPMNEdge id="edge_flow_start_hello" bpmnElement="flow_start_hello">
      <di:waypoint x="215" y="117" />
      <di:waypoint x="270" y="117" />
    </bpmndi:BPMNEdge>
  """

  flow = Flow(id="flow_start_hello", source=Start(id="start"), target=Task(id="hello"))
  edge = Edge(flow)

  compare(edge.as_dict(with_tag=True), {
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

def test_empty_diagram(compare):
  """
    An empty diagram, always contains a plane.

    <bpmndi:BPMNDiagram id="diagram">
      <bpmndi:BPMNPlane id="plane">
      </bpmndi:BPMNPlane>
    </bpmndi:BPMNDiagram>
  """

  diagram = Diagram(id="diagram")

  compare(diagram.as_dict(with_tag=True), {
    "bpmndi:BPMNDiagram": {
      "@id": "diagram",
      "bpmndi:BPMNPlane": {
        "@id": "plane"
      }
    }
  })

def test_plane_for_collaboration_with_one_participant_without_a_process(compare):
  """
    A plane for a collaboration with on participant.

    <bpmndi:BPMNPlane id="plane_collaboration" bpmnElement="collaboration">
      <bpmndi:BPMNShape id="participant_di" bpmnElement="participant" isHorizontal="true">
        <dc:Bounds x="129" y="57" width="600" height="123" />
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  """ # noqa
  collaboration = Collaboration(id="collaboration").append(
    Participant("participant", None, id="participant")
  )
  plane = Plane(id="plane", element=collaboration)

  compare(plane.as_dict(with_tag=True), {
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

def test_hello(compare_model_to_file):
  activities = [
    Start(id="start"),
    Task('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(id="flow_start_hello", source=activities[0], target=activities[1]),
    Flow(id="flow_hello_end",   source=activities[1], target=activities[2])
  ])

  collaboration = Collaboration(id="collaboration").append(
    Participant("lane", process, id="participant")
  )

  definitions = Definitions(id="definitions").extend([
    process,
    collaboration,
  ])

  definitions.append(
    Diagram(
      id="diagram",
      plane=Plane(id="plane", element=collaboration)
    )
  )

  compare_model_to_file(definitions, "hello.bpmn", save_to="hello-test.bpmn")
