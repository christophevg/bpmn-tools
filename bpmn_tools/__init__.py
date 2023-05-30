"""
  BPMN Tools is a collection of tools to work with BPMN ;-)
"""

__version__ = "0.0.3"

import sys, inspect

from bpmn_tools import notation, collaboration, flow, diagrams

def get_classes(module):
  return [
    c[1] for c in inspect.getmembers(sys.modules[module], inspect.isclass)
  ]

classes = get_classes("bpmn_tools.notation") + \
          get_classes("bpmn_tools.collaboration") + \
          get_classes("bpmn_tools.flow") + \
          get_classes("bpmn_tools.diagrams")
