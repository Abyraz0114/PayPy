from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as requirements:
    required = requirements.read().splitlines()

setup(
    name="PayPy",
    version="1.0.0",
    description="PayPayをPythonから操作します。",
    author="Abyraz",
    license="GPL-3.0",
    keywords="paypay backend frontend api unofficial",
    packages=[
        "PayPy"
    ],
    requires=required,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11.5"
    ]
)