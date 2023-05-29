from pathlib import Path
import xmltodict
import json

from bpmn_tools.xml     import Element
from bpmn_tools.visitor import Visitor

def test_visiting_hello():
  with open(Path(__file__).resolve().parent / "hello.bpmn") as fp:
    xml = xmltodict.parse(fp.read())
    tree = Element.from_dict(xml)

    visitations = []

    class MyVisitor(Visitor):
      def visit(self, visited):
        if visited["id"]:
          visitations.append(visited["id"])

    tree.accept(MyVisitor())

    assert visitations == [
      "definitions",
      "collaboration",
      "participant",
      "process",
      "start",
      "hello",
      "end",
      "flow_start_hello",
      "flow_hello_end",
      "diagram",
      "plane_collaboration",
      "shape_participant",
      "shape_start",
      "shape_hello",
      "shape_end",
      "edge_flow_start_hello",
      "edge_flow_hello_end"
    ]
