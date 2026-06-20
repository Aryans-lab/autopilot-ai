"""
NanoCorp - Autonomous AI Startup System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nanocorp",
    version="2.1.0",
    author="NanoCorp Team",
    description="Autonomous AI Startup System - Build and run your startup with AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aryans-lab/nanocorp",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core - minimal dependencies for free mode
    ],
    extras_require={
        "full": [
            "openhands-sdk>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nanocorp=nanocorp.nanocorp_free:quick_start",
        ],
    },
)
