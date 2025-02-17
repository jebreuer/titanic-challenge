#!/bin/bash
set -e

CERT_DIR="$1"
mkdir -p "$CERT_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$CERT_DIR/tls.key" \
  -out "$CERT_DIR/tls.crt" \
  -subj "/CN=localhost" \
  -addext "subjectAltName = DNS:localhost,DNS:titanic-api.titanic-challenge.svc.cluster.local"
