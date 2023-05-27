"""

Class that accepts an xmltodict-style dictionary, builds a generic Element
hierarchy and can reproduce the dictionary.

The class can be overridden to create classes dealing with specialized Elements.

An ElementVisitor allows for accessing the entire Element-hierarchy.

"""

class Element():
  __tag__ = "Element"
  def __init__(self, **kwargs):
    """
      Accepts an xmltodict value:
      kwargs = {
        "@attribute" : "value",
        "single_element_tag" : { ... },
        "multiple_element_tag : [
          { ... }
        ]
      }
    """
    self._children   = []
    self._parent     = None
    self._attributes = {}
    self.text        = None

    for key, value in kwargs.items():
      if key[0] == "@":
        self._attributes[key[1:]] = value
      elif key == "#text":
        self.text = value
      else:
        if type(value) != list:
          value = [ value ]
        for definition in value:
          if definition is None:
            definition = {}
          elif type(definition) is str:
            definition = { "#text" : definition }
          self.append(Element.from_dict({ key : definition } ))

  def __repr__(self):
    label = f"{self.__class__.__name__}"
    if self.attributes:
      label += f"({self.attributes})"
    if self.text:
      label += f" : {self.text}"
    return label

  def __getattr__(self, name):
    try:
      return self._attributes[name]
    except KeyError:
      return None

  @property
  def root(self):
    if self._parent:
      return self._parent.root
    else:
      return self

  def find(self, key, value):
    # do I have the key=value attribute?
    try:
      if self.attributes[key] == value:
        return self.attrbutes[key]
    except KeyError:
      pass
    
    # recurse down children
    for child in self._children:
      match = child.find(id)
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
  def _more_attributes(self):
    return {}
  
  @property
  def attributes(self):
    return { **self._attributes, **self._more_attributes }

  @property
  def _more_children(self):
    return []

  @property
  def children(self):
    return self._children + self._more_children

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
  
  @classmethod
  def from_dict(cls, d):
    for element_type, element_definition in d.items():
      element = Element(**element_definition)
      element.__tag__ = element_type
      return element

  def accept(self, visitor):
    with visitor:
      visitor.visit(self)
      for child in self.children:
        child.accept(visitor)

class Visitor:
  def __init__(self):
    self.depth = -1

  def __enter__(self):
    self.depth += 1
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    self.depth -= 1

  def visit(self, visited):
    print(f"{'   '*self.depth}{visited}")
