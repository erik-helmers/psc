#!/usr/bin/env python3

from .benchgenv3 import *

root = Path(__file__).parent.parent

samples = root / "benchgen"
out_dir = root / "data" / "benchmarks"
out_dir.mkdir(parents=True, exist_ok=True)

with Generator(out_dir / "text_swap") as bench:
    bench.id ="text-swap"
    bench.name = "Text Swap"
    bench.content_type = "text"
    bench.description = """
Swap text in a file with random text."
"""
    bench.cover = "cover.png"

    for _ in range(8):
        bench.apply_action(samples / "text", SwapText(5, 0.05))


with Generator(out_dir / "image_swap") as bench:
    bench.id ="image-swap"
    bench.name = "Image Swap"
    bench.content_type = "image"
    bench.description = """
 Swap image in a file with random image."
    """
    bench.cover = "cover.png"

    for _ in range(8):
        bench.apply_action(samples / "images", ReplaceImage(5, 0.05))
