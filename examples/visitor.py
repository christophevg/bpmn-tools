from pathlib import Path
import xmltodict
import json

from bpmn_tools.xml import Element, Visitor
from bpmn_tools     import classes

with open(Path(__file__).resolve().parent / ".." / "examples" / "hello.bpmn") as fp:
  xml = xmltodict.parse(fp.read())
  generic_tree = Element.from_dict(xml)

  # default Visitor on generic tree
  generic_tree.accept(Visitor())

  # provide classes to specialize Elements
  tree = Element.from_dict(xml, classes=classes)

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
