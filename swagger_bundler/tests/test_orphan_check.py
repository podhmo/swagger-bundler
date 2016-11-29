import unittest
import os.path

here = os.path.abspath(os.path.dirname(__file__))


class OrphanCheckTests(unittest.TestCase):
    def _callFUT(self, ctx, data):
        from swagger_bundler.modifiers import orphancheck
        ctx.options["prefixing_targets"] = ["definitions", "responses", "parameters"]
        return orphancheck.check_orphan_reference(ctx, data, exception_on_fail=True)

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
        return make_rootcontext(OptionScanner(scan_items, driver_class=FileConcatDriver))

    def test_it(self):
        ctx = self._makeRootContext()

        # ref #/responses/UnexpectedError -> 404
        # ref #/definitions/XProduct -> 404 (Product is found)

        with open(os.path.join(here, "data/orphans/xproduct.yaml")) as rf:
            subcontext = ctx.make_subcontext_from_port(rf)
            with self.assertRaises(ValueError) as e:
                self._callFUT(subcontext, subcontext.data)
            self.assertEqual(len(e.exception.orphans), 2)
