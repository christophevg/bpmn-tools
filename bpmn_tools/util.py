import xmltodict
import re

def dict2xml(xml_as_dict):
  return xmltodict.unparse(
    xml_as_dict,
    pretty=True,
    short_empty_elements=True,
    indent="  "
  )
  
def model2xml(model):
  return dict2xml(model.as_dict(with_tag=True))

def sanitize_xml(xml):
  return dict2xml(xmltodict.parse(xml))

def uncamel(string):
  """
    (
      (?<=[a-z0-9])     preceeded by a lowercase or number
      [A-Z]             => capital
    |
      (?!^)             not at beginning
      [A-Z]             => capital
      (?=[a-z])         followed by a lower case letter
    )
    credit: https://stackoverflow.com/questions/1175208/#12867228
  """
  string = re.sub("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r" \1", string)
  return re.sub(" \\s*", " ", string) # remove multiple spacing

def slugify(string):
  return re.sub("-+", "-",
           re.sub(" +", "-",
             re.sub("[^a-z0-9- ]", "",
               re.sub("_", " ", uncamel(string)).lower()).strip()))
