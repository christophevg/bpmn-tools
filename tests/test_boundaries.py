from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Task
from bpmn_tools.diagrams      import Diagram, Plane 

from bpmn_tools.flow          import BoundaryEvent
from bpmn_tools.flow          import EventDefinitions

def test_message_boundaries(compare_model_to_file):
  X = 130
  Y =  60

  activities = []
  for index, event_definition in enumerate(EventDefinitions):
    name = event_definition.__name__
    task = Task(name, id=f"task-{name}")
    task.x = X + 60 + (task.width + 20) * index
    task.y = Y + 30
    event = BoundaryEvent(
      id=f"boundary-event-{name}",
      definition=event_definition(id=f"message-event-definition-{name}"),
      on=task
    )
    activities.extend([task, event])

  process = Process(id="process").extend(activities)

  participant = Participant("lane", process, id="participant")
  participant.x = X
  participant.y = Y
  participant.width = len(EventDefinitions) * (100 + 20) + 70 # TODO fix ;-)

  collaboration = Collaboration(id="collaboration").append(participant)

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

  compare_model_to_file(definitions, "boundaries.bpmn", save_to="boundaries-test.bpmn")
