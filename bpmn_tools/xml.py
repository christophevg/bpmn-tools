"""

Class that accepts an xmltodict-style dictionary, builds a generic Element
hierarchy and can reproduce the dictionary.

The class can be overridden to create classes dealing with specialized Elements.

A Visitor allows for accessing the entire Element-hierarchy.

"""

import logging

import random
import string

logger = logging.getLogger(__name__)

class Element():
  __tag__     = "Element"

  def __init__(self, text=None, **kwargs):
    self._children   = []
    self._parent     = None
    self._attributes = {}
    self._text       = text

  @property
  def text(self):
    return self._text
  
  @text.setter
  def text(self, value):
    self._text = value

  def __repr__(self):
    label = f"{self.__class__.__name__}"
    if self.attributes:
      label += f"({self.attributes})"
    if self.text:
      label += f" : {self.text}"
    return label

  def __setitem__(self, name, value):
    self._attributes[name] = value

  def __getitem__(self, name):
    try:
      return self._attributes[name]
    except KeyError:
      return None

  def __getattr__(self, name):
    return self[name]

  @property
  def root(self):
    if self._parent:
      return self._parent.root
    else:
      return self

  def find(self, key, value, skip=None, stack=None):
    if stack is None:
      stack = []

    if self in stack:
      logger.warn("avoided recursion")
      return None

    if self is skip:
      return None

    # do I have the key=value attribute?
    try:
      if self._attributes[key] == value:
        return self
    except KeyError:
      pass
    
    # recurse down children
    for child in self.children:
      match = child.find(key, value, skip=skip, stack=stack+[self])
      if match:
        return match

    return None

  def append(self, child):
    if not child:
      raise ValueError(f"invalid child: {child}")
    self._children.append(child)
    child._parent = self
    return self

  def extend(self, children):
    for child in children:
      self.append(child)
    return self

  @property
  def attributes(self):
    return self._attributes

  @property
  def children(self):
    return self._children

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
        definition[child.__tag__].append(d)
      except KeyError:
        definition[child.__tag__] = d
      except AttributeError:
        definition[child.__tag__] = [ definition[child.__tag__] , d ]

    # prune text-only tag
    if list(definition.keys()) == [ "#text" ]:
      definition = definition["#text"]

    # prune empty tag
    if definition == {}:
      definition = None

    if with_tag:
      return { self.__tag__ : definition }
    else:
      return definition
  
  @staticmethod
  def mapped_class(tag, classes):
    if classes:
      for clazz in classes:
        try:
          if clazz.__tag__ == tag:
            return clazz
        except AttributeError:
          pass
    return Element
  
  @classmethod
  def from_dict(cls, d, classes=None, depth=0, raise_unmapped=False):
    element_type, element_definition = list(d.items())[0]
    element_class = cls.mapped_class(element_type, classes)
    if element_class == Element and classes:
      if raise_unmapped:
        raise ValueError(f"unmapped element: {element_type}")
      else:
        logger.warning(f"unmapped element: {element_type}")
    element = element_class()
    element.__tag__ = element_type
    
    if isinstance(element_definition, str):
      element_definition = { "#text" : element_definition }
    
    for key, defintions in element_definition.items():
      if key[0] == "@":
        element._attributes[key[1:]] = defintions
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
          child = Element.from_dict(
            { key : definition }, classes=classes, depth=depth+1,
            raise_unmapped=raise_unmapped
           )
          assert child != element
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

class IdentifiedElement(Element):
  def __init__(self, id=None, **kwargs):
    super().__init__(**kwargs)
    if id is None:
      random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
      id = f"{self.__class__.__name__.lower()}_{random_str}"
    self["id"] = id
