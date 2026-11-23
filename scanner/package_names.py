"""Package-name normalization helpers used by the scanner."""

import sys


PYPI_DISTRIBUTION_ALIASES = {
    "pil": "Pillow",
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
}


def normalize_pypi_name(import_name: str) -> str:
    return PYPI_DISTRIBUTION_ALIASES.get(import_name.lower(), import_name)


def is_python_stdlib(name: str) -> bool:
    return name in sys.stdlib_module_names


NODE_BUILTINS = {
    "assert", "buffer", "child_process", "cluster", "console", "constants",
    "crypto", "dgram", "diagnostics_channel", "dns", "domain", "events",
    "fs", "http", "http2", "https", "module", "net", "os", "path",
    "perf_hooks", "process", "punycode", "querystring", "readline", "repl",
    "stream", "string_decoder", "sys", "timers", "tls", "trace_events",
    "tty", "url", "util", "v8", "vm", "wasi", "worker_threads", "zlib",
}


def is_node_builtin(name: str) -> bool:
    return name.removeprefix("node:") in NODE_BUILTINS
