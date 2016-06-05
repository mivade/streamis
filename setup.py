import sys
from setuptools import setup

assert sys.version_info[0] > 2
if sys.version_info[0] == 3 and sys.version_info[1] < 5:
    raise RuntimeError("Python >= 3.5 is required to install Streamis.")

def read(fname):
    with open(fname, 'r') as f:
        text = f.read()
    return text

setup(
    name="streamis",
    version="0.1.0.dev",
    description="Subscribe to Redis pubsub channels via HTTP and EventSource.",
    long_description=read('README.md'),
    author="Michael V. DePalatis",
    author_email="mike@depalatis.net",
    license="MIT",
    url="https://github.com/mivade/streamis",
    py_modules=["streamis"],
    install_requires=[
        'tornado>=4.3',
        'aioredis>=0.2'
    ]
)
