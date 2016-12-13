# -*- coding:utf-8 -*-
import sys
import json
import logging
import os.path
from ..modifiers.ordering import ordering
from ..walkers import LooseDictWalker
from .. import loading
from collections import namedtuple, ChainMap
logger = logging.getLogger(__name__)

Pair = namedtuple("Pair", "ctx, composed")


class LazyJsonDump(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return json.dumps(self.data, indent=2, ensure_ascii=False)


class MigrationDriver:
    def __init__(self):
        self.refs = {}  # identifier, section -> (ChainMap[name] -> ref position)
        self.arrived = set()

    def migrate_context(self, ctx, pairs):
        logger.debug("@migrate path=%s", ctx.path)
        logger.debug("@@before migration %s", LazyJsonDump(ctx.data))

        for section in ctx.options["prefixing_targets"]:
            if section not in ctx.data:
                continue

            d = {name: ctx.path for name in ctx.data[section]}
            refs = self.refs[(ctx.path, section)] = ChainMap(d, *[self.refs[(p.ctx.path, section)] for p in pairs])
            # print("@@", section, list(d.keys()), "@", list(refs.keys()))
            # print("@@@", [p.ctx.path for p in pairs])

            def on_ref(d):
                prefix, name = d["$ref"].split("#/{}/".format(section), 1)
                if name in ctx.data[section]:
                    return
                # todo: compose
                relpath = os.path.relpath(refs[name], start=ctx.path)
                d["$ref"] = "{}{}".format(relpath, d["$ref"])

            walker = LooseDictWalker(on_container=on_ref)
            walker.walk(["$ref"], ctx.data[section])

        logger.debug("@@after migration %s", LazyJsonDump(ctx.data))

    def resolve(self, ctx, src):
        ctx.make_subcontext(src)
        subcontext = ctx.make_subcontext(src)
        self.transform(subcontext, subcontext.data)
        return subcontext

    def transform(self, ctx, data, namespace=None, last=False):
        if ctx.path in self.arrived:
            return data
        self.arrived.add(ctx.path)
        subfiles = ctx.detector.detect_compose()
        pairs = []
        for src in subfiles:
            subctx = self.resolve(ctx, src)
            pairs.append(Pair(ctx=subctx, composed=src not in ctx.detector.detect_exposed()))
        self.migrate_context(ctx, pairs)
        print("@", data)
        return data

    def run(self, ctx, inp, outp):
        subcontext = ctx.make_subcontext_from_port(inp)
        self.transform(subcontext, subcontext.data, last=True)

    def emit(self, ctx, replacer, dry_run=False):
        for ctx in ctx.env.pool.values():
            if dry_run:
                print(replacer(ctx.path))
            else:
                path = replacer(ctx.path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                sys.stderr.write("generate: {}\n".format(path))
                with open(path, "w") as wf:
                    ordered = ordering(ctx.data)
                    loading.dump(ordered, wf)
