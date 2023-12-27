from pathlib import Path

from bpmn_tools.builder.conditional import Item, Sequence, BranchedItem, Branch
from bpmn_tools.builder.conditional import ConditionSet, Condition, ConditionKind

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

  filepath = folder / "conditional-builder.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_custom_bpmn_element_class_and_boundary(compare_model_to_file):
  sequence = Sequence().expand(
    Item("step 1", cls=flow.ManualTask, boundary=flow.TimerEventDefinition),
  )

  process = sequence.to_process()
  model = process.render()

  filepath = folder / "conditional-builder-with-custom-class-and-boundary.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_all_none_conditions_1(compare):
  sequence = Sequence().expand(
    Item("step 1"),
    Item("step 2", ConditionSet(
      [Condition("condition 1"), Condition("condition 2")],
      [
        ["value 1", "value a"],
        ["value 1", "value b"],
        ["value 2", None     ]
      ]  
    ))
  )
  compare(sequence.to_dict(), [
    "step 1",
    {
      "condition 1(XOR)": [
        {
          "value 1": [
            {
              "condition 2(XOR)": [
                {
                  "value a,value b": [
                    "step 2"
                  ]
                }
              ]
            }
          ]
        },
        {
          "value 2": [
            "step 2"
          ]
        }
      ]
    }
  ])

def test_all_none_conditions_2(compare):
  sequence = Sequence().expand(
    Item("step 1"),
    Item("step 2", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 1", "value a", None],
        ["value 1", "value b", None],
        ["value 2", None,      None]
      ]  
    ))
  )
  compare(sequence.to_dict(), [
    "step 1",
    {
      "condition 1(XOR)": [
        {
          "value 1": [
            {
              "condition 2(XOR)": [
                {
                  "value a,value b": [
                    "step 2"
                  ]
                }
              ]
            }
          ]
        },
        {
          "value 2": [
            "step 2"
          ]
        }
      ]
    }
  ])

def test_all_none_conditions(compare, compare_model_to_file):
  sequence = Sequence().expand(
    Item("step 1"),
    Item("step 2", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 1", "value a", None],
        ["value 1", "value b", None],
        ["value 2", None,      None]
      ]  
    )),
    Item("step 3", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 3", None, None],
        ["value 4", None, None]
      ]  
    )),
    Item("step 4", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 3", None, None],
        ["value 4", None, None]
      ]  
    )),
    Item("step 5", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 1", None, "something"],
        ["value 2", None, None]
      ]  
    )),
    Item("step 6", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        ["value 2", None, None]
      ]  
    )),
    Item("step 7", ConditionSet(
      [Condition("condition 1"), Condition("condition 2"), Condition("condition 3")],
      [
        [ None, None, "something"]
      ]  
    ))
  )
  compare(sequence.to_dict(), [
    "step 1",
    {
      "condition 1(XOR)": [
        {
          "value 1": [
            {
              "condition 2(XOR)": [
                {
                  "value a,value b": [
                    "step 2"
                  ]
                }
              ]
            },
            {
              "condition 3(XOR)": [
                {
                  "something": [
                    "step 5"
                  ]
                }
              ]
            }
          ]
        },
        {
          "value 2": [
            "step 2",
            "step 5",
            "step 6"
          ]
        },
        {
          "value 3,value 4": [
            "step 3",
            "step 4"
          ]
        }
      ]
    },
    {
      "condition 3(XOR)": [
        {
          "something": [
            "step 7"
          ]
        }
      ]
    }
  ])

  process = sequence.to_process()
  model = process.render()

  filepath = folder / "conditional-builder-with-various-nones.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_collapse_sequential_branched_items(compare, compare_model_to_file):
  sequence = Sequence().expand(
    Item("step 1"),
    Item("step 2", ConditionSet(
      [Condition("condition 1"), Condition("condition 2")],
      [
        [None, "value 1"]
      ]  
    )),
    Item("step 3", ConditionSet(
      [Condition("condition 1"), Condition("condition 2")],
      [
        [None, "value 2"],
        [None, "value 3"]
      ]  
    )),
    Item("step 4")
  )
  compare(sequence.to_dict(), [
    "step 1",
    {
      "condition 2(XOR)": [
        {
          "value 1": [ "step 2" ]
        },
        {
          "value 2,value 3": [ "step 3" ]
        }
      ]
    },
    "step 4"
  ])

  process = sequence.to_process()
  model = process.render()

  filepath = folder / "conditional-builder-collapse_sequential_branched_items.bpmn"
  compare_model_to_file(model, filepath, save_to=f"{filepath.stem}-test.bpmn")

def test_adding_process_properties(compare):
  sequence = Sequence().expand(Item("step 1"))
  process = sequence.to_process(name="with properties", starts=True, ends=True)
  assert len(process.children) == 1
  assert process.children[0].name == "step 1"
  assert process.name == "with properties"
  assert process.starts
  assert process.ends

def test_conditions_require_same_number_of_conditions_and_values():
  try:
    ConditionSet(["condition 1", "condition 2"], [[[1, 2, 3]]])
    assert False, "number of values must match number of conditions"
  except ValueError:
    pass

def test_branch_and_item_condition_value_should_match():
  item = Item("name", ConditionSet(["condition"], [[ "something" ]] ))
  try:
    Branch(("value",)).expand(item)
    assert False, "branch should only accept items with same condition value"
  except ValueError:
    pass

def test_branched_item_and_item_condition_should_match():
  item = Item("name", ConditionSet([Condition("condition")], [[ "something" ]] ))
  try:
    BranchedItem(Condition(["other condition"])).expand(item)
    assert False, "branched item should only accept items with same condition"
  except ValueError:
    pass
  
def test_provide_id_for_task():
  item = Item("name")                                 # task_0
  assert item.to_process().id == "task_0"

  item = Item("name", id="testing")                   # task_1
  assert item.to_process().id == "testing"
  
  item = Item("name", id=lambda d: f"prefixed_{d}")   # task_2
  assert item.to_process().id == "prefixed_task_2"

def test_copy():
  item = Item(
    "name", ConditionSet(), flow.ManualTask, flow.TimerEventDefinition, "id"
  )
  copy = item.copy()
  assert copy.name == item.name
  assert copy.conditions is item.conditions
  assert copy.cls == item.cls
  assert copy.boundary == item.boundary
  assert copy.id == item.id
  