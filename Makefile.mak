LOG_LEVEL=ERROR
EXAMPLES=examples/*.png

examples: $(EXAMPLES)
	PYTHONPATH=. python examples/visitor.py

examples/%.png: examples/%.bpmn
	bpmn-to-image $<:$@

examples/%.bpmn: examples/generate-%.py FORCE
	PYTHONPATH=. python $< | tee $@

.PHONY: FORCE
 
SCHEMA=https://www.omg.org/spec/BPMN/20100501/BPMN20.xsd

schemas:
	mkdir -p $@; cd $@; xsdata download $(SCHEMA)

bpmn_tools/models: schemas
	xsdata $< --package $(subst /,.,$@)
