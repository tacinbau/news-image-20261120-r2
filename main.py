#!/usr/bin/env python3
"""news-image-20261120 entry: a one-page newspaper front page summing up
Friday 20 November 2026 in a single image (38 dated stories, 7 regions).

The image is the entry.png beside this file, drawn for this competition;
the program only copies it to the output path. Standard library only.
Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUT, "entry.png"))
