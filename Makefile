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

.PHONY: example example2
.PHONY: watch updatespec test regenerate
