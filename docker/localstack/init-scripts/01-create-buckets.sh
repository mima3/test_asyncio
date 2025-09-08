#!/usr/bin/env bash
set -euo pipefail

# awslocal は LocalStack 同梱の AWS CLI ラッパー
awslocal s3 mb s3://my-bucket
