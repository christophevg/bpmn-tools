import xmltodict

from bpmn_tools.notation import Definitions
from bpmn_tools.layout import graphviz

from tests.conftest import load_model_src

def test_graphviz_routing(compare_model_to_file):
  model = Definitions.from_dict(
    xmltodict.parse(load_model_src("graphviz-original.bpmn"))
  ) 
  graphviz.layout(model)
  compare_model_to_file(model, "graphviz-goal.bpmn", save_to="graphviz-goal-test.bpmn")
