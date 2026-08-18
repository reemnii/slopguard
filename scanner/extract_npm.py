import re


def extract_npm_packages(code: str) -> list[str]:
    packages = set()

    # npm install package
    npm_pattern = r"npm\s+(?:install|i)\s+([^\n\r]+)"

    for match in re.findall(npm_pattern, code):
        for package in match.split():

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

            packages.add(package)

    # import x from "package"
    import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'

    for package in re.findall(import_pattern, code):
        packages.add(get_top_level_package(package))

    # require("package")
    require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)'

    for package in re.findall(require_pattern, code):
        packages.add(get_top_level_package(package))

    return sorted(packages)


def get_top_level_package(package: str) -> str:
    # Scoped package
    if package.startswith("@"):
        parts = package.split("/")

        if len(parts) >= 2:
            return "/".join(parts[:2])

        return package

    # lodash/get → lodash
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