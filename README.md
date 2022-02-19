# tensorboard-viewer

Minimal project for aggregating and viewing remote and local Tensorboard logs.

## About

`tensorboard-viewer` aggregates Tensorboard logs into a common, local directory for viewing. It uses the `fsspec` library to interface with most any storage type, including but not limited to:
* local files
* AWS S3
* Google Storage
* Azure Storage

It does **not** rely on storage mounts like `S3FS-FUSE` or `gcsfuse`. Those solutions are convenient, but they often download more files than necessary (i.e. files not related to Tensorboard). `tensorboard-viewer` downloads only `tfevents` files, and updates them only when a change is detected in the remote file system. This helps to minimize latency and the amount of data tansmitted.

## Install

```bash
pip install "tensorboard-viewer @ git+ssh://git@github.com/fkodom/tensorboard-viewer.git"

# Install all dev dependencies (tests etc.)
pip install "tensorboard-viewer[all] @ git+ssh://git@github.com/fkodom/tensorboard-viewer.git"

# Setup pre-commit hooks
pre-commit install
```

## Usage

```bash
tensorboard-viewer \
    --uris path/to/logs-1/ gs://path/to/logs-2/ s3://path/to/logs-3/
```
Optional args:
```bash
# Persistent local directory to cache Tensorboard logs
--cache-dir path/to/dir/
# How often to check and synchronize remote data
--sync-interval 30  # (float) default: 30

# Any args you might normally provide to `tensorboard`.
# 'tensorboard-viewer' pipes those directly into the 'tensorboard' command.
```
