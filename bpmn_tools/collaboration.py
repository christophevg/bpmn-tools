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
    self.extension_groups = {}
  
  @property
  def extension_properties(self):
    properties = {}
    for group in self.extension_groups.values():
      for item in group.children:
        if isinstance(item, PropertyExtension):
          properties[item.name] = item.value
    return properties
  
  def append(self, child):
    if isinstance(child, Extension):
      group = child.__extension_group__
      try:
        self.extension_groups[group].append(child)
      except KeyError:
        self.extension_groups[group] = group().append(child)
    else:
      super().append(child)
    return self
  
  @property
  def children(self):
    children = []
    if self.extension_groups:
      children.append(ExtensionElements().extend(self.extension_groups.values()))
    children.extend(super().children.copy())
    return children
