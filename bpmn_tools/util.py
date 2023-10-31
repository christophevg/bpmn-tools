import xmltodict

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
