import unittest
import os.path
import yaml

here = os.path.abspath(os.path.dirname(__file__))


class GenerationgTests(unittest.TestCase):
    def _callFUT(self, subcontext, *args, **kwargs):
        return subcontext.driver.transform(subcontext, *args, **kwargs)

    def _makeRootContext(self):
        from swagger_bundler.context import make_rootcontext
        from swagger_bundler.context import OptionScanner
        from swagger_bundler.drivers import FileConcatDriver
        # [(sysname, getname),...]
        scan_items = [
            ("compose", "x-bundler-compose"),
            ("concat", "x-bundler-concat"),
            ("namespace", "x-bundler-namespace"),
            ("exposed", "x-bundler-exposed"),
        ]
        scanner = OptionScanner(scan_items, driver_class=FileConcatDriver)
        return make_rootcontext(scanner)

    def test_it(self):
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/parts/product.parts.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/xproduct.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)

    def test_it__duplicated_import(self):
        # dependencies:
        # user -> {group, common}
        # group -> {common}
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/parts/user.parts.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/yuser.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)

    def test_it__exposed(self):
        # dependencies:
        # group -> {common[exposed]}
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/parts/group.parts.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/zgroup.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)

    def test_it__recursive_information(self):
        # dependencies:
        # group-user -> {group -> {common[exposed]}, user -> {group, common}}
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/rel/group-user.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/gugroup-user.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)

    def test_it__qualified_Import(self):
        # dependencies:
        # user-state -> {x-state as X -> {type[exposed]}, y-state as Y -> {type}}
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/rel/use-state.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/ouse-state.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)
