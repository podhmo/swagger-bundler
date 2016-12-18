class RefSpec(object):
    def __init__(self, ref, file_path, ref_path):
        self.ref = ref
        self.file_path = file_path
        self.ref_path = ref_path

    def is_external(self):
        return self.file_path is not None

    def is_broken(self):
        return self.ref_path is None

    @classmethod
    def broken(cls, ref):
        return cls(ref, None, None)

    @classmethod
    def internal(cls, ref, ref_path):
        return cls(ref, None, ref_path)

    @classmethod
    def external(cls, ref, file_path, ref_path):
        return cls(ref, file_path, ref_path)
