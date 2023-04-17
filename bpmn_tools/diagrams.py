"""
  Classes representing the different parts of a BPMN file.
"""

def prune(lst):
  if len(lst) == 1:
    return lst[0]
  return lst

class Process():
  def __init__(self, ref="process"):
    self.ref = ref
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
    base["@ref"] = self.ref
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
  def ref(self):
    return f"flow_{self.source.ref}_{self.target.ref}"

  def as_dict(self):
    return {
      "@ref"       : self.ref,
      "@sourceRef": self.source.ref,
      "@targetRef": self.target.ref
    }

class Activity():
  def __init__(self, ref):
    self.ref = ref
    self.incoming = []
    self.outgoing = []
  
  def flow_to(self, next_activity):
    Flow(self, next_activity)
    return self
  
  def as_dict(self):
    base = {
      "@ref": self.ref
    }
    if self.outgoing:
      base["bpmn:outgoing"] = prune([ flow.ref for flow in self.outgoing ])
    if self.incoming:
      base["bpmn:incoming"] = prune([ flow.ref for flow in self.incoming ])
    return base

class Start(Activity):
  __tag__ = "startEvent"

  def __init__(self, ref="start"):
    super().__init__(ref)

class End(Activity):
  __tag__ = "endEvent"

  def __init__(self, ref="end"):
    super().__init__(ref)

class Task(Activity):
  __tag__ = "task"

  def __init__(self, name, ref="task"):
    super().__init__(ref)
    self.name = name

  def as_dict(self):
    base = super().as_dict()
    base["@name"] = self.name
    return base

class Collaboration():
  def __init__(self, ref="process"):
    self.ref = ref
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
    base["@ref"] = self.ref
    return {
      f"bpmn:{self.__class__.__name__.lower()}" : base
    }

class Participant():
  def __init__(self, name, process, ref="participant"):
    self.ref      = ref
    self.name    = name
    self.process = process

  def as_dict(self):
    return {
      "@ref"        : self.ref, 
      "@name"      : self.name,
      "@processRef": self.process.ref
    }
