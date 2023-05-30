class Colored():
  """
    "Decorator" to route everything to the wrapped class
  """

  __color_scheme__ = {}

  def __init__(self, wrapped):
    self.wrapped = wrapped

  def __getattr__(self, attr):
    return getattr(self.wrapped, attr)

  def __getitem__(self, key):
    return self.wrapped[key]

class Red(Colored):
  __color_scheme__ = {
    "bioc:stroke"            : "#831311",
    "bioc:fill"              : "#ffcdd2",
    "color:background-color" : "#ffcdd2",
    "color:border-color"     : "#831311"
  }

class Green(Colored):
  __color_scheme__ = {
    "bioc:stroke"            : "#205022",
    "bioc:fill"              : "#c8e6c9",
    "color:background-color" : "#c8e6c9",
    "color:border-color"     : "#205022"
  }

class Orange(Colored):
  __color_scheme__ = {
    "bioc:stroke"            : "#6b3c00",
    "bioc:fill"              : "#ffe0b2",
    "color:background-color" : "#ffe0b2",
    "color:border-color"     : "#6b3c00"
  }

class Blue(Colored):
  __color_scheme__ = {
    "bioc:stroke"            : "#0d4372",
    "bioc:fill"              : "#bbdefb",
    "color:background-color" : "#bbdefb",
    "color:border-color"     : "#0d4372"
  }
