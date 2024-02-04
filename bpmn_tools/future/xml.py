"""

Class that accepts an xmltodict-style dictionary, builds a generic Element
hierarchy and can reproduce the dictionary.

The class can be overridden to create classes dealing with specialized Elements.

A Visitor allows for accessing the entire Element-hierarchy.

"""

import logging

import random
import string

from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, Union, ForwardRef, get_args, get_origin

logger = logging.getLogger(__name__)

class ElementList(list):
  """
  ElementList is a list with the additional functionality that it maintains
  the _parent property on its items, which are expected to be of type Element,
  thus having that property.
  """
  def __init__(self, iterable=None):
    if not iterable:
      iterable = []
    super().__init__(iterable)
    self._parent = None
  
  @property
  def parent(self):
    return self._parent
  
  @parent.setter
  def parent(self, new_parent):
    self._parent = new_parent
    self._set_parent_on_all()

  def _set_parent_on_all(self):
    for item in self:
      self._set_parent(item)

  def _set_parent(self, item):
    try:
      item._parent = self._parent
    except AttributeError:
      # the item doesn't have a _parent 🤷‍♂️
      pass

  def _unset_parent(self, item):
    try:
      item._parent = None
    except AttributeError:
      # the item doesn't have a _parent 🤷‍♂️
      pass

  def __setitem__(self, index, item):
    self._set_parent(item)
    super().__setitem__(index, item)

  def __delitem__(self, index):
    self[index]._parent = None
    super().__delitem__(index)

  def clear(self):
    for item in self:
      self._unset_parent(item)
    super().clear()

  def remove(self, item):
    self._unset_parent(item)
    super().remove(item)

  def pop(self, item=None):
    item = super().pop(item)
    self._unset_parent(item)
    return item

  def insert(self, index, item):
    self._set_parent(item)
    super().insert(index, item)

  def append(self, item):
    self._set_parent(item)
    super().append(item)

  def extend(self, other):
    for item in other:
      self._set_parent(item)
    super().extend(other)

class ElementProperty():
  """
  ElementProperty wraps access to an property containing an Element, ensuring
  that the Element has a parent, set to the owner of the property.
  """
  def __set_name__(self, type, name):
    self.name = name
    self.attrname = f"_{name}_value"
  
  def __get__(self, parent, cls):
    return getattr(parent, self.attrname)
      
  def __set__(self, parent, element):
    if isinstance(element, type(self)):
      element = None
    else:
      element._parent = parent
    setattr(parent, self.attrname, element)
    
  def __delete__(self, instance):
    getattr(instance, self.attrname)._parent = None
    delattr(instance, self.attrname)

# utility argument sets for supplying to field()
# e.g.
#   field(**xml.children)  to store children of the type mentioned in List[type]
#   field(**xml.child)     to store a child of the type mentioned 
#   field(**xml.attribute) to store an attribute with the name of the field

children = { "default_factory" : ElementList }

class ChildProperty(Mapping):
  def __len__(self):
    return 1

  def __getitem__(self, k):
    return ElementProperty()

  def __iter__(self):
    return iter({ "default" : ElementProperty() })

child = ChildProperty()

attribute = { "metadata" : { "attribute" : True }}

