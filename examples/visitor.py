from pathlib import Path
import xmltodict

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
colorama_init()

from bpmn_tools          import classes
from bpmn_tools.xml      import Element
from bpmn_tools.visitor  import Visitor, PrintingVisitor, visiting
from bpmn_tools.diagrams import Diagram, Plane, Shape

with open(Path(__file__).resolve().parent / ".." / "examples" / "hello.bpmn") as fp:
  xml = xmltodict.parse(fp.read())
  generic_tree = Element.from_dict(xml)

  # default Visitor on generic tree
  generic_tree.accept(Visitor())

  # provide classes to specialize Elements
  tree = Element.from_dict(xml, classes=classes)

  # default Visitor
  tree.accept(PrintingVisitor())

  # custom Handler
  class MyVisitor(PrintingVisitor):
    def visit(self, visited):
      if visited.id:
        print(f"{'   '*self.depth}{visited.id}")
      else:
        super().visit(visited)

  tree.accept(MyVisitor())

  # using visitor with class-specific visiting functions
  
  class ShapeVisitor(Visitor):
    @visiting(Shape)
    def visit(self, shape):
      print(f"{'    '*(self.depth-1)}{Fore.GREEN}{shape}{Style.RESET_ALL}")

    @visiting(Diagram, Plane)
    def visit(self, visited):
      print(f"{'   '*(self.depth-1)}{Fore.BLUE}{visited}{Style.RESET_ALL}")

  tree.accept(ShapeVisitor())
