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


hello = UserTask('Say "Hello!"')
lane1 = Lane("lane 1").append(hello)

hear_self = ScriptTask('Hear own "Hello!"')
ignore = ScriptTask("Ignore")
lane2 = Lane("lane 2").append(hear_self).append(ignore)

flow = Flow(source=hello, target=hear_self)
flow2 = Flow(source=hear_self, target=ignore)

process1 = Process().append(lane1).append(lane2).append(flow).append(flow2)

hear = UserTask('Hear "Hello!"')
respond = UserTask("Respond")

flow3 = Flow(source=hear, target=respond)

process2 = Process().append(hear).append(respond).append(flow3)

collaboration = Collaboration(id="collaboration").extend([
  Participant("participant 1", process1, id="p1"),
  Participant("participant 2", process2, id="p2"),
  MessageFlow(source=hello, target=hear)
])

definitions = Definitions(id="definitions").extend([
  process1,
  process2,
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
