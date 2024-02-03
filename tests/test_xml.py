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
  class Trunk(xml.Element):
    _tag = "Trunk"
    branches : List["Branch"] = field(default_factory=list, metadata={"child": True})

  @dataclass
  class Branch(xml.Element):
    _tag = "Branch"
    leafs : List["Leaf"] = field(default_factory=list, metadata={"child": True})

  @dataclass
  class Leaf(xml.Element):
    _tag = "Leaf"

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

def test_ensure_root_is_available():
  @dataclass
  class Something(xml.Element):
    pass

  @dataclass
  class SomeContainer(xml.Element):
    values : List[Something] = field(**xml.children)
  
  something = Something()
  container = SomeContainer()
  container.append(something)
  assert something.root is container
  assert container.root is container

def test_ensure_unspecialized_attributes_are_managed():
  element = xml.Element()
  assert element.attributes == {}

  try:
    element["hello"]
    assert False, "element should raise KeyError for uninitialized attribute"
  except KeyError:
    pass
  element["hello"] = "world"
  assert element["hello"] == "world"
  try:
    element.hello
    assert False, "element should raise AttributeError for unspecialized attribute"
  except AttributeError:
    pass
  assert element.attributes == {"hello" : "world"}

def test_ensure_initialization_of_attributes():
  print("start")
  element = xml.Element(attributes={"hello": "world"})
  print(element)
  print("stop")

  assert element["hello"] == "world"
  assert element.attributes == {"hello" : "world"}

def test_finding_elements():
  element1 = xml.Element(attributes={"name" : "element 1"})
  element2 = xml.Element(attributes={"name" : "element 2"})
  element3 = xml.Element(attributes={"name" : "element 3"})

  element1.append(element3)
  element2.append(element3)

  assert element1.find("name", "element 3") is element3

def test_avoiding_finding_recursion(caplog):
  caplog.set_level(logging.WARNING)

  element1 = xml.Element(attributes={"name" : "element 1"})
  element2 = xml.Element(attributes={"name" : "element 2"})
  element3 = xml.Element(attributes={"name" : "element 3"})

  element1.append(element2)
  element2.append(element3)
  element3.append(element1)

  assert element1.find("name", "element 4") is None
  assert "avoided recursion" in caplog.text

def test_skipping_of_element_in_hierarchy():
  element1 = xml.Element(attributes={"name" : "element 1"})
  element2 = xml.Element(attributes={"name" : "element 2"})
  element3 = xml.Element(attributes={"name" : "element 3"})

  element1.append(element2)
  element2.append(element3)

  assert element1.find("name", "element 3") is element3
  assert element1.find("name", "element 3", skip=element2) is None

def test_ignore_unknown_attributes_on_find():
  element1 = xml.Element(attributes={"name" : "element 1"})
  element2 = xml.Element(attributes={"name" : "element 2"})
  element3 = xml.Element(attributes={"named" : "element 3"})

  element1.append(element2)
  element2.append(element3)

  assert element1.find("named", "element 3") is element3

def test_identified_element_creation_and_update():
  element = xml.IdentifiedElement(id="test-id")
  assert element.id == "test-id"
  assert element["id"] == "test-id"
  element.id = "test-id-2"
  assert element.id == "test-id-2"
  assert element["id"] == "test-id-2"
  element["id"] = "test-id-3"
  assert element.id == "test-id-3"
  assert element["id"] == "test-id-3"

def test_identified_element_id_generation():
  element = xml.IdentifiedElement()
  assert len(element.id) == len("identifiedelement_") + 8
  assert element.id[:len("identifiedelement_")] == "identifiedelement_"
