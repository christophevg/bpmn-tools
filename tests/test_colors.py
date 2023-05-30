from pathlib import Path
import xmltodict

from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Start, End, Task, Flow
from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge
from bpmn_tools.colors        import Red, Orange, Green, Blue
from bpmn_tools.layout        import simple

from bpmn_tools.util import compare

def test_colors():
  with open(Path(__file__).resolve().parent / "hello-colors.bpmn") as fp:
    expected = xmltodict.parse(fp.read())
    
  activities = [
    Red(Task('Red"',    id="red")),
    Green(Task('Green', id="green")),
    Blue(Task('Blue"',  id="blue"))
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(source=activities[0], target=activities[1]),
    Flow(source=activities[1], target=activities[2])
  ])

  collaboration = Collaboration(id="collaboration").append(
    Orange(Participant("lane", process, id="participant"))
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
  
  simple.layout(definitions)

  result = definitions.as_dict(with_tag=True)
  
  compare(result, expected)
