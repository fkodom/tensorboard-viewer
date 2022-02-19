import logging
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import lru_cache, partial
from typing import ContextManager, List, Optional, Tuple, Union

import fsspec
from tqdm import tqdm


@lru_cache(maxsize=8)
def cached_filesystem(protocol: str) -> fsspec.AbstractFileSystem:
    return fsspec.filesystem(protocol)


def filesystem_from_uri(uri: str) -> fsspec.AbstractFileSystem:
    if "://" in uri:
        protocol = uri.split("://")[0]
    else:
        protocol = "file"
    return cached_filesystem(protocol)


def get_protocol_from_filesystem(fs: fsspec.AbstractFileSystem) -> str:
    protocol: Union[str, Tuple[str]] = fs.protocol
    if isinstance(protocol, tuple):
        protocol = protocol[0]
    assert isinstance(protocol, str)
    return protocol


@lru_cache(maxsize=2048)
def _download_if_changed_size(uri: str, dest: str, size: int, protocol: str) -> str:
    assert isinstance(size, int)
    fs: fsspec.AbstractFileSystem = fsspec.filesystem(protocol)
    fs.download(uri, dest)
    return dest


def _cached_download(uri: str, dest: str, fs: fsspec.AbstractFileSystem) -> str:
    size = fs.size(uri)
    protocol = get_protocol_from_filesystem(fs)
    return _download_if_changed_size(uri, dest, size, protocol)


def sync_file(uri: str, dest: str) -> str:
    fs = filesystem_from_uri(uri)
    return _cached_download(uri, dest, fs)


def sync_tfevents_files(
    uri: str,
    dest: str,
    max_workers: Optional[int] = None,
    show_progress: bool = False,
) -> List[str]:
    fs = filesystem_from_uri(uri)
    dir_path = uri.split("://")[1]
    paths: List[str] = fs.glob(os.path.join(uri, "**/*tfevents*"))

    relative_paths = [f.removeprefix(dir_path).strip("/") for f in paths]
    dest_paths = [os.path.join(dest, f) for f in relative_paths]

    logging.info(f"Downloading 'tfevents' files from '{uri}' to '{dest}'")
    pool = ThreadPoolExecutor(max_workers=max_workers)
    download_fn = partial(_cached_download, fs=fs)
    futures = pool.map(download_fn, paths, dest_paths)
    _ = [f for f in tqdm(futures, total=len(paths), disable=not show_progress)]

    return dest_paths


def local_cache_context_manager(local_path: Optional[str] = None) -> ContextManager:
    if local_path is None:
        return tempfile.TemporaryDirectory()

    @contextmanager
    def _local_context_manager():
        yield os.path.abspath(local_path)

    if os.path.exists(local_path):
        resp = input(f"Folder {local_path} already exists. Overwrite? (y/N): ")
        if resp.lower() == "y":
            shutil.rmtree(local_path)
    os.makedirs(local_path, exist_ok=True)
    return _local_context_manager()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with tempfile.TemporaryDirectory() as tempdir:
        paths = sync_tfevents_files(
            "gs://frank-odom/experiments", tempdir, show_progress=True
        )
        paths = sync_tfevents_files(
            "gs://frank-odom/experiments", tempdir, show_progress=True
        )
        breakpoint()
        pass
