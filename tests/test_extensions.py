from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.extensions    import ZeebePropertyExtension

def test_minimal_zeebe_properies_extension(compare_model_to_file):

  process = Process(id="process")

  collaboration = Collaboration(id="collaboration").append(
    Participant("lane", process, id="participant")
  ).extend([
    ZeebePropertyExtension("name 1", "value 1"),
    ZeebePropertyExtension("name 2", "value 2")
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
    definitions, "extensions-zeebe.bpmn", save_to="extensions-zeebe-latest.bpmn"
  )

def test_extensions_access():
  process = Process(id="process")

  collaboration = Collaboration(id="collaboration").append(
    Participant("lane", process, id="participant")
  ).extend([
    ZeebePropertyExtension("zeebe name 1", "value 1"),
    ZeebePropertyExtension("zeebe name 2", "value 2")
  ])
  
  assert collaboration.extension_properties == {
    "zeebe name 1"   : "value 1",
    "zeebe name 2"   : "value 2"
  }
