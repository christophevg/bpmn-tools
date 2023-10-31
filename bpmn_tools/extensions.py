"""
  Support for Extensions, with support for Zeebe Properties

  <bpmn:collaboration id="...">
    <bpmn:extensionElements>
      <zeebe:properties>
        <zeebe:property name="name 1" value="value 1"></zeebe:property>
        <zeebe:property name="name 2" value="value 2"></zeebe:property>
      </zeebe:properties>
    </bpmn:extensionElements>
  </bpmn:collaboration>

  ExtensionElements
    +-- ExtensionGroup                --> ZeebeProperties
          +-- Extension
                +-- PropertyExtension --> ZeebePropertyExtension
"""

from . import xml

class ExtensionElements(xml.Element):
  __tag__ = "bpmn:extensionElements"

class ExtensionGroup(xml.Element):
  pass

class ZeebeProperties(ExtensionGroup):
  __tag__ = "zeebe:properties"

class Extension(xml.Element):
  pass

class PropertyExtension(Extension):
  def __init__(self, name, value):
    super().__init__()
    self.name  = name
    self.value = value

  @property
  def attributes(self):
    return {
      "name" : self.name,
      "value": self.value
    }

class ZeebePropertyExtension(PropertyExtension):
  __tag__             = "zeebe:property"
  __extension_group__ = ZeebeProperties
