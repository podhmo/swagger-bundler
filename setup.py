# -*- coding:utf-8 -*-

import os
import sys


from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''


install_requires = [
    "PyYAML",
    "click",
    "magicalimport",
]


docs_extras = [
]

tests_require = [
]

testing_extras = tests_require + [
]

validation_extras = [
    "jsonschema"
]

watch_extras = [
    "watchdog"
]

setup(name='swagger-bundler',
      version='0.1.5',
      description='swagger schema bundler',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: Implementation :: CPython",
          'Programming Language :: Python :: 3',
      ],
      keywords='',
      author="podhmo",
      author_email="",
      url="https://github.com/podhmo/swagger-bundler",
      packages=find_packages(exclude=["swagger_bundler.tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
          "validation": validation_extras,
          "watch": watch_extras,
      },
      tests_require=tests_require,
      test_suite="swagger_bundler.tests",
      entry_points="""
      [console_scripts]
swagger-bundler=swagger_bundler.cmd:main
""")
