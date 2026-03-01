#!/bin/sh
set -e

case "$1" in
  auth)  exec gdocs-suite-auth ;;
  serve) exec gdocs-suite-mcp  ;;
  *)     exec "$@"            ;;
esac
