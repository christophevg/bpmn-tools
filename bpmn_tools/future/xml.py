"""

Class that accepts an xmltodict-style dictionary, builds a generic Element
hierarchy and can reproduce the dictionary.

The class can be overridden to create classes dealing with specialized Elements.

A Visitor allows for accessing the entire Element-hierarchy.

"""

import logging

from dataclasses import dataclass, field, fields
from typing import Optional, Union, List, Dict, ForwardRef, get_origin, get_args

import random
import string

logger = logging.getLogger(__name__)

@dataclass
class Element():
  text        : Optional[str]       = None
  children    : List["Element"]     = field(default_factory=list)
  attributes  : Dict[str,str]       = field(default_factory=dict)
  _children   : List["Element"]     = field(init=False, repr=False)
  _tag        : str                 = field(init=False, default="Element")
  _parent     : Optional["Element"] = field(init=False, default=None)
  
  _catch_all_children = True

  def __post_init__(self):
    self._split_specialized_children()
    self._validate_fields()
  
  def _split_specialized_children(self):
    children = self._children.copy()
    self._children.clear()
    self.extend(children)
  
  def _validate_fields(self):
    def _validate(name, instance, field_type):
      logger.debug(f"post init validating {name} : {field_type} = {instance}")
      if isinstance(field_type, ForwardRef):
        try:
          field_type = field_type._evaluate(globals(), locals())
        except TypeError:
          field_type = field_type._evaluate(globals(), locals(), frozenset())
      if not isinstance(instance, field_type):
        raise TypeError(f"on {self} field `{name}` should be `{field_type}` not `{type(instance)}`")

    for fld in fields(self):
      # skip our special/private properties and those marked as not to typecheck
      if fld.name in ["children", "_tag", "_parent"] or \
         not fld.metadata.get("typecheck", True):
        continue
      # perform runtime typecheck
      base_type = get_origin(fld.type)
      type_args = get_args(fld.type)
      if base_type is list:
        _validate(fld.name, self.__dict__[fld.name], list)
        list_type = type_args[0]
        for index, item in enumerate(self.__dict__[fld.name]):
          _validate(f"{fld.name}[{index}]", item, list_type)
      elif base_type is Union:
        # Optiona[...] == Union[..., NoneType]
        if len(type_args) == 2 and type_args[1] is None.__class__:
          if self.__dict__[fld.name] is not None:
            _validate(fld.name, self.__dict__[fld.name], type_args[0])
        else:
          logger.warning("type checking for Union is not (yet) implemented")
      elif base_type is None:
        _validate(fld.name, self.__dict__[fld.name], fld.type)
      else:
        logger.warning(f"type checking for {base_type} is not (yet) implemented")

  @property
  def children(self):                                      # readonly tuple
    return tuple(self._children) + tuple(self.specialized_children)

  @children.setter
  def children(self, new_children):
    if type(new_children) is property:
      new_children = []
    self._children = new_children

  @property
  def specialized_children(self):
    return [
      child
      for fld in self.specialized_children_fields
      for child in self.__dict__[fld.name]
    ]

  @property
  def specializations(self):
    return {
      get_args(fld.type)[0] : self.__dict__[fld.name]
      for fld in self.specialized_children_fields
    }

  @property
  def specialized_children_fields(self):
    for fld in fields(self):
      if fld.metadata.get("child", False):
        yield fld

  def append(self, child):
    if isinstance(child, Element):
      child._parent = self
    
    # find specialization
    for fld_type, fld in self.specializations.items():
      if type(child) is fld_type:
        fld.append(child)
        return
    # default
    if self._catch_all_children:
      self._children.append(child)
    else:
      raise ValueError(f"{self} doesn't allow for children of type {type(child)}")

  def extend(self, children):
    for child in children:
      self.append(child)
    return self

  @property
  def root(self):
    if self._parent:
      return self._parent.root
    else:
      return self

  def __setitem__(self, name, value):
    self.attributes[name] = value

  def __getitem__(self, name):
    try:
      return self.attributes[name]
    except KeyError:
      return None

  def __getattr__(self, name):
    return self[name]

  def __eq__(self, other):
    return self.text == other.text and \
           self.attributes == other.attributes and \
           self.children == other.children

  def find(self, key, value, skip=None, stack=None):
    if stack is None:
      stack = []

    if self in stack:
      logger.warning("avoided recursion")
      return None

    if self is skip:
      return None

    # do I have the key=value attribute?
    try:
      if self.attributes[key] == value:
        return self
    except KeyError:
      pass
    
    # recurse down children
    for child in self.children:
      match = child.find(key, value, skip=skip, stack=stack+[self])
      if match:
        return match

    return None

  def children_oftype(self, cls, recurse=False):
    children = []
    for child in self.children:
      if isinstance(child, cls) or isinstance(child.wrapped, cls):
        children.append(child)
      if recurse:
        children.extend(child.children_oftype(cls, recurse=True))
    return children

  def as_dict(self, with_tag=False):
    # collect attributes
    definition = {
      f"@{key}" : value for key, value in self.attributes.items() if value is not None
    }

    # collect text
    if self.text:
      definition["#text"] = self.text

    # collect children
    for child in self.children:
      d = child.as_dict()
      try:
        definition[child._tag].append(d)
      except KeyError:
        definition[child._tag] = d
      except AttributeError:
        definition[child._tag] = [ definition[child._tag] , d ]

    # prune text-only tag
    if list(definition.keys()) == [ "#text" ]:
      definition = definition["#text"]

    # prune empty tag
    if definition == {}:
      definition = None

    if with_tag:
      return { self._tag : definition }
    else:
      return definition
  
  @classmethod
  def mapped_class(cls, tag, classes):
    if classes:
      for clazz in classes:
        try:
          if clazz._tag == tag:
            return clazz
        except AttributeError:
          pass
    return cls
  
  @classmethod
  def from_dict(cls, d, classes=None, depth=0, raise_unmapped=False):
    element_type, element_definition = list(d.items())[0]
    element_class = cls.mapped_class(element_type, classes)
    if element_class == cls and classes:
      if raise_unmapped:
        raise ValueError(f"unmapped element: {element_type}")
      else:
        logger.warning(f"unmapped element: {element_type}")
    element = element_class()
    element._tag = element_type
    
    if isinstance(element_definition, str):
      element_definition = { "#text" : element_definition }
    
    for key, defintions in element_definition.items():
      if key[0] == "@":
        element.attributes[key[1:]] = defintions
      elif key == "#text":
        element.text = defintions
      else:
        if not isinstance(defintions, list):
          defintions = [ defintions ]
        for definition in defintions:
          if definition is None:
            definition = {}
          elif isinstance(definition, str):
            definition = { "#text" : definition }
          child = cls.from_dict(
            { key : definition }, classes=classes, depth=depth+1,
            raise_unmapped=raise_unmapped
           )
          assert child is not element
          element.append(child)

    return element

  def accept(self, visitor):
    with visitor:
      visitor.visit(self)
      for child in self.children:
        try:
          child.accept(visitor)
        except TypeError:
          raise ValueError(f"accept() on {child} is missing argument")

@dataclass
class IdentifiedElement(Element):
  """
  IdentifiedElement adds an explicit construction argument `id` to attributes.
  """
  id : Optional[str] = None 
  
  def __post_init__(self):
    if self.id is None:
      random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
      self.id = f"{self.__class__.__name__.lower()}_{random_str}"
    self["id"] = self.id

  @property 
  def id(self):
    return self["id"]

  @id.setter
  def id(self, new_id):
    if type(new_id) is property:
      new_id = None
    self["id"] = new_id
