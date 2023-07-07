from difflib import unified_diff
import json
import xmltodict

def prune(lst):
  if len(lst) == 1:
    return lst[0]
  return lst

def show_diff(result, expected):
  def as_dict(obj):
    return obj.as_dict()
  result   = json.dumps(result,   indent=2, sort_keys=True, default=as_dict)
  expected = json.dumps(expected, indent=2, sort_keys=True, default=as_dict)
  diff = unified_diff(expected.splitlines(keepends=True),
                      result.splitlines(keepends=True),
                      fromfile="expected", tofile="result")
  print("".join(diff), end="")

def compare(result, expected):
  print("=" * 20, "result dict", "=" * 20)
  print(json.dumps(result, indent=2))
  print("=" * 20, "result XML", "=" * 20)
  print(xmltodict.unparse(result, pretty=True))
  print("=" * 20, "diff", "=" * 20)
  show_diff(result, expected)
  assert result == expected
