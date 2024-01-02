from bpmn_tools.flow          import Process, Flow, MessageFlow, Lane
from bpmn_tools.flow          import Task
from bpmn_tools.flow          import ExclusiveGateway
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.layout        import simple

def test_issue_1(compare_model_to_file):
  # minimal example to illustrate problem, based on submitted example
  # https://github.com/christophevg/bpmn-tools/issues/1

  a = Task("task a", id="a")
  b = Task("task b", id="b")

  decision = ExclusiveGateway("gateway", id="gateway")

  lane1 = Lane("lane", id="lane")
  lane1.extend([a, decision, b])

  flow1 = Flow(source=a,        target=decision, id="flow1")
  flow2 = Flow(source=decision, target=b,        id="flow2")

  process = Process(id="process").extend([ lane1, flow1, flow2 ])

  collaboration = Collaboration(id="Colaboration").extend([
    Participant("participant", process, id="participant")
  ])

  definitions = Definitions(id="definitions").extend([
    process,
    collaboration
  ])

  definitions.append(
    Diagram( id="diagram", plane=Plane(id="plane", element=collaboration) )
  )

  simple.layout(definitions)

  compare_model_to_file(definitions, "issues/1.bpmn", save_to="issues/1-test.bpmn")

def test_issue_2(compare_model_to_file):
  # minimal example to illustrate problem, based on submitted example
  # https://github.com/christophevg/bpmn-tools/issues/2
  
  task = Task("task a", id="a")

  process1 = Process(id="process1").append(task)
  process2 = Process(id="process2")
  
  participant1 = Participant("participant 1", process1, id="participant 1")
  participant2 = Participant("participant 2", process2, id="participant 2")

  # "correct" target would be the participant
  participant1.append(MessageFlow(id="flow", source=task, target=participant2))

  collaboration = Collaboration(id="Colaboration").extend([
    participant1, participant2
  ])

  definitions = Definitions(id="definitions").extend([
    process1,
    process2,
    collaboration
  ])

  definitions.append(
    Diagram( id="diagram", plane=Plane(id="plane", element=collaboration) )
  )

  simple.layout(definitions)

  compare_model_to_file(definitions, "issues/2.bpmn", save_to="issues/2-test.bpmn")
