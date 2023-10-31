from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.extensions    import CamundaPropertyExtension

def test_minimal_extensions_setup(compare_model_to_file):

  process = Process(id="process")

  collaboration = Collaboration(id="collaboration").append(
    Participant("lane", process, id="participant")
  ).extend([
    CamundaPropertyExtension("name 1", "value 1"),
    CamundaPropertyExtension("name 2", "value 2")
  ])

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

  compare_model_to_file(
    definitions, "extensions.bpmn", save_to="extensions-lastest.bpmn"
  )
