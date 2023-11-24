from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Start, End, UserTask, ScriptTask
from bpmn_tools.flow          import Flow, Lane
from bpmn_tools.flow          import MessageFlow
from bpmn_tools.diagrams      import Diagram, Plane

from bpmn_tools.layout        import simple

def test_diagram_with_lane(compare_model_to_file):
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
    Flow(id="flow_start_hello", source=activities_lane1[0], target=activities_lane1[1]),
    Flow(id="flow_hello_end",   source=activities_lane1[1], target=activities_lane1[2])
  ])

  process_lane2 = Process(id="process2").append(lane2)

  collaboration = Collaboration(id="collaboration").extend([
    Participant("participant1", process_lane1, id="participant1"),
    Participant("participant2", process_lane2, id="participant2"),
    MessageFlow(id="flow_hello_hear",  source=activities_lane1[1], target=activities_lane2[0]),
    MessageFlow(id="flow_hello_hear2", source=activities_lane1[1], target=activities_lane2[1]),
    MessageFlow(id="flow_hello_hear3", source=activities_lane1[1], target=activities_lane2[2])
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

  compare_model_to_file(
    definitions,
    "hello-lanes-with-message.bpmn",
    save_to="hello-lanes-with-message-test.bpmn"
  )
  
  # TODO: first implement extraction of x, y, height, width from Shape->Element
  # compare_with_roundtrip(definitions, expected)
