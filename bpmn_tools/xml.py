"""

Class that accepts an xmltodict-style dictionary, builds a generic Element
hierarchy and can reproduce the dictionary.

The class can be overridden to create classes dealing with specialized Elements.

A Visitor allows for accessing the entire Element-hierarchy.

"""

class Element():
  __tag__     = "Element"

  def __init__(self, **kwargs):
    self._children   = []
    self._parent     = None
    self._attributes = {}
    self.text        = None

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

  def find(self, key, value):
    # do I have the key=value attribute?
    try:
      if self._attributes[key] == value:
        return self
    except KeyError:
      pass
    
    # recurse down children
    for child in self._children:
      match = child.find(key, value)
      if match:
        return match

    return None

  def append(self, child):
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

  def children_oftype(self, cls):
    return [ child for child in self._children if isinstance(child, cls) ]

  def as_dict(self, with_tag=False):
    # collect attributes
    definition = {
      f"@{key}" : value for key, value in self.attributes.items()
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
        if clazz.__tag__ == tag:
          return clazz
    return Element
  
  @classmethod
  def from_dict(cls, d, classes=None, depth=0):
    element_type, element_definition = list(d.items())[0]
    element_class = cls.mapped_class(element_type, classes)
    element = element_class()
    element.__tag__ = element_type
    
    for key, defintions in element_definition.items():
      if key[0] == "@":
        element._attributes[key[1:]] = defintions
      elif key == "#text":
        element.text = defintions
      else:
        if type(defintions) != list:
          defintions = [ defintions ]
        for definition in defintions:
          if definition is None:
            definition = {}
          elif type(definition) is str:
            definition = { "#text" : definition }
          child = Element.from_dict({ key : definition }, classes=classes, depth=depth+1 )
          assert child != element
          element.append(child)

    return element

  def accept(self, visitor):
    with visitor:
      visitor.visit(self)
      for child in self.children:
        child.accept(visitor)

# decorator based visitor, inspired by https://stackoverflow.com/a/28398903

def _qualname(obj):
  """Get the fully-qualified name of an object (including module)."""
  return obj.__module__ + '.' + obj.__qualname__

def _declaring_class(obj):
  """Get the name of the class that declared an object."""
  name = _qualname(obj)
  return name[:name.rfind('.')]

_methods = {}

def _visitor_impl(self, arg):
  """Actual visitor method implementation."""
  try:
    method = _methods[(_qualname(type(self)), type(arg))]
    return method(self, arg)
  except KeyError:
    pass
  return Visitor.visit(self, arg) 

def visiting(arg_types):
  """Decorator that creates a visitor method."""
  if type(arg_types) != list:
    arg_types = [ arg_types ]
  def decorator(fn):
    declaring_class = _declaring_class(fn)
    for arg_type in arg_types:
      _methods[(declaring_class, arg_type)] = fn
    return _visitor_impl
  return decorator

class Visitor:
  def __init__(self):
    self.depth = -1

  def __enter__(self):
    self.depth += 1
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    self.depth -= 1

  def visit(self, visited):
    pass

class PrintingVisitor(Visitor):
  def visit(self, visited):
    print(f"{'   '*self.depth}{visited}")
