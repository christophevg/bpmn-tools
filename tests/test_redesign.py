"""

Tests to drive the redesign of the BPMN object model.
Goal is to rebuild the entire model in the future submodule and then drop-in
replace to ensure all existng tests work.

"""

import xmltodict

from bpmn_tools.future import bpmn

# Definitions

def test_creation_of_empty_definitions():
  definitions = bpmn.Definitions()

  assert len(definitions.processes)      == 0
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 0

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      f"@{key}" : value for key, value in bpmn.notation.BPMN_NS.items()
    }
  }

def test_parsing_of_empty_definitions():
  xml = """
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
</bpmn:definitions>
"""
  
  definitions = bpmn.Definitions.from_dict(xmltodict.parse(xml))

  assert len(definitions.processes)      == 0
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 0

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      f"@{key}" : value for key, value in bpmn.notation.BPMN_NS.items()
    }
  }

# Process

def test_creation_of_empty_process():
  process = bpmn.Process(id="test-process")
  
  assert len(process.elements) == 0
  
  assert process.as_dict(with_tag=True) == {
    "bpmn:process" : {
      "@id" : "test-process",
      "@isExecutable" : "true"
    }
  }

def test_parsing_of_definitions_with_empty_process():
  xml = """
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <bpmn:process id="parsed-id" isExecutable="false"></bpmn:process>
</bpmn:definitions>
"""

  definitions = bpmn.Definitions.from_dict(xmltodict.parse(xml))

  assert len(definitions.processes)      == 1
  assert len(definitions.collaborations) == 0
  assert len(definitions.diagrams)       == 0
  assert len(definitions.children)       == 1

  assert definitions.as_dict(with_tag=True) == {
    "bpmn:definitions" : {
      **{ f"@{key}" : value for key, value in bpmn.notation.BPMN_NS.items() },
      **{ "bpmn:process" : {
            "@id" : "parsed-id",
            "@isExecutable" : "false"
          }
      }
    }
  }
