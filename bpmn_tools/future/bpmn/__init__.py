"""

The `bpmn` module contains a class hierarchy that adheres closely to the BPMN
XML format and serves as an object model for it.

Typical usage:

>>> import xmltodict
>>> 
>>> from bpmn_tools.future import bpmn
>>> 
>>> task          = bpmn.UserTask("Say Hello!")
>>> process       = bpmn.Process().append(task)
>>> participant   = bpmn.Participant("some participant", process)
>>> collaboration = bpmn.Collaboration().append(participant)
>>> plane         = bpmn.Plane(element=collaboration)
>>> diagram       = bpmn.Diagram(plane=plane)
>>> definitions   = bpmn.Definitions().extend([ process, collaboration, diagram ])
>>> 
>>> print(xmltodict.unparse(
...   definitions.as_dict(with_tag=True),
...   pretty=True,
...   short_empty_elements=True,
...   indent="  "
... ))
<?xml version="1.0" encoding="utf-8"?>
<bpmn:definitions id="definitions_ER3DWXS3" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:bioc="http://bpmn.io/schema/bpmn/biocolor/1.0" xmlns:color="http://www.omg.org/spec/BPMN/non-normative/color/1.0" xmlns:zeebe="http://camunda.org/schema/zeebe/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <bpmn:process id="process_S2Q5KU6D">
    <bpmn:userTask id="usertask_0V384C6T" name="Say Hello!"/>
  </bpmn:process>
  <bpmn:collaboration id="collaboration">
    <bpmn:participant id="participant" name="some participant" processRef="process_S2Q5KU6D"/>
  </bpmn:collaboration>
  <bpmndi:BPMNDiagram id="diagram">
    <bpmndi:BPMNPlane id="plane_collaboration" bpmnElement="collaboration">
      <bpmndi:BPMNShape id="shape_participant" bpmnElement="participant" isHorizontal="true">
        <dc:Bounds x="0" y="0" width="600" height="125"/>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="shape_usertask_0V384C6T" bpmnElement="usertask_0V384C6T">
        <dc:Bounds x="0" y="0" width="100" height="80"/>
      </bpmndi:BPMNShape>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
  
"""

from bpmn_tools.flow          import * # noqa
from bpmn_tools.collaboration import * # noqa
from bpmn_tools.notation      import * # noqa
from bpmn_tools.diagrams      import * # noqa

from bpmn_tools.future.bpmn.flow   import * # noqa
