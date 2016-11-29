import yaml
from collections import OrderedDict


def make_dict():
    return OrderedDict()


def ordering(data):
    d = make_dict()
    used = set()
    expected = [
        "swagger", "info", "host", "schemes", "basePath", "consumes", "produces",
        "definitions", "responses", "paths"
    ]
    for k in expected:
        if k in data:
            used.add(k)
            d[k] = data[k]
    for k, v in data.items():
        if k not in used:
            d[k] = data[k]
    return d


def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())


def construct_odict(loader, node):
    return OrderedDict(loader.construct_pairs(node))


def setup():
    yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_odict)
    yaml.add_constructor(u'tag:yaml.org,2002:map', construct_odict)
    yaml.add_representer(OrderedDict, represent_odict)
