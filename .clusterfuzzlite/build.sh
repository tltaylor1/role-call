#!/bin/bash -eu
# Build every harness under fuzz/ against the pinned dependency tree.
# The parsers under test import only the standard library and the
# pinned packages, so the install is the same hash-enforced step the
# pipeline runs everywhere else.
pip3 install --require-hashes -r requirements.txt
pip3 install .
for harness in fuzz/fuzz_*.py; do
  compile_python_fuzzer "$harness"
done
