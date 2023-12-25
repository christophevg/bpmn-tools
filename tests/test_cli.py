import io
from pathlib import Path
import xmltodict
import json

from bpmn_tools.tool import CLI

def test_loading_of_bpmn_from_stdin(monkeypatch):
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models" 
  filepath = folder / "hello.bpmn"
  expected = filepath.read_text()
  monkeypatch.setattr("sys.stdin", io.StringIO(expected))
  result = str(cli.from_bpmn())
  assert xmltodict.parse(result) == xmltodict.parse(expected)

def test_loading_of_bpmn_from_file():
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models" 
  filepath = folder / "hello.bpmn"
  result = str(cli.load(filepath).from_bpmn())
  expected = filepath.read_text()
  assert xmltodict.parse(result) == xmltodict.parse(expected)

def test_loading_of_json_from_stdin(monkeypatch):
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models" 
  filepath = folder / "hello.json"
  json_str = filepath.read_text()
  monkeypatch.setattr("sys.stdin", io.StringIO(json_str))
  result = str(cli.from_json())
  expected = (folder / "hello.bpmn").read_text()
  assert xmltodict.parse(result) == xmltodict.parse(expected)

def test_loading_of_json_from_file():
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models" 
  filepath = (folder / "hello.json")
  result = str(cli.load(filepath).from_json())
  expected = (folder / "hello.bpmn").read_text()
  assert xmltodict.parse(result) == xmltodict.parse(expected)

def test_exporting_to_json():
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models" 
  filepath = folder / "hello.bpmn"
  result = str(cli.load(filepath).from_bpmn().to_json())
  expected = filepath.read_text()
  assert json.loads(result) == xmltodict.parse(expected)
