from bpmn_tools.diagrams import Process, Start, End, Task, Flow
from bpmn_tools.diagrams import Collaboration, Participant
from bpmn_tools.diagrams import Definitions
from bpmn_tools.diagrams import Diagram, Plane, Shape, Edge

import xmltodict

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

print(xmltodict.unparse(definitions.as_dict(), pretty=True))
