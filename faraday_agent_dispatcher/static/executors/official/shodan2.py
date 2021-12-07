#!/usr/bin/env python3

import os
import gzip
import sys
import subprocess
import tempfile
from pathlib import Path

from faraday_plugins.plugins.manager import PluginsManager


def main():
    shodan_query = os.environ.get("EXECUTOR_CONFIG_SHODAN_QUERY")

    with tempfile.TemporaryDirectory() as tempdirname:
        tmpdir = Path(tempdirname)
        name_result = tmpdir / "output.json.gz"

        cmd = [
            "shodan",
            "download",
            name_result,
            f'"{shodan_query}"',
        ]

        shodan_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if len(shodan_process.stdout) > 0:
            print(f"Shodan stdout: {shodan_process.stdout.decode('utf-8')}", file=sys.stderr)
        if len(shodan_process.stderr) > 0:
            print(f"Shodan stderr: {shodan_process.stderr.decode('utf-8')}", file=sys.stderr)
        plugin = PluginsManager().get_plugin("shodan")
        with gzip.open(name_result, "rb") as f:
            plugin.parseOutputString(f.read().decode("utf-8"))
            print(plugin.get_json())


if __name__ == "__main__":
    main()
