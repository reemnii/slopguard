import re
import shlex


def extract_npm_packages(code: str) -> list[str]:
    packages = set()

    # npm install package
    npm_pattern = r"npm\s+(?:install|i)\s+([^\n\r]+)"

    for match in re.findall(npm_pattern, code):
        try:
            tokens = shlex.split(match, comments=True)
        except ValueError:
            continue
        skip_next = False
        for package in tokens:
            if skip_next:
                skip_next = False
                continue
            if package in {"--registry", "--prefix", "--workspace", "-w", "--cache"}:
                skip_next = True
                continue
            if package in {"&&", ";", "||", "|"}:
                break

            if package.startswith("-"):
                continue

            # Remove versions
            if package.startswith("@"):
                # Scoped package: @scope/package@version
                parts = package.split("@")

                if len(parts) > 2:
                    package = "@" + parts[1]
            else:
                package = package.split("@")[0]

            if re.fullmatch(r"(?:@[\w.-]+/)?[\w.-]+", package) and not package.startswith("."):
                packages.add(package)

    # import x from "package"
    import_pattern = r'\b(?:import|export)\s+[^;]*?\s+from\s+[\'"]([^\'"]+)[\'"]'

    for package in re.findall(import_pattern, code):
        if is_package_specifier(package):
            packages.add(get_top_level_package(package))

    # require("package")
    require_pattern = r'\b(?:require|import)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'

    for package in re.findall(require_pattern, code):
        if is_package_specifier(package):
            packages.add(get_top_level_package(package))

    for package in re.findall(r"\bimport\s*['\"]([^'\"]+)['\"]", code):
        if is_package_specifier(package):
            packages.add(get_top_level_package(package))

    return sorted(packages)


def is_package_specifier(package: str) -> bool:
    return not package.startswith((".", "/", "#")) and (":" not in package or package.startswith("node:"))


def get_top_level_package(package: str) -> str:
    # Scoped package
    if package.startswith("@"):
        parts = package.split("/")

        if len(parts) >= 2:
            return "/".join(parts[:2])

        return package

    # lodash/get resolves to lodash
    return package.split("/")[0]


if __name__ == "__main__":
    test_code = """
npm install react express axios
npm install fake-ai-js-package

import React from "react";
import axios from "axios";
const express = require("express");
"""

    print(extract_npm_packages(test_code))
