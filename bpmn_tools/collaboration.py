"""
  Classes representing the different parts of a BPMN file.
"""

from . import xml

from .extensions import Extension, ExtensionElements, PropertyExtension

class Participant(xml.Element):
  __tag__        = "bpmn:participant"
  __horizontal__ = True

  def __init__(self, name="participant", process=None, id="participant"):
    super().__init__()
    self["id"]   = id
    self["name"] = name
    self._process = process
    self.x      = 0
    self.y      = 0
    self.height = 125
    self.width  = 600
  
  @property
  def process(self):
    if self._process:
      return self._process
    elif self["processRef"]:
      return self.root.find("id", self["processRef"])
    return None
  
  @property
  def attributes(self):
    attributes = super().attributes.copy()
    if self.process:
      attributes.update({
        "processRef" : self.process["id"]
      })
    return attributes

class Collaboration(xml.Element):
  __tag__ = "bpmn:collaboration"

  def __init__(self, id="collaboration"):
    super().__init__()
    self["id"] = id
  
  @property
  def extension_properties(self):
    return {
      extension.name : extension.value
      for extension in self.children_oftype(cls=PropertyExtension, recurse=True)
    }
  
  def append(self, child):
    # accept short-hand appending of Extensions, wrapping them in
    # ExtensionElements > [...]Properties
    if isinstance(child, Extension):
      try:
        extension_elements = self.children_oftype(ExtensionElements)[0]
      except Exception:
        extension_elements = ExtensionElements()
        super().append(extension_elements)
      try:
        group = extension_elements.children_oftype(child.__extension_group__)[0]
      except Exception:
        group = child.__extension_group__()
        extension_elements.append(group)
    
      group.append(child)
    else:
      super().append(child)
    return self
  
  @property
  def children(self):
    # put ExtensionElements first in line ;-)
    children = super().children.copy()
    children.sort(key=lambda c: 0 if c.__class__ is ExtensionElements else 1)
    return children
