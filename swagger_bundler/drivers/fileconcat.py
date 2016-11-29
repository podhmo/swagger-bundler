from ..modifiers import bundling


class FileConcatDriver:
    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, rf, wf, namespace=None):
        return bundling.run(self.ctx, rf, wf, namespace=namespace)
