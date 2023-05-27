from pathlib import Path
import xmltodict
import json

from bpmn_tools.xml import Element, Visitor

with open(Path(__file__).resolve().parent / ".." / "examples" / "hello.bpmn") as fp:
  xml = xmltodict.parse(fp.read())
  tree = Element.from_dict(xml)

  # default Visitor
  tree.accept(Visitor())

  # custom Handler
  class MyVisitor(Visitor):
    def visit(self, visited):
      if visited.id:
        print(f"{'   '*self.depth}{visited.id}")
      else:
        super().visit(visited)

  tree.accept(MyVisitor())
