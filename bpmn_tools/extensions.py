"""
  Support for Extensions, with support for Camunda Properties

  <bpmn:collaboration id="...">
    <bpmn:extensionElements>
      <camunda:properties>
        <camunda:property name="name 1" value="value 1"></camunda:property>
        <camunda:property name="name 2" value="value 2"></camunda:property>
      </camunda:properties>
    </bpmn:extensionElements>
  </bpmn:collaboration>

"""

from . import xml

class ExtensionElements(xml.Element):
  __tag__ = "bpmn:extensionElements"

class CamundaProperties(xml.Element):
  __tag__ = "camunda:properties"

class Extension(xml.Element):
  pass

class CamundaPropertyExtension(Extension):
  __tag__             = "camunda:property"
  __extension_group__ = CamundaProperties

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
