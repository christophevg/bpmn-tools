from bpmn_tools.flow          import Process, Flow, Lane
from bpmn_tools.flow          import Task
from bpmn_tools.flow          import ExclusiveGateway
from bpmn_tools.collaboration import Collaboration, Participant
from bpmn_tools.notation      import Definitions
from bpmn_tools.diagrams      import Diagram, Plane
from bpmn_tools.layout        import simple

def test_issue_1(compare_model_to_file):
  # minimal example to illustrate raise problem, based on submitted example
  # https://github.com/christophevg/bpmn-tools/issues/1

  a = Task("task a")
  b = Task("task b")

  decision = ExclusiveGateway("gateway")

  lane1 = Lane("lane")
  lane1.extend([a, decision, b])

  flow1 = Flow(source=a,        target=decision)
  flow2 = Flow(source=decision, target=b)

  process = Process().extend([ lane1, flow1, flow2 ])

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

  compare_model_to_file(definitions, "issue-1.bpmn", save_to="issue-1-test.bpmn")
