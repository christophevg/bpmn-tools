from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, IntermediateThrow, MessageEventDefinition
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.layout        import simple

def test_message_event(compare_model_to_file):
  message = MessageEventDefinition(id="message")
  event = IntermediateThrow(id="event", definition=message)

  process = Process(id="process").append(event)

  collaboration = Collaboration(id="collaboration").append(
    Participant("lane", process, id="participant")
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

  compare_model_to_file(definitions, "events.bpmn", save_to="events-test.bpmn")
