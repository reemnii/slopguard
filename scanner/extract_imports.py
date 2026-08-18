import ast
import re


def extract_imports(code: str) -> list[str]:
    packages = set()

    # 1. Extract normal Python imports
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    packages.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    packages.add(node.module.split(".")[0])

    except SyntaxError:
        # The input might contain shell commands such as pip install
        pass

    # 2. Extract pip install commands
    pip_pattern = r"(?:pip|pip3)\s+install\s+([^\n\r]+)"

    matches = re.findall(pip_pattern, code)

    for match in matches:
        parts = match.split()

        for package in parts:
            # Ignore command options such as --upgrade
            if package.startswith("-"):
                continue

            # Remove version specifications
            package = re.split(r"[=<>!~]", package)[0]

            if package:
                packages.add(package)

    return sorted(packages)


if __name__ == "__main__":
    test_code = """
import pandas
import requests

pip install numpy
pip install flask scikit-learn
pip install requests==2.32.0

pip install definitely-fake-ai-library
"""

    print(extract_imports(test_code))