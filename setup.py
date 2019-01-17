from setuptools import setup

setup(
    name="opswrapper",
    version="0.0.1",

    packages=["opswrapper"],

    python_requires=">=3.7",
    install_requires=["numpy"],

    author="Peter Talley",
    author_email="ptalley2@vols.utk.edu",
    description="Python helpers for writing OpenSees scripts.",
    license="MIT",
)
