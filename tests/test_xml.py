import logging

from pathlib import Path
import xmltodict

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

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

def test_field_metadata_typecheck_flag():
  @dataclass
  class Something(xml.Element):
    ints  : List[int] = field(default_factory=list, metadata={"child": True, "typecheck": False})
  Something(ints=["a", "b", "c"])

  @dataclass
  class SomethingElse(xml.Element):
    ints  : List[int]  = field(default_factory=list, metadata={"child": True})
  try:
    SomethingElse(ints=["a", "b", "c"])
    assert False, "default metadata typecheck not enforced"
  except TypeError:
    pass

def test_typecheck_of_simple_type():
  @dataclass
  class Something(xml.Element):
    value : str = ""

  Something()
  Something(value="hello")
  try:
    Something(value=True)
    assert False, "typecheck should fail for boolean"
  except TypeError:
    pass

def test_typecheck_of_optional():
  @dataclass
  class Something(xml.Element):
    value : Optional[str] = None

  Something()
  Something(value="hello")
  Something(value=None)
  try:
    Something(value=True)
    assert False, "typecheck should fail for boolean"
  except TypeError:
    pass

def test_unimplemented_typecheck_of_union(caplog):
  caplog.set_level(logging.WARNING)
  @dataclass
  class Something(xml.Element):
    value : Union[str, int] = 1

  Something()
  assert "type checking for Union is not (yet) implemented" in caplog.text

def test_unimplemented_typecheck_of_other_base_type(caplog):
  caplog.set_level(logging.WARNING)
  @dataclass
  class Something(xml.Element):
    value : Dict[str, str] = field(default_factory=dict)

  Something()
  assert "type checking for <class 'dict'> is not (yet) implemented" in caplog.text

def test_strict_validation_on_append():
  @dataclass
  class Something(xml.Element):
    _catch_all_children = False
    values : List[int] = field(default_factory=list, metadata={"child": True})

  try:
    Something(children=[1, 2, "blah"])
    assert False, "children other than int and Element should not be validated"
  except ValueError:
    pass

def test_ensure_parent_link_is_set():
  @dataclass
  class Something(xml.Element):
    pass

  @dataclass
  class SomeContainer(xml.Element):
    values : List[Something] = field(default_factory=list, metadata={"child": True})
  
  something = Something()
  container = SomeContainer()
  container.append(something)
  assert something._parent is container
