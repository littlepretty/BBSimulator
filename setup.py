#!/usr/bin/env python

from setuptools import setup


setup(name='bbsimulator',
      version='0.1',
      description='The funniest joke in the world',
      url='http://github.com/littlepretty/bbsimulator',
      author='Jiaqi Yan',
      author_email='littlepretty881203@gmail.com',
      license='MIT',
      packages=['bbsimulator'],
      install_requires=[
          'enum',
          'tabulate',
          'matplotlib',
          'numpy'
      ],
      zip_safe=False)
