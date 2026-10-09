#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "       DOCKER INVENTORY REPORT"
echo "========================================"
echo "Generated: $(date)"
echo "Host: $(hostname)"
echo

echo "========== CONTAINER INVENTORY =========="
docker ps -a --size \
  --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}\t{{.Ports}}"
echo

echo "========== IMAGE INVENTORY ============="
docker image ls \
  --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
echo

echo "========== VOLUME INVENTORY ============"
docker volume ls
echo

echo "========== DOCKER STORAGE SUMMARY ======"
docker system df
echo

echo "========== DETAILED STORAGE USAGE ======"
docker system df -v
echo

echo "Report completed."