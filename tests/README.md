## Introduction

Folder containing the tests for this project: unit test, integration test.

We mirror the project folder tree in the folder to test to ease the tests' comprehension.

One can run the tests by using pytest library as followed:

```console
python -m pytest
```

pytest library will parse the `tests` folder for all the tests files it can find and run them.

Here is an output example:

```console
PS C:\Users\pguimon\dev\ted\ted> python -m pytest
===================== test session starts =====================
platform win32 -- Python 3.11.0, pytest-7.4.0, pluggy-1.2.0
rootdir: C:\Users\pguimon\dev\ted\ted
plugins: anyio-4.4.0, cov-4.1.0
collected 6 items

tests\services\test_Generator.py ...... [100%]

===================== 6 passed in 0.51s =====================
```

## Coverage

One can compute the tests coverage and generate a report.

Coverage python library comes into play and is part of the requirements of the pip installation, through the 
pytest-cov requirement (overlay on top of coverage python library bringing some more integration capabilities).

One can get the tests coverage ran locally by using the following command:

```console
python -m pytest --cov . --cov-report=term-missing
```

Coverage will run the testing and collect data.

A .coverage file will be created in the folder containing the tests.

In order for you to see it as a HTML report, you can type:

```console
python -m pytest --cov . --cov-report=term-missing --cov-report=html
```

This is saved in a folder named `htmlcov` and to view it, open the index.html file.

It highlights the pieces of code that are not tested.

You can exclude pieces of code from coverage: just add a file or a folder in the `.coveragerc` file in the omit section.

This file will be red the pytest library.

Here is an example:

```console
[run]
# Folders/files to omit from the coverage report
omit =  tests/*
	    venv/*
```

For instance, you usually want to remove the `venv` folder from the coverage.