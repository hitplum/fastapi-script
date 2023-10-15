
#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

__author__ = "hitplum"

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='fastapi-script',
      version='0.0.1',
      description='An extension for FastAPI',
      author='hitplum',
      author_email='ycx921101@163.com',
      url='https://github.com/hitplum/fastapi-script',
      py_modules=["fastapi-script"],
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="MIT",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License"
      ],
      python_requires='>=3.7'
      )


