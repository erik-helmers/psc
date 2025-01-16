import os, sys, progress.bar
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
from actions import *



class ImageAction(Action):
    def apply(self, inp: Path, out: Path):
        img = Image.open(inp)
        if inp.suffix == '.gif': img = img.convert('L')
        self.transform(img).save(out)
    def transform(self, inp: Image):
        raise NotImplementedError("Override me!")



class Gray(ImageAction):
    def transform(self, img):
        return ImageOps.grayscale(img)

class Zoom(ImageAction):
    nargs = 1
    def transform(self, img):
        width, height = img.size
        f = self.factor * 0.01
        zoomed = img.crop((width * f, height * f, width * (1-f), height * (1-f)))
        return zoomed.resize((width, height), Image.Resampling.NEAREST)

class Flip(ImageAction):
    def transform(self, img):
        return ImageOps.mirror(img)

class Blur(ImageAction):
    nargs = 1
    def transform(self, img):
        return img.filter(ImageFilter.GaussianBlur(self.factor))


class Shift(ImageAction):
    nargs = 1
    def transform(self, img):
        bounds = int(img.width * self.factor * 0.01)
        left, right = img.crop((0, 0, bounds, img.height)), img.crop((bounds, 0, img.width, img.height))
        out = img.copy()
        out.paste(right, (0, 0))
        out.paste(left, (img.width - bounds, 0))
        return out




def main():
    out_dir = Path(sys.argv[1])
    paths = list(map(Path, sys.argv[2:]))

    actions = [Ref(), Gray(), Zoom(10), Zoom(20), Zoom(30), Flip(), Blur(5), Shift(10), Shift(20), Shift(30)]

    bar = progress.bar.IncrementalBar('Generating', max=len(actions) * len(paths))
    for path in paths:
        for action in actions:
            action.run(path, out_dir)
            bar.next()

if __name__ == '__main__':
    main()
