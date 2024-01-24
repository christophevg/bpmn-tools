from bpmn_tools.layout import graphviz
from bpmn_tools import util

from tests.conftest import load_model_src
from unittest.mock import Mock
import json

def test_graphviz_routing(compare_model_to_file):
  model = util.xml2model(load_model_src("graphviz-original.bpmn"))

  # graphviz doesn't produce the same results on different platforms, so, to
  # eliminate this, we're mocking this
  gv_mock = Mock()
  gv_mock.pipe.return_value = json.dumps({
    "objects": [
      { "name": "Activity_0yvzjff", "pos": "69.544,380.58" },
      { "name": "Activity_0k2y43l", "pos": "182.25,60.475" },
      { "name": "Activity_00ip78i", "pos": "419.35,603.23" },
      { "name": "Activity_12mr32b", "pos": "394.39,300.6"  },
      { "name": "Activity_1i04bed", "pos": "526.28,18"     },
      { "name": "Activity_1t7zz52", "pos": "715.2,319.19"  }
    ]
  }).encode("ascii")

  graphviz.layout(model, g=gv_mock)
  compare_model_to_file(model, "graphviz-goal.bpmn", save_to="graphviz-goal-test.bpmn")
