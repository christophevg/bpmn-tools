from pathlib import Path
import xmltodict

from bpmn_tools.notation  import Definitions
from bpmn_tools.util      import compare

def compare_with_roundtrip(xml1):
  # xml -> obj
  d1 = xmltodict.parse(xml1)
  obj1 = Definitions.from_dict(d1)

  # obj -> xml
  d1g = obj1.as_dict(with_tag=True)
  
  # ensure that generated dict equals original parsed dict
  compare(d1g, d1)
  
  xml2 = xmltodict.unparse(d1g)

  # xml -> obj
  d2 = xmltodict.parse(xml2)
  
  compare(d2, d1)
  
  obj2 = Definitions.from_dict(d2)
  d2g = obj2.as_dict(with_tag=True)
  
  compare(d2g, d1)

def test_hello():
  with open(Path(__file__).resolve().parent / "hello.bpmn") as fp:
    compare_with_roundtrip(fp.read())

def test_hello_lanes():
  with open(Path(__file__).resolve().parent / "hello-lanes.bpmn") as fp:
    compare_with_roundtrip(fp.read())

def test_hello_lanes_with_message():
  with open(Path(__file__).resolve().parent / "hello-lanes-with-message.bpmn") as fp:
    compare_with_roundtrip(fp.read())

def test_hello_colors():
  with open(Path(__file__).resolve().parent / "hello-colors.bpmn") as fp:
    compare_with_roundtrip(fp.read())

def test_message_events():
  with open(Path(__file__).resolve().parent / "message-events.bpmn") as fp:
    compare_with_roundtrip(fp.read())
