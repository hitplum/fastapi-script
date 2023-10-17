
#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

__author__ = "hitplum"

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='fastapi-script',
      version='0.0.8',
      description='An extension for FastAPI',
      author='hitplum',
      author_email='ycx921101@163.com',
      url='https://github.com/hitplum/fastapi-script',
      packages=find_packages(),
      include_package_data=True,
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="MIT",
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: Implementation :: PyPy",
          "License :: OSI Approved :: MIT License"
      ],
      python_requires='>=3.7',
      install_requires=[
          "fastapi",
          "uvicorn"]
      )


