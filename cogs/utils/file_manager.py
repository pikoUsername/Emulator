import asyncio
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
def change_file(fp: str, text: str, mode: str, *, line: int = None):  # changed or add lines
    """
    use with context manager
    example of usage
    >>> change_file("example/example.toml", text, "append")
    <<< 32 # changed lines
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
        if mode is not "line":
            raise ValueError("line and not line mode is unacaptable")  # for handling in handle
        else:
            change_line(fp, text, line)

    elif mode == available_modes[0]:
        change_line(fp=fp, text=text, line=-1)

    elif mode == available_modes[1] and line is None:
        change_line(fp, text, 0)

    elif mode == available_modes[2]:
        center = int(len(fp.readlines()) / 2)
        change_line(fp, text, center)
    if fp.closed:
        return
    fp.close()


@wrap
def change_line(fp: IO, text: str, line: int) -> int:
    saved = fp.readlines()
    if not saved:
        fp.write(text)
    saved[line] = text
    c = fp.write(saved)
    return c
