import unittest
import os.path
import yaml

here = os.path.abspath(os.path.dirname(__file__))


class GenerationgTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from swagger_bundler import generating
        return generating.transform(*args, **kwargs)

    def _makeRootContext(self):
        from swagger_bundler.context import make_rootcontext
        from swagger_bundler.context import Detector
        # [(sysname, getname),...]
        scan_items = [
            ("bundle", "x-bundler-bundle"),
            ("namespace", "x-bundler-namespace"),
            ("ignore_prefixer", "x-bundler-ignore-prefixer")
        ]
        return make_rootcontext(lambda config: Detector(config, scan_items))

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

    def test_it__ignore_prefixer(self):
        # dependencies:
        # group -> {common[ignore_prefixer]}
        ctx = self._makeRootContext()

        with open(os.path.join(here, "data/parts/group.parts.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/zgroup.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)
