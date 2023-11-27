from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Tasks
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.layout        import simple

def test_all_task_types(compare_model_to_file):
  process = Process(id="process").extend(
    [ cls(cls.__name__, id=cls.__name__) for cls in Tasks ]
  )

  collaboration = Collaboration(id="collaboration").append(
    Participant("all tasks", process, id="participant")
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

  compare_model_to_file(model, "layout-all-tasks.bpmn", save_to="layout-all-tasks-test.bpmn")
