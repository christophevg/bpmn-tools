import pytest

from pathlib import Path
from difflib import unified_diff
import json

from bpmn_tools.util import model2xml, sanitize_xml

from bpmn_tools.builder.process import Task, Branch

def compare_strings(result, expected):
  # print to std, which shows up in test output when assertion fails
  print("".join(unified_diff(
    expected.splitlines(keepends=True),
    result.splitlines(keepends=True)
  )))
  assert result == expected, "see diff"

def compare(result,expected):
  result_str   = json.dumps(result,   indent=2, sort_keys=True)
  expected_str = json.dumps(expected, indent=2, sort_keys=True)
  compare_strings(result_str, expected_str)

def load_model_src(filename):
  return (Path(__file__).parent / "models" / filename).read_text()

def compare_to_file(result, filename, save_to=None):
  if save_to:
    (Path(__file__).parent / "models" / save_to).write_text(result)
  try:
    expected = load_model_src(filename)
    expected = sanitize_xml(expected)
  except FileNotFoundError:
    expected = ""
  compare_strings(result, expected)

def compare_model_to_file(model, filename, save_to=None):
  xml = model2xml(model)
  compare_to_file(xml, filename, save_to)
  return xml

@pytest.fixture(name="compare_to_file")
def compare_to_file_fixture():
  def tester(result, filename, save_to=None) :
    return compare_to_file(result, filename, save_to=save_to)
  return tester

@pytest.fixture(name="compare")
def compare_fixture():
  def tester(result, expected):
    return compare(result, expected)
  return tester

@pytest.fixture(name="compare_model_to_file")
def compare_model_to_file_fixture():
  def tester(model, filename, save_to=None):
    return compare_model_to_file(model, filename, save_to=save_to)
  return tester

@pytest.fixture(autouse=True)
def ensure_starting_each_test_with_generated_ids_starting_at_0():
  Task.reset()
  Branch.reset()
  yield
