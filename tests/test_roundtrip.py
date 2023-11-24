import pytest

from pathlib import Path
import xmltodict

from bpmn_tools.notation  import Definitions

from tests.conftest import compare_model_to_file

def perform_roundtrip_test(filepath):
  """
  given a filename, the BPMN XML is 
  1. loaded as a dict
  2. used to construct a Definitions object
  3. of which the XML rendering is compared to the original
  """
  xml = filepath.read_text()

  # xml -> obj
  as_dict = xmltodict.parse(xml)
  model   = Definitions.from_dict(as_dict, raise_unmapped=True)
  
  # ensure that rebuild model from parsed xml is still equal
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-roundtrip.bpmn")

folder = Path(__file__).resolve().parent / "models" 
models = [ str(filepath.name) for filepath in folder.glob("*.bpmn") ]

@pytest.mark.parametrize("filename", models)
def test_all_reference_models(filename):
  filepath = folder / filename
  if not filepath.stem.endswith("-roundtrip") and not filepath.stem.endswith("-test") and "goal" not in filepath.stem:
    if filepath.stem.startswith("bad-"):
      try:
        perform_roundtrip_test(filepath)
        assert False, f"expected exception: {filepath.stem}"
      except Exception:
        pass
    else:
      perform_roundtrip_test(filepath)
