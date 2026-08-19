#!/usr/bin/env bash
# The gate for the place the secret scanner does not look. The
# repository's secret scan excludes .git/ wholesale, so a credential
# that lands in the local git configuration is invisible to it; this
# check watches exactly that file at every commit. It exists because
# an agent push once wrote a token into the branch configuration
# through a credentialed URL, and the remedy was scrubbing, which is
# not a control (AI-USAGE, D-045).
set -euo pipefail

if grep -nE "x-access-token|ghs_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+" .git/config 2>/dev/null; then
  echo "credential material in .git/config; remove it and rotate the credential" >&2
  exit 1
fi
