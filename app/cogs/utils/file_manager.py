import asyncio
import os
import functools
from typing import IO, List


def wrap(func):
    @functools.wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


@wrap
def read_file(fp: str) -> List[str]:
    f = open(fp, "r")
    try:
        saved = f.readlines()
    finally:
        f.close()
    return saved


stat = wrap(os.stat)
rename = wrap(os.rename)
remove = wrap(os.remove)
mkdir = wrap(os.mkdir)
rmdir = wrap(os.rmdir)


@wrap
def create_file(fp: str, name: str):
    with open(fr"{fp}\{name}", "w"):
        pass


@wrap
def change_file(fp: str, text: str, mode: str, *, line: int = None):  # changed or add lines
    """
    changed file, with modes

    :param fp: path to file
    :param text: to edit
    :param mode: available modes
    modes cant be both, this mutually modes

    ========= ===============================================================
    Character Meaning
    --------- ---------------------------------------------------------------
    'append'  append to end of file
    'start'   add text to start of file
    'center'  add to center of file
    'line'    selected line ll re-write
    ========= ===============================================================

    :param line: need for 'line' mode
    * if text not ends with '\n', automacly adds char
    """
    available_modes = (
        "append", "start", "center", "line")
    fp = open(fp, "w")

    if mode not in available_modes or "w" not in fp.mode:
        fp.close()
        raise TypeError("Invalid Mode")

    if not text.endswith('\n'):
        text += "\n"

    if line:
        if mode != "line":
            raise ValueError("line and not line mode is unacaptable")  # for handling in handle
        else:
            c = change_line(fp, text, line)

    elif mode == available_modes[0]:
        c = change_line(fp=fp, text=text, line=-1)

    elif mode == available_modes[1] and line is None:
        c = change_line(fp, text, 0)

    elif mode == available_modes[2]:
        center = int(len(fp.readlines()) / 2)
        c = change_line(fp, text, center)
    fp.close()
    try:
        return c
    except NameError:
        return 1


@wrap
def change_line(fp: IO, text: str, line: int) -> int:
    saved = fp.readlines()
    if not saved:
        fp.write(text)
    saved[line] = text
    c = fp.write(saved)
    return c
