from setuptools import setup

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name="BsScore",
    version="0.2.0",
    description="モニターAI（新モデル）",
    author='yu tanaka',
    package_dir={"": "src"},
    install_requires=_requires_from_file('requirements.txt'),
    python_requires='>=3.7.0',
    include_package_data=True,
)
