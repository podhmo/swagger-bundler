import unittest
import os.path


here = os.path.abspath(os.path.dirname(__file__))


class GenerationgTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from swagger_bundler import generating
        return generating.transform(*args, **kwargs)

    def test_it(self):
        from swagger_bundler import loading
        with open(os.path.join(here, "data/parts/product.parts.yaml")) as rf:
            data = loading.load(rf)
            result = self._callFUT(data)
        with open(os.path.join(here, "data/xproduct.yaml")) as rf:
            expected = loading.load(rf)
        self.assertEqual(result, expected)
