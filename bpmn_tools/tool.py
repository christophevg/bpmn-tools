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
  """
  def __init__(self):
    self._filepath = None
    self._model    = None

  def version(self):
    """
    provides bpmn-tools's version.
    """
    return __version__ # pragma: no cover
    
  def load(self, filepath):
    """
    accepts a filepath, which enables `bpmn` or `json` loaders to use it as an
    alternative to stdin.
    
    usage:
      % bpmn-tool load examples/minimal-hello.bpmn bpmn
    """
    self._filepath = Path(filepath)
    return self

  def from_bpmn(self):
    """
    accepts BPMN XML from stdin
    """
    return self._import("bpmn")

  def to_bpmn(self):
    """
    outputs model as BPMN XML to stdout
    """
    return self._export("bpmn")

  def from_json(self):
    """
    accepts BPMN XML in JSON format from stdin
    """
    return self._import("json")

  def to_json(self):
    """
    outputs model as BPMN XML in JSON format to stdout
    """
    return self._export("json")

  def __str__(self):
    """
    standard string-based output: BPMN (XML)
    """
    return self.to_bpmn()

  def _import(self, format):
    if self._filepath:
      src = self._filepath.read_text()
    else:
      src = sys.stdin.read()
    {
      "bpmn" : self._import_bpmn,
      "json" : self._import_json
    }[format](src)
    return self

  def _import_bpmn(self, bpmn_str):
    self._import_model(xmltodict.parse(bpmn_str))

  def _import_json(self, json_str):
    self._import_model(json.loads(json_str))

  def _import_model(self, model_as_dict):
    self._model = Definitions.from_dict(model_as_dict)

  def _export(self, format):
    if not self._model: # pragma: no cover
      logger.error("No model is available. Did you forget to `load` it?")
      return ""
    return {
      "bpmn" : self._export_bpmn,
      "json" : self._export_json
    }[format]()
  
  def _export_bpmn(self):
    return xmltodict.unparse(self._model.as_dict(with_tag=True), pretty=True, indent="  ")

  def _export_json(self):
    return json.dumps(self._model.as_dict(with_tag=True), indent=2)
