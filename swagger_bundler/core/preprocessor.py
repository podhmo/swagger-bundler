# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


class Preprocessor:
    def __call__(self, detector, data):
        return self.preprocess_concat(detector, data)

    def preprocess_concat(self, detector, data):
        concat_members = detector.detect_concat()
        if concat_members:
            ignore_members = detector.init_exposed()
            compose_members = detector.init_compose()
            for fname in concat_members:
                ignore_members.append(fname)
                compose_members.append(fname)
        return data


DEFAULT_PREPROCESSOR = Preprocessor()
