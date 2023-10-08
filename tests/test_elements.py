from pathlib import Path
import xmltodict

from bpmn_tools.notation import Definitions

def test_process_of_event():
  """
    fixes issue that `process` property was at Task level
    by moving it to `Element` level, along with `lane` property
  """
  with open(Path(__file__).resolve().parent / "models" / "message-events.bpmn") as fp:
    xml = fp.read()
    d = xmltodict.parse(xml)
    definitions = Definitions.from_dict(d)
    end_message = definitions.find("name", "End Message")
    assert end_message.process == definitions.processes[0]
