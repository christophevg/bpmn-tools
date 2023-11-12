from pathlib import Path
import xmltodict

from bpmn_tools.xml     import Element
from bpmn_tools.visitor import Visitor

def test_visiting_hello():
  with open(Path(__file__).resolve().parent / "models" / "hello.bpmn") as fp:
    xml = xmltodict.parse(fp.read())
    tree = Element.from_dict(xml)

    visitations = []

    class MyVisitor(Visitor):
      def visit(self, visited):
        if visited["id"]:
          visitations.append(visited["id"])

    tree.accept(MyVisitor())

    assert visitations == [
      'definitions',
      'process',
      'flow_start_hello',
      'flow_hello_end',
      'start',
      'hello',
      'end',
      'collaboration',
      'participant',
      'diagram',
      'plane_collaboration',
      'edge_flow_hello_end',
      'edge_flow_start_hello',
      'shape_end',
      'shape_hello',
      'shape_participant',
      'shape_start'
    ]
