from pathlib import Path

from bpmn_tools.builder.conditional import Item, Sequence, BranchedItem
from bpmn_tools.builder.conditional import ConditionSet, Condition, ConditionKind

from bpmn_tools.builder.process import Task, Branch

from bpmn_tools import flow

folder = Path(__file__).resolve().parent / "models"

def test_single_item_without_conditions():
  item = Item("name")
  sequence = Sequence().expand(item)
  assert len(sequence) == 1
  assert sequence[0] == item

def test_multiple_items_without_conditions():
  items = [ Item("name 1"), Item("name 2") ]
  sequence = Sequence().expand(*items)
  assert len(sequence) == 2
  assert sequence[0] == items[0]
  assert sequence[1] == items[1]

def test_single_item_with_single_condition_and_single_value():
  item = Item(
    "name", ConditionSet( [ Condition("condition") ], [["value"]])
  )
  sequence = Sequence().expand(item)
  assert len(sequence) == 1
  assert isinstance(sequence[0], BranchedItem)
  branched_item = sequence[0]
  assert branched_item.name == "condition"
  assert len(branched_item) == 1
  branch = branched_item[0]
  assert branch.value == ("value",)
  assert len(branch.sequence) == 1
  assert branch.sequence[0].name == "name"

def test_single_item_with_single_condition_and_multiple_values_to_collapse():
  item = Item(
    "name", ConditionSet(
      [Condition("condition")], [["value 1"], ["value 2"]]
    )
  )
  sequence = Sequence().expand(item)
  assert len(sequence) == 1
  assert isinstance(sequence[0], BranchedItem)
  branched_item = sequence[0]
  assert branched_item.name == "condition"
  assert len(branched_item) == 1
  assert branched_item[0].value == ("value 1","value 2")
  assert branched_item[0].sequence[0].name == "name"

def test_single_item_with_multiple_conditions_and_multiple_value():
  item = Item(
    "name", ConditionSet(
      [Condition("condition 1"), Condition("condition 2")],
      [["value 1a", "value 1b"], ["value 2a", "value 2b"]]
    )
  )
  sequence = Sequence().expand(item)
  assert len(sequence) == 1
  assert isinstance(sequence[0], BranchedItem)
  branched_item = sequence[0]
  assert branched_item.name == "condition 1"
  assert len(branched_item) == 2
  assert isinstance(branched_item[0].sequence[0], BranchedItem)
  assert isinstance(branched_item[1].sequence[0], BranchedItem)

def test_a_more_complex_all_in_one_flow(compare, compare_model_to_file):
  sequence = Sequence().expand(
    Item("step 1"),
    Item("step 2", ConditionSet(
      [Condition("condition 1", ConditionKind.AND)],
      [["value 1"], ["value 2"]]
    )),
    Item("step 3", ConditionSet(
      [Condition("condition 1"), Condition("condition 2")],
      [["value 1", "value a"], ["value 3", "value b"], [None, "value c"]]
    )),
    Item("step 4"),
    Item("step 5", ConditionSet(
      [Condition("condition 1")],
      [["value 1"]]
    )),
    Item("step 6", ConditionSet(
      [Condition("condition 1")],
      [["value 1"]]
    )),    
  )
  compare(sequence.to_dict(), [
    "step 1",
    {
      "condition 1(AND)": [
        {
          "value 1": [
            "step 2",
            {
              "condition 2(XOR)": [
                { "value a,value c": [ "step 3" ] }
              ]
            }
          ]
        },
        {
          "value 2": [
            "step 2",
            {
              "condition 2(XOR)": [
                { "value c": [ "step 3" ] }
              ]
            }
          ]
        },
        {
          "value 3": [
            {
              "condition 2(XOR)": [
                { "value b,value c": [ "step 3" ] }
              ]
            }
          ]
        }
      ]
    },
    "step 4",
    {
      "condition 1(XOR)" : [
        { "value 1": [ "step 5", "step 6" ] }
      ]
    }
  ])

  process = sequence.to_process()
  model = process.render()

  Task.reset()
  Branch.reset()

  filepath = folder / "conditional-builder.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_custom_bpmn_element_class_and_boundary(compare_model_to_file):
  sequence = Sequence().expand(
    Item("step 1", cls=flow.ManualTask, boundary=flow.TimerEventDefinition),
  )

  process = sequence.to_process()
  model = process.render()

  Task.reset()
  Branch.reset()

  filepath = folder / "conditional-builder-with-custom-class-and-boundary.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")
