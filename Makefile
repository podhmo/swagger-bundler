SRC = swagger_bundler/tests/data

regenerate:
	swagger-bundler bundle ${SRC}/parts/product.parts.yaml > ${SRC}/xproduct.yaml
	swagger-bundler bundle ${SRC}/parts/user.parts.yaml > ${SRC}/yuser.yaml
	swagger-bundler bundle ${SRC}/parts/group.parts.yaml > ${SRC}/zgroup.yaml
	swagger-bundler bundle ${SRC}/rel/group-user.yaml > ${SRC}/gugroup-user.yaml
	swagger-bundler concat ${SRC}/yuser.yaml ${SRC}/zgroup.yaml > ${SRC}/concat-yuser-zgroup.yaml
	swagger-bundler bundle ${SRC}/rel/use-state.yaml > ${SRC}/ouse-state.yaml

test:
	python setup.py test

updatespec:
	curl http://json.schemastore.org/swagger-2.0 > swagger_bundler/schema/swagger-2.0.json

watch:
	swagger-bundler bundle ${SRC}/parts/product.parts.yaml --watch=*.yaml --outfile=${SRC}/xproduct.yaml

example:
	rm -rf .tmp; mkdir -p .tmp
	tree examples/basic > .tmp/00structure.txt
	for i in `find examples/basic/ -name "*.yaml" -type f`; do cat $$i > .tmp/01`echo $$i | tr '/' '__'`;  done
	swagger-bundler bundle examples/basic/main.yaml > .tmp/02generated.yaml
	rm -f example.rst; touch example.rst
	echo "# structure" >> example.rst
	echo "\n.. code-block:: bash" >> example.rst
	echo "" >> example.rst
	echo "$ tree" | gsed 's/^/   /g' >> example.rst
	cat .tmp/00* | gsed 's/^/   /g' >> example.rst
	echo "$ swagger-bundler bundle main.yaml > generated.yaml" | gsed 's/^/   /g' >> example.rst
	for i in `ls .tmp/01* | grep -v generated.yaml`; do echo "\n" >> example.rst; echo `echo $${i} | gsed 's@^.tmp/01examples_@@g; s@__*@/@g;'` >> example.rst; echo "\n.. code-block:: yaml\n" >> example.rst; cat $${i} | gsed 's/^/   /g' >> example.rst; done
	echo "\n" >> example.rst
	echo "## generated.yaml" >> example.rst
	echo "\n.. code-block:: yaml\n" >> example.rst
	cat .tmp/02* | gsed 's/^/   /g' >> example.rst
	rm -r .tmp

example2:
	rm -rf .tmp; mkdir -p .tmp
	tree examples/qualified-import > .tmp/00structure.txt
	for i in `find examples/qualified-import/ -name "*.yaml" -type f`; do cat $$i > .tmp/01`echo $$i | tr '/' '__'`;  done
	swagger-bundler bundle examples/qualified-import/main.yaml > .tmp/02generated.yaml
	rm -f example2.rst; touch example2.rst
	echo "# structure" >> example2.rst
	echo "\n.. code-block:: bash" >> example2.rst
	echo "" >> example2.rst
	echo "$ tree" | gsed 's/^/   /g' >> example2.rst
	cat .tmp/00* | gsed 's/^/   /g' >> example2.rst
	echo "$ swagger-bundler bundle main.yaml > generated.yaml" | gsed 's/^/   /g' >> example2.rst
	for i in `ls .tmp/01* | grep -v generated.yaml`; do echo "\n" >> example2.rst; echo `echo $${i} | gsed 's@^.tmp/01examples_@@g; s@__*@/@g;'` >> example2.rst; echo "\n.. code-block:: yaml\n" >> example2.rst; cat $${i} | gsed 's/^/   /g' >> example2.rst; done
	echo "\n" >> example2.rst
	echo "## generated.yaml" >> example2.rst
	echo "\n.. code-block:: yaml\n" >> example2.rst
	cat .tmp/02* | gsed 's/^/   /g' >> example2.rst
	rm -r .tmp

