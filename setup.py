from setuptools import find_packages, setup


def readme():
    with open("README.md") as file:
        return file.read()


def get_requirements():
    with open("requirements.txt") as file:
        return file.read().splitlines()


setup(
    name="spandas",
    version="0.0.1",
    author="D1midr0sh",
    author_email="info@dimidrosh.ru",
    description="This is the data analysis module made by Selling Pandas team",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Selling-Pandas/spandas",
    packages=find_packages(),
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: Apache-2.0",
        "Operating System :: OS Independent",
    ],
    keywords="pandas eda analysis data science",
    project_urls={"GitHub": "https://github.com/Selling-Pandas/spandas"},
    python_requires=">=3.6",
)
