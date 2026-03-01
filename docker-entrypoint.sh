#!/bin/sh
set -e

case "$1" in
  auth)  exec google-docs-auth ;;
  serve) exec google-docs-mcp  ;;
  *)     exec "$@"            ;;
esac
