"""
  Classes representing the different parts of a BPMN file.
"""

def prune(lst):
  if len(lst) == 1:
    return lst[0]
  return lst

class Process():
  def __init__(self, id="process"):
    self.id = id
    self._activities = {}
  
  def append(self, activity):
    try:
      self._activities[activity.__tag__].append(activity)
    except KeyError:
      self._activities[activity.__tag__] = [ activity ]
    return self

  def extend(self, activities):
    for activity in activities:
      self.append(activity)
    return self

  def as_dict(self):
    # compile activities
    base = {
      f"bpmn:{name}" : prune([
        activity.as_dict() for activity in activities
      ]) for name, activities in self._activities.items()
    }
    # TODO detect flows

    # add properties
    base["@id"] = self.id
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Flow():
  __tag__ = "sequenceFlow"

  def __init__(self, source=None, target=None):
    self.source = source
    self.target = target
    self.source.outgoing.append(self)
    self.target.incoming.append(self)

  @property
  def id(self):
    return f"flow_{self.source.id}_{self.target.id}"

  def as_dict(self):
    return {
      "@id"       : self.id,
      "@sourceRef": self.source.id,
      "@targetRef": self.target.id
    }

class Activity():
  def __init__(self, id):
    self.id = id
    self.incoming = []
    self.outgoing = []
  
  def flow_to(self, next_activity):
    Flow(self, next_activity)
    return self
  
  def as_dict(self):
    base = {
      "@id": self.id
    }
    if self.outgoing:
      base["bpmn:outgoing"] = prune([ flow.id for flow in self.outgoing ])
    if self.incoming:
      base["bpmn:incoming"] = prune([ flow.id for flow in self.incoming ])
    return base

class Start(Activity):
  __tag__ = "startEvent"

  def __init__(self, id="start"):
    super().__init__(id)

class End(Activity):
  __tag__ = "endEvent"

  def __init__(self, id="end"):
    super().__init__(id)

class Task(Activity):
  __tag__ = "task"

  def __init__(self, name, id="task"):
    super().__init__(id)
    self.name = name

  def as_dict(self):
    base = super().as_dict()
    base["@name"] = self.name
    return base

class Collaboration():
  def __init__(self, id="process"):
    self.id = id
    self.participants = []
  
  def append(self, participant):
    self.participants.append(participant)
    return self

  def extend(self, participants):
    self.participants.extend(participants)
    return self

  def as_dict(self):
    # compile participants
    if self.participants:
      base = {
        f"bpmn:participant" : prune([
          participant.as_dict() for participant in self.participants
        ])
      }

    # add properties
    base["@id"] = self.id
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Participant():
  def __init__(self, name, process, id="participant"):
    self.id      = id
    self.name    = name
    self.process = process

  def as_dict(self):
    return {
      "@id"        : self.id, 
      "@name"      : self.name,
      "@processRef": self.process.id
    }
