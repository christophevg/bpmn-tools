# BPMN Tools

> a collection of tools to work with BPMN

[![Latest Version on PyPI](https://img.shields.io/pypi/v/bpmn-tools.svg)](https://pypi.python.org/pypi/bpmn-tools/)
[![Supported Implementations](https://img.shields.io/pypi/pyversions/bpmn-tools.svg)](https://pypi.python.org/pypi/bpmn-tools/)
[![Built with PyPi Template](https://img.shields.io/badge/PyPi_Template-v0.2.0-blue.svg)](https://github.com/christophevg/pypi-template)

## Installation

```console
% pip install bpmn-tools
```

## See it in Action

```pycon
>>> import xmltodict
>>> from bpmn_tools.flow          import Process, Start, End, Task, Flow
>>> from bpmn_tools.collaboration import Collaboration, Participant
>>> from bpmn_tools.notation      import Definitions
>>> from bpmn_tools.diagrams      import Diagram, Plane, Shape, Edge
>>> from bpmn_tools.layout        import simple
>>> activities = [
...   Start(id="start"),
...   Task('Say "Hello!"', id="hello"),
...   Task('Wait for response...', id="wait"),
...   End(id="end")
... ]
>>> process = Process(id="process").extend(activities).extend([
...   Flow(source=activities[0], target=activities[1]),
...   Flow(source=activities[1], target=activities[2]),
...   Flow(source=activities[2], target=activities[3])
... ])
>>> collaboration = Collaboration(id="collaboration").append(
...   Participant("lane", process, id="participant")
... )
>>> model = Definitions(id="definitions").extend([
...   process,
...   collaboration,
... ])
>>> model.append(
...   Diagram(
...     id="diagram",
...     plane=Plane(id="plane", element=collaboration)
...   )
... )
Definitions({'id': 'definitions', 'xmlns:bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL', 'xmlns:bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI', 'xmlns:dc': 'http://www.omg.org/spec/DD/20100524/DC', 'xmlns:di': 'http://www.omg.org/spec/DD/20100524/DI'})
>>> simple.layout(model)
>>> xml = xmltodict.unparse(model.as_dict(with_tag=True), pretty=True)
>>> with open("hello.bpmn", "w") as fp:
...   fp.write(xml)
... 
2937
```

Use `bpmn-to-image` to visualize the generated XML, because "what (sane) human being wants to read XML?" 😉

```console
% npm install -g bpmn-to-image
% bpmn-to-image hello.bpmn:hello.png
```

Et voila...

![Hello BPMN](https://raw.githubusercontent.com/christophevg/bpmn-tools/master/examples/hello.png)
