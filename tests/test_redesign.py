"""

Tests to drive the redesign of the BPMN object model.
Goal is to rebuild the entire model in the future submodule and then drop-in
replace to ensure all existng tests work.

"""

import xmltodict

from bpmn_tools.future import bpmn

# Definitions

NS_ATTRS = { f"@{key}" : value for key, value in bpmn.notation.BPMN_NS.items() }

def test_creation_of_empty_definitions():
  definitions = bpmn.Definitions(id="definitions")

  assert len(definitions.processes)      == 0
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 0

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      **NS_ATTRS,
      **{ "@id" : "definitions" }
    }
  }

def test_parsing_of_empty_definitions():
  xml = """
<bpmn:definitions id="definitions" 
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
</bpmn:definitions>
"""

  definitions = bpmn.Definitions.from_dict(xmltodict.parse(xml))

  assert len(definitions.processes)      == 0
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 0

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      **NS_ATTRS,
      **{ "@id" : "definitions" }
    }
  }

# FlowNodeRef

def test_empty_flow_node_ref():
  ref = bpmn.FlowNodeRef()
  assert ref.text is None
  try:
    ref.element
    assert False, "empty flow node ref should raise ValueError"
  except ValueError:
    pass

def test_flow_node_ref_with_flow_node():
  node1 = bpmn.FlowNode(id="node1")
  ref = bpmn.FlowNodeRef(element=node1)
  assert ref.element is node1
  assert ref.text == "node1"

  ref.text = "other node"
  assert ref.text == "other node"
  try:
    ref.element
    assert False, "flow node with unknown ref should raise ValueError"
  except ValueError:
    pass

  node2 = bpmn.FlowNode(id="node2")
  ref.element = node2
  assert ref.element is node2
  assert ref.text == "node2"

def test_ensure_flow_node_ref_does_not_accept_children():
  ref = bpmn.FlowNodeRef()
  try:
    ref.add(bpmn.FlowNode(id="node1"))
    assert False, "flow node ref should not accept children"
  except ValueError:
    pass

# Lane

def test_empty_lane():
  lane = bpmn.Lane()
  assert len(lane.elements) == 0
  assert len(lane.children) == 0

def test_lane_with_node():
  node1 = bpmn.FlowNode(id="node1")
  lane = bpmn.Lane(elements=[node1])
  assert len(lane.elements) == 1
  assert len(lane.children) == 1

def test_ensure_lane_only_accepts_flow_nodes_and_flow_node_refs():
  node1 = bpmn.FlowNode(id="node1")
  node2 = bpmn.FlowNode(id="node2")
  lane = bpmn.Lane()
  lane.add(node1)
  lane.add(bpmn.FlowNodeRef(element=node2))
  assert len(lane.elements) == 2
  assert len(lane.children) == 2
  try:
    lane.add(bpmn.Lane())
    assert False, "lane should only accept FlowNode(Ref)s"
  except ValueError:
    pass

def test_lane_has_child():
  node1 = bpmn.FlowNode(id="node1")
  node2 = bpmn.FlowNode(id="node2")
  lane = bpmn.Lane(elements=[node1])
  assert lane.has_child(node1)
  assert not lane.has_child(node2)
  lane.add(node2)
  assert lane.has_child(node2)

# LaneSet

def test_empty_lane_set():
  laneset = bpmn.LaneSet()
  assert len(laneset.lanes)    == 0
  assert len(laneset.children) == 0

def test_laneset_only_accepts_lanes():
  lane1 = bpmn.Lane(id="lane1")
  lane2 = bpmn.Lane(id="lane2")
  laneset = bpmn.LaneSet(lanes=[lane1])
  assert len(laneset.lanes) == 1
  laneset.add(lane2)
  assert len(laneset.lanes) == 2
  try:
    laneset.add(bpmn.FlowNode(id="node"))
    assert False, "lane set should only accept lanes"
  except ValueError:
    pass

def test_laneset_lane_of():
  node1 = bpmn.FlowNode(id="node1")
  node2 = bpmn.FlowNode(id="node2")
  lane1 = bpmn.Lane(id="lane1", elements=[node1])
  lane2 = bpmn.Lane(id="lane2", elements=[node2])
  laneset = bpmn.LaneSet(id="laneset", lanes=[lane1, lane2])
  assert laneset.lane_of(node1) is lane1
  assert laneset.lane_of(node2) is lane2

# Task

def test_empty_task():
  task = bpmn.Task(id="task")
  assert task.name is None
  assert task.id == "task"

def test_task_with_name():
  task = bpmn.Task(id="task", name="name")
  assert task.name == "name"
  task.name = "another name"
  assert task.name == "another name"

# Process

def test_creation_of_empty_process():
  process = bpmn.Process(id="test-process")

  assert len(process.elements) == 0
  assert len(process.children) == 0

  assert process.as_dict(with_tag=True) == {
    "bpmn:process" : {
      "@id" : "test-process",
      "@isExecutable" : "true"
    }
  }

def test_parsing_of_definitions_with_empty_process():
  xml = """
<bpmn:definitions id="definitions"
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="parsed-id" isExecutable="false"></bpmn:process>
</bpmn:definitions>
"""

  definitions = bpmn.Definitions.from_dict(xmltodict.parse(xml))

  assert len(definitions.processes)      == 1
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 1

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      **NS_ATTRS,
      **{ "@id" : "definitions" },
      **{ "bpmn:process" : {
            "@id" : "parsed-id",
            "@isExecutable" : "false"
          }
      }
    }
  }

def test_process_with_tasks():
  task1 = bpmn.Task(id="task1")
  task2 = bpmn.Task(id="task2")
  process = bpmn.Process(id="process", elements=[task1])
  assert len(process.elements) == 1
  assert len(process.children) == 1
  process.add(task2)
  assert len(process.elements) == 2
  assert len(process.children) == 2  

def test_process_with_laneset():
  laneset = bpmn.LaneSet()
  process = bpmn.Process(id="process", laneset=laneset)
  assert len(process.elements) == 0
  assert process.laneset is laneset
  assert len(process.children) == 1
  assert process.children == (laneset,)

def _test_process_as_root_for_tasks_in_lanes(compare):
  task1 = bpmn.Task(id="task1")
  task2 = bpmn.Task(id="task2")
  lane1 = bpmn.Lane(id="lane1")
  lane2 = bpmn.Lane(id="lane2")
  laneset = bpmn.LaneSet(id="laneset", lanes=[lane1, lane2])

  assert lane1._parent is laneset
  assert lane2._parent is laneset

  process = bpmn.Process(id="process", laneset=laneset)
  lane1.add(task1)
  lane2.add(task2)

  for item in [ task1, task2, lane1, lane1._refs[0], lane2, lane2._refs[0], laneset]:
    assert item.process is process

  compare(process.as_dict(with_tag=True), {
    "bpmn:process": {
      "@id" : "process",
      "@isExecutable" : "true",
      "bpmn:laneSet" : {
        "@id" : "laneset",
        "bpmn:lane" : [
          {
            "@id" : "lane1",
            "bpmn:flowNodeRef" : "task1"
          },
          {
            "@id" : "lane2",
            "bpmn:flowNodeRef" : "task2"
          }
        ]
      },
      "bpmn:Task" : [
        {
          "@id" : "task1"
        },
        {
          "@id" : "task2"
        }
      ]
    }
  })
