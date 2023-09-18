examples: examples/hello.png examples/hello-with-lanes.png
	PYTHONPATH=. python examples/visitor.py

examples/%.png: examples/%.bpmn
	bpmn-to-image $<:$@

examples/%.bpmn: examples/generate-%.py FORCE
	PYTHONPATH=. python $< | tee $@

.PHONY: FORCE
