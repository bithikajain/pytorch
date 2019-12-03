#!/usr/bin/env python3
#
# Computes difference between measurements produced by ./main.py.
#

import argparse
import json

import numpy as np


def load(path):
    with open(path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='PyTorch distributed benchmark diff')
    parser.add_argument("file", nargs=2)
    args = parser.parse_args()

    if len(args.file) != 2:
        raise "Must specify 2 files to diff"

    ja = load(args.file[0])
    jb = load(args.file[1])

    keys = (set(ja.keys()) | set(jb.keys())) - set(["benchmark_results"])
    print("{:20s} {:>20s}      {:>20s}".format("", "baseline", "test"))
    print("{:20s} {:>20s}      {:>20s}".format("", "-" * 20, "-" * 20))
    for key in sorted(keys):
        va = ja.get(key, "-")
        vb = jb.get(key, "-")
        print("{:20s} {:>20s}  vs  {:>20s}".format(key + ":", va, vb))
    print("")

    ba = ja["benchmark_results"]
    bb = jb["benchmark_results"]
    for ra, rb in zip(ba, bb):
        if ra["model"] != rb["model"]:
            continue
        if ra["batch_size"] != rb["batch_size"]:
            continue

        name = "{} with batch size {}".format(ra["model"], ra["batch_size"])
        print("Benchmark: {}".format(name))
        for (i, (xa, xb)) in enumerate(zip(ra["result"], rb["result"])):
            # Ignore warmup round
            if i == 0:
                continue
            if len(xa["ranks"]) != len(xb["ranks"]):
                continue

            ngpus = len(xa["ranks"])
            ma = sorted(xa["measurements"])
            mb = sorted(xb["measurements"])
            print("{:>4d} GPUs: ".format(ngpus), end='')
            for p in [75, 95]:
                va = np.percentile(ma, p)
                vb = np.percentile(mb, p)
                # We're measuring time, so lower is better (hence the negation)
                delta = -100 * ((vb - va) / va)
                print("p{:02d}:  {:1.3f} ({:+5.1f}%)  ".format(p, vb, delta), end='')
            print("")
        print("")


if __name__ == '__main__':
    main()