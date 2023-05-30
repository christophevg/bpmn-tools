import xmltodict
from pathlib import Path

from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Start, End, Task, UserTask, ScriptTask
from bpmn_tools.flow          import Flow, FlowNodeRef, Lane, LaneSet
from bpmn_tools.flow          import MessageFlow
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge

from bpmn_tools.layout        import simple

from bpmn_tools.xml           import Element

from bpmn_tools.util import compare

def test_diagram_with_lane():
  with open(Path(__file__).resolve().parent / "hello-lanes-with-message.bpmn") as fp:
    expected = xmltodict.parse(fp.read())

  activities_lane1 = [
    Start(id="start"),
    UserTask('Say "Hello!"', id="hello"),
    End(id="end")
  ]

  activities_lane2 = [
    ScriptTask('Hear "Hello!"', id="hear"),
    ScriptTask('Also Hear "Hello!"', id="hear2"),
    ScriptTask('Also Also Hear "Hello!"', id="hear3"),
  ]

  lane2 = Lane("lane 2", id="lane2").extend(activities_lane2)

  process_lane1 = Process(id="process1").extend(activities_lane1).extend([
    Flow(source=activities_lane1[0], target=activities_lane1[1]),
    Flow(source=activities_lane1[1], target=activities_lane1[2])
  ])

  process_lane2 = Process(id="process2").append(lane2)

  collaboration = Collaboration(id="collaboration").extend([
    Participant("participant1", process_lane1, id="participant1"),
    Participant("participant2", process_lane2, id="participant2"),
    MessageFlow(source=activities_lane1[1], target=activities_lane2[0]),
    MessageFlow(source=activities_lane1[1], target=activities_lane2[1]),
    MessageFlow(source=activities_lane1[1], target=activities_lane2[2])
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

  compare(definitions.as_dict(with_tag=True), expected)
  
  # TODO: first implement extraction of x, y, height, width from Shape->Element
  # compare_with_roundtrip(definitions, expected)
  