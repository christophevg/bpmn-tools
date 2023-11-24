from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Task, Flow
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.colors        import Red, Orange, Green, Blue
from bpmn_tools.layout        import simple

def test_colors(compare_model_to_file):
  activities = [
    Red(Task('Red"',    id="red")),
    Green(Task('Green', id="green")),
    Blue(Task('Blue"',  id="blue"))
  ]

  process = Process(id="process").extend(activities).extend([
    Flow(id="flow_red_green",  source=activities[0], target=activities[1]),
    Flow(id="flow_green_blue", source=activities[1], target=activities[2])
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

  compare_model_to_file(definitions, "hello-colors.bpmn", save_to="hello-colors-test.bpmn")
