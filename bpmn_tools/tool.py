import logging
import sys

import xmltodict
from pathlib import Path
import json

from bpmn_tools import __version__
from bpmn_tools.notation import Definitions

logger = logging.getLogger(__name__)

class CLI():
  """
  thé command line interface to bpmn-tools: bpmn-tool
  
  enables reading/writing BPMN XML (or JSON) files and more (to come ;-))
  
    % bpmn-tool load tests/models/hello.bpmn 
    % bpmn-tool load - < tests/models/hello.bpmn
    % bpmn-tool load tests/models/hello.bpmn export json
  """
  def __init__(self):
    self._model = Definitions(id="definitions")

  def version(self):
    """
    provides bpmn-tools's version.
    """
    return __version__ # pragma: no cover
    
  def load(self, filepath="-"):
    """
    accepts a filepath to a file in one of the supported formats 
    provide "-" or "-:<format>" to load from stdin
    """
    if str(filepath)[0] == "-":
      src = sys.stdin.read()
      _, format = f"{filepath}:bpmn".split(":", 2)[0:2]
    else:  
      filepath = Path(filepath)
      src = filepath.read_text()
      format = filepath.suffix[1:]
    loader = getattr(self, f"_import_{format}")
    self._model = Definitions.from_dict(loader(src))
    return self

  def export(self, format="bpmn"):
    # then export
    return getattr(self, f"_export_{format}")()

  def __str__(self):
    """
    this is triggered at the end if no explicit action (e.g. export is given)
    """
    return self.export()

  # importer and exporters

  def _import_bpmn(self, bpmn_str):
    return xmltodict.parse(bpmn_str)

  def _import_json(self, json_str):
    return json.loads(json_str)

  def _export_bpmn(self):
    return xmltodict.unparse(self._model.as_dict(with_tag=True), pretty=True, indent="  ")

  def _export_json(self):
    return json.dumps(self._model.as_dict(with_tag=True), indent=2)
