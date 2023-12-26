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
  cli.load()
  result_str = str(cli)
  result_export = cli.export()
  assert result_str == result_export
  assert xmltodict.parse(result_str) == xmltodict.parse(expected)

def test_loading_of_bpmn_from_load(monkeypatch):
  monkeypatch.setattr("sys.stdin", io.StringIO())
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models"
  filepath = folder / "hello.bpmn"
  cli.load(filepath)
  result_str = str(cli)
  result_export = cli.export()
  assert result_str == result_export
  expected = filepath.read_text()
  assert xmltodict.parse(result_str) == xmltodict.parse(expected)

def test_loading_of_json_from_stdin(monkeypatch):
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models"
  filepath = folder / "hello.json"
  json_str = filepath.read_text()
  monkeypatch.setattr("sys.stdin", io.StringIO(json_str))
  result = str(cli.load("-:json"))
  expected = (folder / "hello.bpmn").read_text()
  assert xmltodict.parse(result) == xmltodict.parse(expected)

def test_loading_of_json_from_load(monkeypatch):
  monkeypatch.setattr("sys.stdin", io.StringIO())
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models"
  filepath = (folder / "hello.json")
  cli.load(filepath)
  result_str = str(cli)
  result_export = cli.export()
  assert result_str == result_export
  expected = (folder / "hello.bpmn").read_text()
  assert xmltodict.parse(result_str) == xmltodict.parse(expected)

def test_exporting_to_json(monkeypatch):
  monkeypatch.setattr("sys.stdin", io.StringIO())
  cli = CLI()
  folder = Path(__file__).resolve().parent / "models"
  filepath = folder / "hello.bpmn"
  result = str(cli.load(filepath).export("json"))
  expected = filepath.read_text()
  assert json.loads(result) == xmltodict.parse(expected)
