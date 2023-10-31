import logging

import os

from bpmn_tools.flow          import Process, Start, IntermediateThrow, Task, Flow
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.layout        import simple

from bpmn_tools.util          import model2xml

logger = logging.getLogger(__name__)

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
FORMAT    = "[%(name)s] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)
logging.getLogger().handlers[0].setFormatter(formatter)

activities = [
  Start(id="start"),
  Task("Generate Message", id="generate"),
  IntermediateThrow(id="end", message=True, name="an Event")
]

process = Process(id="process").extend(activities).extend([
  Flow(source=activities[0], target=activities[1]),
  Flow(source=activities[1], target=activities[2])
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

print(model2xml(model))
