import logging
logger = logging.getLogger(__name__)

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "WARN"
FORMAT    = "[%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

from bpmn_tools.flow          import Process, Start, End, Task, Flow, Lane, UserTask, ScriptTask, MessageFlow
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge
from bpmn_tools.colors        import Green, Red
from bpmn_tools.layout        import simple

import xmltodict

activities_lane1 = [
  Start(id="start"),
  Green(UserTask('Say "Hello!"', id="hello")),
  Task('Wait for response...', id="wait"),
  End(id="end")
]

activities_lane2 = [
  ScriptTask('Hear "Hello!"', id="hear"),
  Red(ScriptTask('Also Hear "Hello!"', id="hear2")),
  ScriptTask('Also Also Hear "Hello!"', id="hear3"),
]

lane2 = Lane("lane 2", id="lane2").extend(activities_lane2)

process_lane1 = Process(id="process1").extend(activities_lane1).extend([
  Flow(source=activities_lane1[0], target=activities_lane1[1]),
  Flow(source=activities_lane1[1], target=activities_lane1[2]),
  Flow(source=activities_lane1[2], target=activities_lane1[3])
])

process_lane2 = Process(id="process2").append(lane2)

collaboration = Collaboration(id="collaboration").extend([
  Participant("participant1", process_lane1, id="participant1"),
  Participant("participant2", process_lane2, id="participant2"),
  MessageFlow(source=activities_lane1[1], target=activities_lane2[1]),
  MessageFlow(source=activities_lane2[1], target=activities_lane1[2])
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

print(xmltodict.unparse(definitions.as_dict(with_tag=True), pretty=True))
