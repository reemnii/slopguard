import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import requests

import cli
from scanner.extract_imports import extract_imports
from scanner.extract_npm import extract_npm_packages
from scanner.heuristics import analyze_package_metadata, calculate_risk_score
from scanner.registry_check import check_npm_exists, check_pypi_exists
from scanner.scanner import scan_code


class ExtractionTests(unittest.TestCase):
    def test_mixed_python_and_shell(self):
        self.assertEqual(extract_imports('import pandas\npip install requests'), ['pandas', 'requests'])

    def test_relative_python_imports(self):
        self.assertEqual(extract_imports('from .helpers import util\nfrom requests.api import get'), ['requests'])

    def test_pip_options_extras_and_versions(self):
        code = 'python -m pip install -r requirements.txt --index-url https://example.org "requests[socks]>=2" numpy==2 # comment'
        self.assertEqual(extract_imports(code), ['numpy', 'requests'])

    def test_multiline_js_and_scopes(self):
        code = 'import {\n x\n} from "@scope/pkg/subpath";\nexport {y} from "lodash/get";'
        self.assertEqual(extract_npm_packages(code), ['@scope/pkg', 'lodash'])

    def test_side_effect_and_dynamic_imports(self):
        self.assertEqual(extract_npm_packages('import "react"; import("axios");'), ['axios', 'react'])

    def test_local_js_modules(self):
        code = 'import x from "./file"; require("../helper"); import "/src/app"; import "#internal"; import "https://example.org/a.js";'
        self.assertEqual(extract_npm_packages(code), [])

    def test_npm_options_versions_and_scopes(self):
        code = 'npm i --registry https://example.org react@19 @scope/pkg@2 --save-dev && echo done'
        self.assertEqual(extract_npm_packages(code), ['@scope/pkg', 'react'])


class RegistryTests(unittest.TestCase):
    def test_missing_vs_unavailable(self):
        for check in (check_pypi_exists, check_npm_exists):
            for status, expected in ((404, False), (429, None), (500, None)):
                with self.subTest(check=check.__name__, status=status), patch('scanner.registry_check.requests.get', return_value=Mock(status_code=status)):
                    self.assertIs(check('example')['exists'], expected)

    def test_timeout(self):
        for check in (check_pypi_exists, check_npm_exists):
            with patch('scanner.registry_check.requests.get', side_effect=requests.Timeout('timeout')):
                self.assertIsNone(check('example')['exists'])

    def test_invalid_json(self):
        for check in (check_pypi_exists, check_npm_exists):
            response = Mock(status_code=200)
            response.json.side_effect = ValueError('invalid JSON')
            with patch('scanner.registry_check.requests.get', return_value=response):
                self.assertIsNone(check('example')['exists'])

    def test_null_project_urls(self):
        response = Mock(status_code=200)
        response.json.return_value = {'info': {'project_urls': None}, 'releases': {}}
        with patch('scanner.registry_check.requests.get', return_value=response):
            self.assertTrue(check_pypi_exists('example')['exists'])


class ScanTests(unittest.TestCase):
    def test_builtins_do_not_query_registries(self):
        with patch('scanner.scanner.check_pypi_exists') as pypi, patch('scanner.scanner.check_npm_exists') as npm:
            self.assertEqual(scan_code('import os\nimport sys', '.py'), [])
            self.assertEqual(scan_code('import "node:fs/promises"; require("path");', '.js'), [])
            pypi.assert_not_called()
            npm.assert_not_called()

    def test_python_alias(self):
        with patch('scanner.scanner.check_pypi_exists', return_value={'exists': True, 'repository_url': 'https://example.org'}) as check:
            result = scan_code('from PIL import Image', '.py')[0]
            check.assert_called_once_with('Pillow')
            self.assertEqual(result['risk_level'], 'MINIMAL')

    def test_missing_typo(self):
        with patch('scanner.scanner.check_pypi_exists', return_value={'exists': False}):
            result = scan_code('import requets', '.py')[0]
            self.assertEqual(result['risk_level'], 'HIGH')
            self.assertEqual(result['risk_score'], 90)

    def test_unknown_is_not_safe_or_missing(self):
        for extension, code, target in (('.py', 'import requests', 'check_pypi_exists'), ('.js', 'import "react";', 'check_npm_exists')):
            with patch('scanner.scanner.' + target, return_value={'exists': None, 'error': 'timeout'}):
                result = scan_code(code, extension)[0]
                self.assertEqual(result['status'], 'UNVERIFIED')
                self.assertIsNone(result['risk_score'])

    def test_unknown_cli(self):
        output = io.StringIO()
        with patch('sys.argv', ['cli.py', 'test.py']), patch('scanner.scanner.check_pypi_exists', return_value={'exists': None}), redirect_stdout(output):
            cli.main()
        self.assertIn('could not be verified', output.getvalue())

    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            scan_code('', '.txt')

    def test_risk_boundaries(self):
        self.assertEqual(calculate_risk_score(False)['risk_score'], 60)
        self.assertEqual(calculate_risk_score(True)['risk_score'], 0)
        self.assertEqual(calculate_risk_score(None)['risk_level'], 'UNKNOWN')

    def test_naive_metadata_timestamp(self):
        self.assertEqual(analyze_package_metadata({'repository_url': 'https://example.org', 'first_upload': '2020-01-01T00:00:00'}), [])


if __name__ == '__main__':
    unittest.main()
