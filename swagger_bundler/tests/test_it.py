import unittest
import os.path
import yaml

here = os.path.abspath(os.path.dirname(__file__))


class GenerationgTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from swagger_bundler import generating
        return generating.transform(*args, **kwargs)

    def test_it(self):
        from swagger_bundler import make_rootcontext

        ctx = make_rootcontext()
        with open(os.path.join(here, "data/parts/product.parts.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            result = self._callFUT(subcontext, subcontext.data)
        with open(os.path.join(here, "data/xproduct.yaml")) as rf:
            expected = yaml.load(rf)
        self.assertEqual(result, expected)
