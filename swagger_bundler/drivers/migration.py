# -*- coding:utf-8 -*-
import sys
import re
import json
import logging
import os.path
from collections import namedtuple, ChainMap
from dictknife import LooseDictWalker
from dictknife.contexts import SimpleContext
from ..modifiers.ordering import ordering, make_dict
from ..langhelpers import highlight
from .. import loading
logger = logging.getLogger(__name__)


Pair = namedtuple("Pair", "ctx, composed")


class LazyJsonDump(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return json.dumps(self.data, indent=2, ensure_ascii=False)


class MigrationDriver(object):
    def __init__(self):
        self.refs = {}  # identifier, section -> (ChainMap[name] -> ref position)
        self.allrefs = {}
        self.arrived = set()
        self.candidates = ["definitions", "responses", "parameters", "paths"]
        self.rx = re.compile("#/({})/".format("|".join(self.candidates)))

    def migrate_context(self, ctx, pairs):
        logger.debug("@migrate path=%s", ctx.path)
        logger.debug("@@before migration %s", LazyJsonDump(ctx.data))

        for section in self.candidates:
            d = {name: ctx.path for name in ctx.data.get(section, [])}
            for k, v in d.items():
                if k not in self.allrefs:
                    self.allrefs[k] = v
            self.refs[(ctx.path, section)] = ChainMap(d, *[self.refs.get((p.ctx.path, section)) or {} for p in pairs])

        def on_ref(d):
            m = self.rx.search(d["$ref"])
            if m is None:
                msg = "  on where={!r}, invalid ref {!r}\n".format(ctx.path, d["$ref"])
                highlight(msg)
                return

            prefix = m.group(1)
            name = d["$ref"][m.end():]

            if prefix in ctx.data and name in ctx.data[prefix]:
                return

            refs = self.refs[(ctx.path, prefix)]

            # todo: compose
            if name not in refs:
                msg = "  on where={!r}, {!r} is not found\n".format(ctx.path, d["$ref"])
                highlight(msg)
                if name in self.allrefs:
                    highlight("    maybe file={!r}".format(self.allrefs[name]))
                return

            relpath = os.path.relpath(refs[name], start=os.path.dirname(ctx.path))
            d["$ref"] = "{}{}".format(relpath, d["$ref"])

        for section in self.candidates:
            if section not in ctx.data:
                continue

            walker = LooseDictWalker(on_container=on_ref, context_factory=SimpleContext)
            walker.walk(["$ref"], ctx.data[section])

        logger.debug("@@after migration %s", LazyJsonDump(ctx.data))

    def resolve(self, ctx, src):
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
        return data

    def run(self, basectx, inp, outp):
        ctx = basectx.make_subcontext_from_port(inp)
        self.transform(ctx, ctx.data, last=True)
        detector = ctx.detector
        ns = detector.detect_namespace()
        squash_map = make_dict()
        if ns:
            squash_map[ns] = ns

        for src in detector.detect_compose():
            if src in detector.detect_exposed():
                store = ctx.data
            else:
                store = ctx.data
                if ns:
                    if ns not in store:
                        store[ns] = make_dict()
                        squash_map[ns] = ns
                    store = store[ns]
                subctx = ctx.make_subcontext(src)
                if subctx.ns:
                    if subctx.ns not in store:
                        store[subctx.ns] = make_dict()
                        squash_map[subctx.ns] = subctx.ns
                    store = store[subctx.ns]
            k = ctx.exact_tagname("concat")
            if k not in store:
                store[k] = []
            store[k].append(src.split(" ", 1)[0])
        if ns:
            ctx.data["x-bundler-squash"] = squash_map
        return ctx

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
