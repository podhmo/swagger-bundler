SRC = swagger_bundler/tests/data

regenerate:
	swagger-bundler bundle ${SRC}/parts/product.parts.yaml > ${SRC}/xproduct.yaml
	swagger-bundler bundle ${SRC}/parts/user.parts.yaml > ${SRC}/yuser.yaml
	swagger-bundler bundle ${SRC}/parts/group.parts.yaml > ${SRC}/zgroup.yaml
