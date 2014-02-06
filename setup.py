from setuptools import *

setup(
    name="ipop-stats",
    version="0.0.1",
    install_requires=[
        "flask>=0.10.1,<0.11",
        "SQLAlchemy>=0.9.1,<0.10.0",
    ],
    description="Gathers anonymous usage statistics of IPOP users",
    packages=find_packages(),
    scripts=["bin/ipop-stats"],
)
