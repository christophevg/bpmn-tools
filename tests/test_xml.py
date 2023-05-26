from pathlib import Path
import xmltodict
import json

from bpmn_tools.xml  import Element
from bpmn_tools.util import compare

def test_hello_round_trip():
  with open(Path(__file__).resolve().parent / ".." / "examples" / "hello.bpmn") as fp:
    expected = xmltodict.parse(fp.read())
  tree = Element.from_dict(expected)
  result = tree.as_dict(with_tag=True)
  compare(result, expected)
  # print(json.dumps(result, indent=2, sort_keys=True))
  # assert False
