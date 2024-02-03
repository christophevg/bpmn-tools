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


# Process

def test_creation_of_empty_process():
  process = bpmn.Process(id="test-process")

  assert len(process.elements) == 0

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
    ref.append(bpmn.FlowNode(id="node1"))
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
  lane.append(node1)
  lane.append(bpmn.FlowNodeRef(element=node2))
  assert len(lane.elements) == 2
  assert len(lane.children) == 2
  try:
    lane.append(bpmn.Lane())
    assert False, "lane should only accept FlowNode(Ref)s"
  except ValueError:
    pass

def test_lane_has_child():
  node1 = bpmn.FlowNode(id="node1")
  node2 = bpmn.FlowNode(id="node2")
  lane = bpmn.Lane(elements=[node1])
  assert lane.has_child(node1)
  assert not lane.has_child(node2)
  lane.append(node2)
  assert lane.has_child(node2)
  