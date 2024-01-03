# Design

If you're interested in what's under the hood, and why, this page elaborates on this. I started writing it when I deemed the time right to move from the more ad-hoc prototyping approach to a more thought-through design, based on the initial experiences and focussing on a possible version 1.0 release in the near future - which would require at least a decent coverage of the BPMN features.

## From xmltodict to objects

The overall design that I started of with is here to stay, XML is turned into JSON using [xmltodict](https://github.com/martinblech/xmltodict), which is loaded into a generic object model, based on the `Element` class.

Given a list of additional, customized classes, that inherit from the `Element` base class, the object model can be further specialized.

So given the following XML...

```xml
<Trunk>
  <Branch>
    <Leaf>green</Leaf>
  </Branch>
</Trunk>
```

xmltodict turns this into a dict like...

```json
{
  "Trunk": {
    "Branch": {
      "Leaf": "green"
    }
  }
}
```

Feeding this into the `Element` class, using `Element.from_dict(json)` turns the dict into a small class hierarchy consisting of 

```python
Element(
  text=None,
  children=[
    Element(
      text=None,
      children=[
        Element(
          text='green',
          children=[],
          _tag='Leaf',
          _parent=...,
          _attributes={}
        )
      ],
      _tag='Branch',
      _parent=...,
      _attributes={}
    )
  ],
  _tag='Trunk',
  _parent=None,
  _attributes={}
)
```

Using the `.to_dict()` method, the `Element` hierarchy can be turned back into JSON (and using `xmltodict.unparse()` back to XML).

All of the above results in this round-trip example:

```pycon
>>> import xmltodict
>>> import json
>>> from bpmn_tools.xml import Element
>>> xml = """
... <Trunk>
...   <Branch>
...     <Leaf>green</Leaf>
...   </Branch>
... </Trunk>
... """
>>> data = xmltodict.parse(xml)
>>> print(json.dumps(data, indent=2))
{
  "Trunk": {
    "Branch": {
      "Leaf": "green"
    }
  }
}
>>> tree = Element.from_dict(data)
>>> print(tree)
Element(text=None, children=[Element(text=None, children=[Element(text='green', children=[], _tag='Leaf', _parent=..., _attributes={})], _tag='Branch', _parent=..., _attributes={})], _tag='Trunk', _parent=None, _attributes={})
>>> result = tree.as_dict(with_tag=True)
>>> print(json.dumps(result, indent=2))
{
  "Trunk": {
    "Branch": {
      "Leaf": "green"
    }
  }
}
```

## Specializing Element

Because we all don't like [anemic models](https://martinfowler.com/bliki/AnemicDomainModel.html) and the `Element` is nothing more than a generic objectivation of the JSON representation, we want to specialize `Element` using full fletched objects, raising the level of abstraction to a functional level, exposing the hierarchy of elements as their true and meaningful value.

The `Element.from_dict()` method takes an optional `classes` keyword argument, which enables you to provide a list of `Element`-specializations, to which you can add additional functionality and/or redesign the API provided by the XML.

Accessing the color currently would look something like:

```python
>>> print(tree.children[0].children[0].text)
green
```

Let's define a `Leaf` class to improve at least upon the way the data is accessed:

```pycon
>>> class Leaf(Element):
...   _tag = "Leaf"
...   @property
...   def color(self):
...     return self.text
... 
>>> tree = Element.from_dict(data, classes=[Leaf])
unmapped element: Trunk
unmapped element: Branch
>>> print(tree)
Element(text=None, children=[Element(text=None, children=[Leaf(text='green', children=[], _tag='Leaf', _parent=..., _attributes={})], _tag='Branch', _parent=..., _attributes={})], _tag='Trunk', _parent=None, _attributes={})
>>> print(tree.children[0].children[0].color)
green
```

Let's add a `Branch` class...

```pycon
>>> @dataclass
... class Branch(Element):
...   _tag = "Branch"
...   leafs : List[Leaf] = field(default_factory=list)
...   def append(self, child):
...     if isinstance(child, Leaf):
...       self.leafs.append(child)
...     else:
...       raise ValueError(f"branches only can hold leafs, not {child}")
... 
>>> tree = Element.from_dict(data, classes=[Leaf, Branch])
unmapped element: Trunk
>>> print(tree)
Element(text=None, children=[Branch(text=None, children=[], _tag='Branch', _parent=..., _attributes={}, leafs=[Leaf(text='green', children=[], _tag='Leaf', _parent=None, _attributes={})])], _tag='Trunk', _parent=None, _attributes={})
>>> print(tree.children[0].leafs[0].color)
green
>>> Branch().append(1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 9, in append
ValueError: branches only can hold leafs, not 1
```

> Note: besides our own validation in append, `Element` provides post init type checking of fields, which is not provided by stock-dataclasses:

```pycon
>>> Branch(leafs=1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 7, in __init__
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/xml.py", line 244, in __post_init__
    _validate_type(field.name, self.__dict__[field.name], list)
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/xml.py", line 230, in _validate_type
    raise TypeError(f"on {self} field `{name}` should be `{field_type}` not `{type(instance)}`")
TypeError: on Branch(text=None, children=[], _tag='Branch', _parent=None, _attributes={}, leafs=1) field `leafs` should be `<class 'list'>` not `<class 'int'>`
>>> Branch(leafs=[Leaf(),2])
_tag='Leaf', _parent=None, _attributes={}), 2]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 7, in __init__
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/xml.py", line 247, in __post_init__
    _validate_type(f"{field.name}[{index}]", item, list_type)
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/xml.py", line 230, in _validate_type
    raise TypeError(f"on {self} field `{name}` should be `{field_type}` not `{type(instance)}`")
TypeError: on Branch(text=None, children=[], _tag='Branch', _parent=None, _attributes={}, leafs=[Leaf(text=None, children=[], _tag='Leaf', _parent=None, _attributes={}), 2]) field `leafs[1]` should be `<class '__main__.Leaf'>` not `<class 'int'>`
```

## Specialization Support

Since some patterns in specialized `Element`s are so common, additional support is provided to avoid common boilerplate.

### Specializing Children

By default, all child elements go into the `children` list property. Often we want to split them up into several, type-specific lists. Above, the `Branch` class provided an `append` method that check a child's type, and if it was a `Leaf`, it was added to the `leafs` list.

To avoid this boilerplate, we can pass `metadata` to the dataclass `field` factory and have this, and more, handled for us:

```pycon
>>> import xmltodict
>>> 
>>> from dataclasses import dataclass, field
>>> from typing import List
>>> 
>>> from bpmn_tools.future import xml
>>> 
>>> src = """
... <Trunk>
...   <Branch>
...     <Leaf>green</Leaf>
...   </Branch>
... </Trunk>
... """
>>> 
>>> @dataclass
... class Leaf(xml.Element):
...   _tag = "Leaf"
...   @property
...   def color(self):
...     return self.text
...   @color.setter
...   def color(self, value):
...     self.text = value
... 
>>> @dataclass
... class Branch(xml.Element):
...   _tag = "Branch"
...   _catch_all_children = False
...   leafs : List[Leaf] = field(default_factory=list, metadata={"child": True})
... 
>>> @dataclass
... class Trunk(xml.Element):
...   _tag = "Trunk"
...   _catch_all_children = False
...   branches : List[Branch] = field(default_factory=list, metadata={"child": True})
... 
>>> data = xmltodict.parse(src)
>>> tree = xml.Element.from_dict(data, classes=[Trunk, Branch, Leaf])
>>> 
>>> tree.append(Branch())
>>> 
>>> tree.append(Leaf())
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/future/xml.py", line 114, in append
    raise ValueError(f"{self} doesn't allow for children of type {type(child)}")
ValueError: Trunk(text=None, children=(Branch(text=None, children=(Leaf(text='green', children=(), _tag='Leaf', _parent=None, _attributes={}),), _tag='Branch', _parent=None, _attributes={}, leafs=[Leaf(text='green', children=(), _tag='Leaf', _parent=None, _attributes={})]), Branch(text=None, children=(), _tag='Branch', _parent=None, _attributes={}, leafs=[])), _tag='Trunk', _parent=None, _attributes={}, branches=[Branch(text=None, children=(Leaf(text='green', children=(), _tag='Leaf', _parent=None, _attributes={}),), _tag='Branch', _parent=None, _attributes={}, leafs=[Leaf(text='green', children=(), _tag='Leaf', _parent=None, _attributes={})]), Branch(text=None, children=(), _tag='Branch', _parent=None, _attributes={}, leafs=[])]) doesn't allow for children of type <class '__main__.Leaf'>
```

### Controling Child List Validation

Through the field's metadata, it is also possible to determine if typechecking should be performed `Element`:

```pycon
>>> from bpmn_tools.future import xml
>>> from dataclasses import dataclass, field
>>> from typing import List
>>> 
>>> @dataclass
... class Something(xml.Element):
...   ints  : List[int]  = field(default_factory=list, metadata={"child": True, "typecheck": False})
... 
>>> Something(ints=["a", "b", "c"])
Something(text=None, children=('a', 'b', 'c'), _tag='Element', _parent=None, _attributes={}, ints=['a', 'b', 'c'])
>>> 
>>> @dataclass
... class SomethingElse(xml.Element):
...   ints  : List[int]  = field(default_factory=list, metadata={"child": True})
... 
>>> SomethingElse(ints=["a", "b", "c"])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 7, in __init__
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/future/xml.py", line 36, in __post_init__
    self._validate_fields()
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/future/xml.py", line 68, in _validate_fields
    _validate(f"{fld.name}[{index}]", item, list_type)
  File "/Users/xtof/Workspace/bpmn-tools/bpmn_tools/future/xml.py", line 50, in _validate
    raise TypeError(f"on {self} field `{name}` should be `{field_type}` not `{type(instance)}`")
TypeError: on SomethingElse(text=None, children=('a', 'b', 'c'), _tag='Element', _parent=None, _attributes={}, ints=['a', 'b', 'c']) field `ints[0]` should be `<class 'int'>` not `<class 'str'>
````