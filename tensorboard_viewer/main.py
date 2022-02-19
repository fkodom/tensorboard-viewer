import argparse
import os
import subprocess
import time
from functools import partial
from threading import Thread
from typing import Iterable, Optional, Union

from tensorboard_viewer.data import local_cache_context_manager, sync_tfevents_files

EPS = 1e-6


def sync_experiments(
    uris: Iterable[str],
    logdir: str,
    max_workers: Optional[int] = None,
):
    for uri in uris:
        folder_name = os.path.basename(uri.strip("/"))
        dest = os.path.join(logdir, folder_name)
        sync_tfevents_files(uri, dest, max_workers=max_workers)


def _repeatedly_sync_experiments(
    uris: Iterable[str],
    logdir: str,
    sync_interval: Union[float, int] = 30.0,
):
    logdir = logdir.removesuffix("/") + "/"
    while True:
        start = time.time()
        sync_experiments(uris=uris, logdir=logdir)
        sleep_time = max(0, sync_interval - (time.time() - start))
        time.sleep(sleep_time)


def run_tensorboard(logdir: str, *args: str):
    try:
        subprocess.check_call(["tensorboard", "--logdir", logdir, *args])
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uris", required=True, nargs="+")
    parser.add_argument("--cache-dir", type=str, default=None)
    parser.add_argument("--sync-interval", type=float, default=30.0)
    args, tensorboard_args = parser.parse_known_args()

    with local_cache_context_manager(local_path=args.cache_dir) as logdir:
        print("Syncing data...")
        sync_experiments(args.uris, logdir)

        thread_fn = partial(
            _repeatedly_sync_experiments,
            uris=args.uris,
            logdir=logdir,
            sync_interval=args.sync_interval,
        )
        sync_thread = Thread(target=thread_fn, name="sync", daemon=True)
        if args.sync_interval > EPS:
            sync_thread.start()

        run_tensorboard(logdir, *tensorboard_args)


if __name__ == "__main__":
    main()