example3:
	rm -rf .tmp; mkdir -p .tmp
	tree examples/nested > .tmp/00structure.txt
	for i in `find examples/nested/ -name "*.yaml" -type f`; do cat $$i > .tmp/01`echo $$i | tr '/' '__'`;  done
	(cd examples/nested; swagger-bundler bundle main.yaml) > .tmp/02generated.yaml
	rm -f example3.rst; touch example3.rst
	echo "# structure" >> example3.rst
	echo "\n.. code-block:: bash" >> example3.rst
	echo "" >> example3.rst
	echo "$ tree" | gsed 's/^/   /g' >> example3.rst
	cat .tmp/00* | gsed 's/^/   /g' >> example3.rst
	echo "$ swagger-bundler bundle main.yaml > generated.yaml" | gsed 's/^/   /g' >> example3.rst
	echo "\n## swagger-bundler.ini(config file)" >> example3.rst
	echo "\n.. code-block::" >> example3.rst
	echo "" >> example3.rst
	cat examples/nested/swagger-bundler.ini | gsed 's/^/   /g' >> example3.rst
	for i in `ls .tmp/01* | grep -v generated.yaml`; do echo "\n" >> example3.rst; echo `echo $${i} | gsed 's@^.tmp/01examples_@@g; s@__*@/@g;'` >> example3.rst; echo "\n.. code-block:: yaml\n" >> example3.rst; cat $${i} | gsed 's/^/   /g' >> example3.rst; done
	echo "\n" >> example3.rst
	echo "## generated.yaml" >> example3.rst
	echo "\n.. code-block:: yaml\n" >> example3.rst
	cat .tmp/02* | gsed 's/^/   /g' >> example3.rst
	rm -r .tmp

example4:
	rm -rf .tmp; mkdir -p .tmp
	tree examples/mixin > .tmp/00structure.txt
	for i in `find examples/mixin/ -name "*.yaml" -type f`; do cat $$i > .tmp/01`echo $$i | tr '/' '__'`;  done
	for i in `find examples/mixin/ -name "*.py" -type f`; do cat $$i > .tmp/02`echo $$i | tr '/' '__'`;  done
	(cd examples/mixin; swagger-bundler bundle main.yaml) > .tmp/03generated.yaml
	rm -f example4.rst; touch example4.rst
	echo "# structure" >> example4.rst
	echo "\n.. code-block:: bash" >> example4.rst
	echo "" >> example4.rst
	echo "$ tree" | gsed 's/^/   /g' >> example4.rst
	cat .tmp/00* | gsed 's/^/   /g' >> example4.rst
	echo "$ swagger-bundler bundle main.yaml > generated.yaml" | gsed 's/^/   /g' >> example4.rst
	echo "\n## swagger-bundler.ini(config file)" >> example4.rst
	echo "\n.. code-block::" >> example4.rst
	echo "" >> example4.rst
	cat examples/mixin/swagger-bundler.ini | gsed 's/^/   /g' >> example4.rst
	for i in `ls .tmp/02* | grep -v generated.py`; do echo "\n" >> example4.rst; echo `echo $${i} | gsed 's@^.tmp/02examples_@@g; s@__*@/@g;'` >> example4.rst; echo "\n.. code-block:: python\n" >> example4.rst; cat $${i} | gsed 's/^/   /g' >> example4.rst; done
	echo "\n" >> example4.rst
	for i in `ls .tmp/01* | grep -v generated.yaml`; do echo "\n" >> example4.rst; echo `echo $${i} | gsed 's@^.tmp/01examples_@@g; s@__*@/@g;'` >> example4.rst; echo "\n.. code-block:: yaml\n" >> example4.rst; cat $${i} | gsed 's/^/   /g' >> example4.rst; done
	echo "\n" >> example4.rst
	echo "## generated.yaml" >> example4.rst
	echo "\n.. code-block:: yaml\n" >> example4.rst
	cat .tmp/03* | gsed 's/^/   /g' >> example4.rst
	rm -r .tmp

.PHONY: example example4
.PHONY: watch updatespec test regenerate
