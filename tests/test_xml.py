from pathlib import Path
import xmltodict

from bpmn_tools.xml  import Element

def test_hello_round_trip(compare):
  with open(Path(__file__).resolve().parent / "models" / "hello.bpmn") as fp:
    expected = xmltodict.parse(fp.read())
  tree = Element.from_dict(expected)
  result = tree.as_dict(with_tag=True)
  compare(result, expected)
