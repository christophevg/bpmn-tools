# decorator based visitor, inspired by https://stackoverflow.com/a/28398903

def _qualname(obj):
  """Get the fully-qualified name of an object (including module)."""
  return obj.__module__ + '.' + obj.__qualname__

def _declaring_class(obj):
  """Get the name of the class that declared an object."""
  name = _qualname(obj)
  return name[:name.rfind('.')]

_methods = {}

def _visitor_impl(self, arg):
  """Actual visitor method implementation."""
  try:
    method = _methods[(_qualname(type(self)), type(arg))]
    return method(self, arg)
  except KeyError:
    pass
  return Visitor.visit(self, arg) 

def visiting(*arg_types):
  """Decorator that creates a visitor method."""
  def decorator(fn):
    declaring_class = _declaring_class(fn)
    for arg_type in arg_types:
      _methods[(declaring_class, arg_type)] = fn
    return _visitor_impl
  return decorator

class Visitor:
  def __init__(self):
    self.depth = -1

  def __enter__(self):
    self.depth += 1
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    self.depth -= 1

  def visit(self, visited):
    pass

class PrintingVisitor(Visitor):
  def visit(self, visited):
    print(f"{'   '*self.depth}{visited}")
