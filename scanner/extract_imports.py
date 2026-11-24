import ast
import re
import shlex


def extract_imports(code: str) -> list[str]:
    packages = set()

    # 1. Extract normal Python imports
    try:
        cleaned = re.sub(r"(?m)^.*\b(?:pip|pip3)\s+install\b.*$|^\s*```.*$", "", code)
        tree = ast.parse(cleaned)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    packages.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    packages.add(node.module.split(".")[0])

    except SyntaxError:
        # The input might contain shell commands such as pip install
        pass

    # 2. Extract pip install commands
    pip_pattern = r"(?:pip|pip3)\s+install\s+([^\n\r]+)"

    matches = re.findall(pip_pattern, code)

    for match in matches:
        try:
            parts = shlex.split(match, comments=True)
        except ValueError:
            continue

        skip_next = False
        for package in parts:
            if skip_next:
                skip_next = False
                continue
            if package in {"-r", "--requirement", "-c", "--constraint", "-i", "--index-url", "--extra-index-url", "--trusted-host", "-t", "--target", "--proxy"}:
                skip_next = True
                continue
            if package in {"&&", ";", "||", "|"}:
                break
            # Ignore command options such as --upgrade
            if package.startswith("-"):
                continue

            # Remove version specifications
            package = re.split(r"[=<>!~]", package)[0]
            package = package.split("[")[0]

            if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", package):
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
