from pathlib import Path
import xmltodict

from dataclasses import dataclass, field
from typing import List

from bpmn_tools.future import xml

def test_hello_round_trip(compare):
  with open(Path(__file__).resolve().parent / "models" / "hello.bpmn") as fp:
    expected = xmltodict.parse(fp.read())
  tree = xml.Element.from_dict(expected)
  result = tree.as_dict(with_tag=True)
  compare(result, expected)

def test_xml_element(compare):
  @dataclass
  class Leaf(xml.Element):
    _tag = "Leaf"

  @dataclass
  class Branch(xml.Element):
    _tag = "Branch"
    leafs : List[Leaf] = field(default_factory=list, metadata={"child": True})

  @dataclass
  class Trunk(xml.Element):
    _tag = "Trunk"
    branches : List[Branch] = field(default_factory=list, metadata={"child": True})

  src = """
<Trunk>
  <Branch>
    <Leaf>green</Leaf>
  </Branch>
</Trunk>
"""
  data = xmltodict.parse(src)
  tree = xml.Element.from_dict(data, classes=[Trunk, Branch, Leaf])
  assert isinstance(tree, Trunk)
  assert len(tree.children) == 1
  assert tree.children == tuple(tree.branches)
  assert isinstance(tree.branches[0], Branch)
  assert len(tree.branches[0].children) == 1
  assert tree.branches[0].children == tuple(tree.branches[0].leafs)
  assert isinstance(tree.branches[0].leafs[0], Leaf)
  assert len(tree.branches[0].leafs[0].children) == 0
  result = tree.as_dict(with_tag=True)
  compare(result, data)

def test_xml_init_children_of_different_types(compare):
  @dataclass
  class Something(xml.Element):
    pass

  @dataclass
  class Specialist(xml.Element):
    ints  : List[int]  = field(default_factory=list, metadata={"child": True})
    bools : List[bool] = field(default_factory=list, metadata={"child": True})

  something = Something()
  branch = Specialist(children=[1, 2, True, 3, False, something, 4])
  assert branch.children == tuple([something, 1, 2, 3, 4, True, False])
  assert branch.specialized_children == [1, 2, 3, 4, True, False]
  assert branch.ints  == [1, 2, 3, 4]
  assert branch.bools == [True, False]
