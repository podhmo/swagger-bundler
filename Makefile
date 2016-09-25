SRC = swagger_bundler/tests/data

regenerate:
	swagger-bundler bundle ${SRC}/parts/product.parts.yaml > ${SRC}/xproduct.yaml
	swagger-bundler bundle ${SRC}/parts/user.parts.yaml > ${SRC}/yuser.yaml
	swagger-bundler bundle ${SRC}/parts/group.parts.yaml > ${SRC}/zgroup.yaml
	swagger-bundler bundle ${SRC}/rel/group-user.yaml > ${SRC}/gugroup-user.yaml
	swagger-bundler concat ${SRC}/yuser.yaml ${SRC}/zgroup.yaml > ${SRC}/concat-yuser-zgroup.yaml
