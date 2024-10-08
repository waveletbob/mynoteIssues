# Python 编程笔记
## AI框架
* pytorch
* tensorflow
* keras

## virtualenv
```shell
pip install virtualenv
virtualenv venv
source venv/bin/activate
deactivate
```
## miniconda
https://docs.conda.io/en/latest/miniconda.html
conda create -n textgen python=3.10.9
conda activate textgen

conda env list

## setup.py

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
from os import path
from codecs import open
from setuptools import setup,Command,find_packages
"""
------------------------------------
# @FileName    :setup.py
# @Time        :2023/07/20 10:21 AM
# @Author      :
# @description :
------------------------------------
"""

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line]

setup(
    name='',
    version='',
    description="",
    long_description=long_description,
    long_description_content_type='text/markdown',  # This field specifies the format of the `long_description`.
    packages=find_packages(),
    # package_data={'gpt_code_ui.webapp': ['static/*', 'static/assets/*']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'geminigpt = gpt_code_ui.main:main',
        ],
    },
)

```