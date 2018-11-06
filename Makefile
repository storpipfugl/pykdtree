.PHONY: clean build

build: pykdtree/kdtree.c pykdtree/_kdtree_core.c
	python setup.py build

pykdtree/kdtree.c: pykdtree/kdtree.pyx
	cython pykdtree/kdtree.pyx

pykdtree/_kdtree_core.c: pykdtree/_kdtree_core.c.mako
	cd pykdtree && python render_template.py

clean:
	rm -rf build/
	rm -f pykdtree/*.so
