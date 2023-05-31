import logging
logger = logging.getLogger(__name__)

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "WARN"
FORMAT    = "[%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

from bpmn_tools.flow          import Process, Start, End, Task, Flow, Lane, UserTask, ScriptTask, ServiceTask, MessageFlow
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge
from bpmn_tools.colors        import Green, Red, Blue
from bpmn_tools.layout        import simple

import xmltodict

activities1 = [
  Start(id="start"),
  Green(UserTask('Say "Hello!"', id="hello")),
  Task('Wait for response...', id="wait"),
  End(id="end")
]

activities2 = [
  ScriptTask('Hear "Hello!"', id="hear"),
  Red(ScriptTask('Also Hear "Hello!"', id="hear2")),
  ScriptTask('Also Also Hear "Hello!"', id="hear3"),
]

activities3 = [
  Blue(ServiceTask("Support hearing", id="support"))
]

process1 = Process(id="process1").extend(activities1).extend([
  Flow(source=activities1[0], target=activities1[1]),
  Flow(source=activities1[1], target=activities1[2]),
  Flow(source=activities1[2], target=activities1[3])
])

lane2 = Lane("lane 2", id="lane2").extend(activities2)
process2 = Process(id="process2").append(lane2)

process3 = Process(id="process3").extend(activities3)

collaboration = Collaboration(id="collaboration").extend([
  Participant("participant1", process1, id="participant1"),
  Participant("participant2", process2, id="participant2"),
  Participant("participant3", process3, id="participant3"),
  MessageFlow(source=activities1[1], target=activities2[1]),
  MessageFlow(source=activities2[1], target=activities1[2]),
  MessageFlow(source=activities2[1], target=activities3[0])
])

definitions = Definitions(id="definitions").extend([
  process1,
  process2,
  process3,
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
