from bpmn_tools.notation      import Definitions
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.flow          import Process, Task, Flow, MessageFlow
from bpmn_tools.diagrams      import Diagram, Plane

from bpmn_tools.layout        import simple

def test_recursive_simple_layout(compare_model_to_file):
  
  activities = [
    Task("step 1", id="step1"),
    Task("step 2", id="step2"),
    Task("step 3", id="step3"),
    Task("step 4", id="step4")
  ]

  process1 = Process(id="process1").extend(activities).extend([
    Flow(id="flow_step1_step2", source=activities[0], target=activities[1]),
    Flow(id="flow_step1_step3", source=activities[0], target=activities[2]),
    Flow(id="flow_step1_step4", source=activities[0], target=activities[3])
  ])

  remote_activity = Task("step 5", id="step5")
  process2 = Process(id="process2").append(remote_activity)
  
  collaboration = Collaboration(id="collaboration").extend([
    Participant("process 1", process1, id="participant_process1"),
    Participant("process 2", process2, id="participant_process2")
  ]).append(
    MessageFlow(id="flow_step1_step5", source=activities[0], target=remote_activity)
  )

  definitions = Definitions(id="definitions").extend([
    process1,
    process2,
    collaboration
  ])

  definitions.append(
    Diagram(
      id="diagram",
      plane=Plane(id="plane", element=collaboration)
    )
  )
  
  simple.layout(definitions)

  compare_model_to_file(
    definitions,
    "recursive_simple_layout.bpmn",
    save_to="recursive_simple_layout-test.bpmn"
  )
