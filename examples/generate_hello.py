import logging
logger = logging.getLogger(__name__)

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
FORMAT    = "[%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

from bpmn_tools.flow          import Process, Start, End, Task, Flow
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge
from bpmn_tools.layout        import simple

import xmltodict

activities = [
  Start(id="start"),
  Task('Say "Hello!"', id="hello"),
  Task('Wait for response...', id="wait"),
  End(id="end")
]

process = Process(id="process").extend(activities).extend([
  Flow(source=activities[0], target=activities[1]),
  Flow(source=activities[1], target=activities[2]),
  Flow(source=activities[2], target=activities[3])
])

collaboration = Collaboration(id="collaboration").append(
  Participant("lane", process, id="participant")
)

model = Definitions(id="definitions").extend([
  process,
  collaboration,
])

model.append(
  Diagram(
    id="diagram",
    plane=Plane(id="plane", element=collaboration)
  )
)

simple.layout(model)

print(xmltodict.unparse(model.as_dict(with_tag=True), pretty=True))