@dataclass
class Element():
  """
  Element represents a generic XML tag, with other XML tags as children and
  attributes.
  
  It can be subclassed to create specific Elements. These Elements can be hosted
  in specialized children collections.
  
  """
  children    : List["Element"]     = field()  # only used for init generation
  localns     : Dict                = field(default_factory=dict)
  attributes  : Dict[str,str]       = field(default_factory=dict)
  text        : Optional[str]       = field(default=None)
  _children   : List["Element"]     = field(init=False, repr=False)
  _attributes : Dict[str,str]       = field(init=False)
  _tag        : str                 = field(init=False, default="Element")
  _parent     : Optional["Element"] = field(init=False, default=None, repr=False)

  _catch_all_children = True

  def __post_init__(self):
    # dataclasses are great, still we need to do some additional housekeeping
    
    # during init, the default factory (ElementList) can't be provided with
    # a reference to the parent/self - we need to do that post_init
    # _children is our "private" generic children collection, which isn't
    # initialized using the factory, else we would lose the initialized
    # children from __init__
    for fld in fields(self):
      if fld.default_factory is ElementList or fld.name == "_children":
        # ensure that the value stored in the property actually IS an
        # ElementList in case it is still a list, which happens with
        # fields that are defined List[Element]
        if type(self.__dict__[fld.name]) is list: #noqa
          self.__dict__[fld.name] = ElementList(self.__dict__[fld.name])
        self.__dict__[fld.name].parent = self
    
    # we use a pattern of field-sets to allow for nice name-based initialization
    # generated by the dataclass, and access through the same name-based getter.
    # this is a multi-step process.
    # after initialization, children and attributes are stored in _children and
    # _attributes and need to be "distributed" (optionally) to specialized
    # collections in other fields (on subclasses)
    self._adopt_attributes()
    self._adopt_children()
    
    # finally also validate all fields
    self._validate_fields()

  def _validate_fields(self):
    # check that all fields have the correct type

    def _validate(name, instance, field_type):
      logger.debug(f"post init validating {name} : {field_type} = {instance}")
      field_type = self._deref(field_type)
      if not isinstance(instance, field_type):
        raise TypeError(f"on {self} field `{name}` should be `{field_type}` not `{type(instance)}`")

    for fld in fields(self):
      # skip our special/private properties and those marked as not to typecheck
      if fld.name in ["children", "_tag", "_parent", "localns"] or \
         not fld.metadata.get("typecheck", True):
        continue
      # perform runtime typecheck
      base_type = get_origin(fld.type)
      type_args = get_args(fld.type)
      if base_type is list:
        try:
          _validate(fld.name, self.__dict__[fld.name], list)
          list_type = type_args[0]
          for index, item in enumerate(self.__dict__[fld.name]):
            _validate(f"{fld.name}[{index}]", item, list_type)
        except KeyError:
          pass # when no value provided through the init
      elif base_type is Union:
        # Optiona[...] == Union[..., NoneType]
        if len(type_args) == 2 and type_args[1] is None.__class__:
          try:
            if self.__dict__[fld.name] is not None:
              _validate(fld.name, self.__dict__[fld.name], type_args[0])
          except KeyError:
            pass # when no value provided through the init
        else:
          logger.warning("type checking for Union is not (yet) implemented")
      elif base_type is None:
        try:
          _validate(fld.name, self.__dict__[fld.name], fld.type)
        except KeyError:
          pass # when no value provided through the init
      else:
        logger.warning(f"type checking for {base_type} is not (yet) implemented")
        # logger.warning(f" => {fld}")

  # Children Support
  
  # Children are by default stored in the children property. Fields can be
  # configured to be used as specialized collection of certain children-types.

  @property
  def children(self):
    # we return a readonly tuple of the generic children and the specialized
    return tuple(self._children) + tuple(self.specialized_children)

  @property
  def specialized_children(self):
    # returns the children that are stored in specialized collections or
    # element properties
    children = []
    for fld in self.specialized_children_fields:
      value = self._get_value(fld)
      if isinstance(value, list):
        for child in value:
          children.append(child)
      elif value is not None:
        children.append(value)
    return children

  @children.setter
  def children(self, new_children):
    # a bit of a trick setup, where we use the children field to have a
    # children __init__ argument, which is then routed through this setter
    # to be stored in the _children field
    if type(new_children) is property:
      new_children = []
    if type(new_children) is not ElementList:
      new_children = ElementList(new_children)
    self._children = new_children

  def _adopt_children(self):
    # after initialization, children setter has accepted init children and
    # put them in _children. we now need to go through the list and "adopt"
    # them, which might mean that they are put in a specialized collection
    # this basically automates adding them "manually"
    children = self._children.copy()
    self._children.clear()
    self.update(children)

  @property
  def specializations(self):
    # returns a mapping from a Element-sub-type to the corresponding collection
    # this allows for `self.specializations[type(element)].append(element)`
    return {
      self._deref(get_args(fld.type)[0]) : self._get_value(fld)
      for fld in self.specialized_children_fields
    }

  def _get_value(self, fld):
    try:
      return self.__dict__[fld.name]
    except KeyError:
      # LOOK INTO THIS
      # apparently ElementProperty aren't added to the __dict__ like 
      # ElementLists, so we currently store them as _<name>_value
      return self.__dict__[f"_{fld.name}_value"]

  @property
  def specialized_children_fields(self):
    # returns all fields that store specialized children, lists and properties
    yield from self.specialized_children_list_fields
    yield from self.specialized_child_fields
  
  @property
  def specialized_children_list_fields(self):
    # returns all fields that store lists of specialized children
    for fld in fields(self):
      if fld.default_factory is ElementList:
        yield fld

  @property
  def specialized_child_fields(self):
    # returns all fields that store a specialized child as a property
    for fld in fields(self):
      if type(fld.default) is ElementProperty:
        yield fld

  # children property is a read-only tuple, so we provide mutations on Element

  def update(self, children):
    # add all children
    for child in children:
      self.add(child)
    return self

  def add(self, child):
    # add a single child, optionally to the correct specialized collection
    collection = self._collection_of(child)
    if child not in collection:
      collection.append(child)
    return self

  def remove(self, child):
    # remove a child, optionally from its specialized collection
    self._collection_of(child).remove(child)
    return self
    
  def _collection_of(self, child):
    # find a specialized child collection
    try:
      collection = self.specializations[type(child)]
    except KeyError:
      # or default to the generic/catch-all children collection
      # IF catch-all is allowed
      if self._catch_all_children:
        collection = self._children
      else:
        raise ValueError(f"{self} doesn't accept children of type {type(child)}")
    return collection

  def clear(self):
    # clears all children in collections and properties
    # generic children
    self._children.clear()
    # specialized children collections
    for fld in self.specialized_children_list_fields:
      self.__dict__[fld.name].clear()
    # specialized children properties
    for fld in self.specialized_child_fields:
      self.__dict__[fld.name] = None
    return self

  @property
  def root(self):
    # root continues to bubble upwards the parents tree and stops when there
    # is no more parent, hence we are the root
    if self._parent:
      return self._parent.root
    return self

  # Attributes Support

  # just like children, attributes can be stored in specialized fields, in stead
  # of in the generic/catch-all attributes property
  
  @property
  def attributes(self):
    # combine specialized attributes and _attributes
    attrs = {
      fld.name : getattr(self, fld.name)
      for fld in self.specialized_attributes_fields
    }
    attrs.update(self._attributes)
    return attrs

  @attributes.setter
  def attributes(self, new_attributes):
    # a bit of a trick setup, where we use the attributes field to have a
    # attributes __init__ argument, which is then routed through this setter
    # to be stored in the _attributes field
    if type(new_attributes) is property:
      new_attributes = {}
    self._attributes = new_attributes

  def _adopt_attributes(self):
    # after initialization, attibutes setter has accepted init attributes and
    # put them in _attributes. we now need to go throught he list and "adopt"
    # them. this basically automates adding them one-by-one "manually"
    attributes = self._attributes.copy()
    self._attributes.clear()
    for key, value in attributes.items():
      self[key] = value

  @property
  def specialized_attributes_fields(self):
    # returns the fields that store specialized attributes, which means that
    # they hold an attribute with the field's name, so it isn't stored in the
    # generc attributes collection
    for fld in fields(self):
      if fld.metadata.get("attribute", False):
        yield fld

  def __getitem__(self, name):
    # allows for `value = element["attribute"]` access to attribute values
    # check if we have an specialized attribute
    for fld in self.specialized_attributes_fields:
      if fld.name == name:
        return getattr(self, name)
    # else try from unspecialized attributes
    return self._attributes[name]

  def __setitem__(self, name, value):
    # allows for `element["attribute"] = value` manipulation of attributes
    # check if we have an specialized attribute
    for fld in self.specialized_attributes_fields:
      if fld.name == name:
        setattr(self, name, value)
        return
    # unspecialized attributes go in the general pool/dict
    self._attributes[name] = value

  # functionality
  
  def __eq__(self, other):
    # two elements are equal if their text, attributes and children are equal
    return self.text == other.text and \
           self.attributes == other.attributes and \
           self.children == other.children

  def find(self, key, value, skip=None, stack=None):
    """
    find a child that has the attribute/value pair key=value
    """
    if stack is None:
      stack = []

    if self in stack:
      logger.warning("avoided recursion")
      return None

    if self is skip:
      return None

    # do I have the key=value attribute?
    try:
      if self[key] == value:
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
    # return all chilcren, filtered based on a given (sub)class
    # TODO: still in use? -> .wrapped?
    children = []
    for child in self.children:
      if isinstance(child, cls) or isinstance(child.wrapped, cls):
        children.append(child)
      if recurse:
        children.extend(child.children_oftype(cls, recurse=True))
    return children

  def as_dict(self, with_tag=False):
    """
    returns the Element hierarchy as a dict, compatible with xmltodict
    """
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
  def from_dict(cls, d, classes=None, depth=0, raise_unmapped=False):
    """
    given a dict, produced by e.g. `xmltodict.parse(xml)`, unmarshall the dict
    into a Element-hierarchy, using provided classes. 
    """
    if classes is None:
      classes = {} 
    # parse out the top-level element of the dict
    # { element-name : { element-definition } }
    element_type, element_definition = list(d.items())[0]

    def mapped_class(tag, classes):
      if classes:
        for clazz in classes:
          try:
            if clazz._tag == tag:
              return clazz
          except AttributeError:
            pass
      # default
      return Element

    # determine class based on the element/tag-name
    element_class = mapped_class(element_type, classes)
    
    # is the class is Element we don't have a mapping (if classes were provided)
    if element_class == cls and classes:
      if raise_unmapped:
        raise ValueError(f"unmapped element: {element_type}")
      else:
        logger.warning(f"unmapped element: {element_type}")

    # construct an element using the (specialized) class
    # we inject the classes, which might not be in globals() or locals()
    # without this additional local namespace, the element would not be able
    # to dereference ForwardRefs (see _deref)
    element = element_class(localns={ clazz.__name__ : clazz for clazz in classes })
    element._tag = element_type   # in case of no mapping and generic Element
    
    # unpack a simple string into a text attrbute
    if isinstance(element_definition, str):
      element_definition = { "#text" : element_definition }
    
    # process the definition
    for key, defintions in element_definition.items():
      # real attributes are prefixed with an "@"
      if key[0] == "@":
        element[key[1:]] = defintions

      # textual child-content is kept in the "#text" attribute
      elif key == "#text":
        element.text = defintions

      # process all other items as children
      else:
        if not isinstance(defintions, list):
          defintions = [ defintions ]
        # identical tags are combined into a list
        # e.g. <root><branch>1</branch><branch>2</branch></root>
        #      { "root": { "branch" : [ "1", "2" ] } } 
        for definition in defintions:
          if definition is None:
            definition = {}
          elif isinstance(definition, str):
            definition = { "#text" : definition }

          # recurse futher down the dict, creating children
          element.add(
            cls.from_dict(
              { key : definition },
              classes=classes,
              depth=depth+1,
              raise_unmapped=raise_unmapped
           )
         )
    return element

  def accept(self, visitor):
    # accepts a visitor
    with visitor:
      visitor.visit(self)
      for child in self.children:
        try:
          child.accept(visitor)
        except TypeError:
          raise ValueError(f"accept() on {child} is missing argument")

  # utility methods

  def _deref(self, field_type):
    # is ForwardRefs are in use, we de-reference them
    # credits: https://stackoverflow.com/a/76152697
    if isinstance(field_type, ForwardRef):
      args = (globals(), {**locals(), **self.localns})
      try:
        return field_type._evaluate(*args) # < py39
      except TypeError:
        return field_type._evaluate(*args, frozenset())
    return field_type

@dataclass
class IdentifiedElement(Element):
  """
  IdentifiedElement adds an `id` attribute, with a random default value
  """
  id : Optional[str] = field(default=None, **attribute)
  
  def __post_init__(self):
    super().__post_init__()
    if self.id is None:
      random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
      self.id = f"{self.__class__.__name__.lower()}_{random_str}"
