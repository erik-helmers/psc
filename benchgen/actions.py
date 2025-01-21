import shutil, re
from pathlib import Path

class Action:
    def __init__(self, *args):
        nargs = getattr(self.__class__, 'nargs', 0)
        if nargs != len(args):
            raise ValueError(f"Expected {nargs} arguments, got {len(args)}")

        if nargs > 0: self.factor = args[0]
        self.factors = args

    def name(self):
        # convert action name to snake_case
        base = re.sub(r'(?<!^)([A-Z])', r'_\1', self.__class__.__name__).lower()
        params = '-'.join(map(str, self.factors))
        return base + ( '-' + params if params else '' )

    def run(self, inp: Path, out_dir):
        out = out_dir / (inp.stem + "." + self.name() + inp.suffix)
        self.apply(inp, out)

    def apply(self, inp: Path, out: Path):
        raise NotImplementedError("Override me!")

class Ref(Action):
    def apply(self, inp: Path, out: Path):
        shutil.copy(inp, out)
