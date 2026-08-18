import ast


def extract_imports(code: str) -> list[str]:
    tree = ast.parse(code)
    packages = set()

    for node in ast.walk(tree):

        # Example: import pandas
        if isinstance(node, ast.Import):
            for alias in node.names:
                package = alias.name.split(".")[0]
                packages.add(package)

        # Example: from sklearn.model_selection import train_test_split
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                package = node.module.split(".")[0]
                packages.add(package)

    return sorted(packages)


if __name__ == "__main__":
    test_code = """
import pandas
import requests
import numpy as np
from sklearn.model_selection import train_test_split
from matplotlib import pyplot
"""

    print(extract_imports(test_code))