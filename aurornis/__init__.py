#!/usr/bin/env python3

import subprocess
import warnings

from sys import platform
from os import environ
from datetime import datetime

from .model import CommandResult

UNIX_ESC_CHAR = "\33"
WINDOWS_ESC_CHAR = "\u001b"


def run(
    command: [str],
    environment: {str: str} = None,
    remove_colors: bool = False,
    stdin: [str] = None,
    normalize_carriage_return: bool = None,
) -> CommandResult:
    """Execute the given command and return an object ready to check its result.

    >>> run(["mkdir", "-p", "/tmp/aurornis"])
    <CommandResult command="mkdir -p /tmp/aurornis" return_code=0 stdout="" stderr="">

    If you need to run the tests on both UNIX and Windows, it is recommended to set the `normalize_carriage_return` to True.
    This way, all the "\r\n" in standard output and standard error will be converted to "\n".
    **This will become the default behavior in version 2.0.**

    If the command returns a non-zero code, the successful property is false:
    >>> c = run(["python3", "-c", r"import sys; print('Oops, it didn\\'t work!', file=sys.stderr); exit(1)"], normalize_carriage_return=True)
    >>> c.successful
    False

    You can also check the execution time of your command.
    The object provides two values to facilitate your tests, one in milliseconds:
    >>> assert c.exec_time_ms < 1000

    and one in microseconds:
    >>> assert c.exec_time_us < 1000000

    You can get the text returned to the standard output and error:
    >>> c.stdout
    ''
    >>> c.stderr
    "Oops, it didn't work!\\n"

    By default, the command runs with the minimum environment variable required by the operating system (e.g. $PATH on UNIX).
    You can set new ones or overwrite the existing ones with the `environment` argument:
    >>> c = run(["env"], environment={"MY_VERY_COOL_ENV_VARIABLE": "Hello World!"}, normalize_carriage_return=True)
    >>> data = dict(entry.split("=") for entry in c.stdout.strip().split("\\n"))
    >>> data.get("LANG")
    'C'
    >>> data.get("MY_VERY_COOL_ENV_VARIABLE")
    'Hello World!'

    If the command returns colors, you can ask Aurornis to remove them automatically.
    >>> c = run(["python3", "-c", "print('\33[0;32mHello World!\33[0m')"], remove_colors=True, normalize_carriage_return=True)
    >>> c.stdout
    'Hello World!\\n'

    When `remove_color` is set to True, the `NO_COLOR` environment variable is defined to tell your command it should not output colors.
    It is recommended to take this environment variable in account, as it is becoming a standard.
    For more information, see https://no-color.org.

    If your command reads the standard input, you can give it with the `stdin` argument.
    It is a list of strings, which are joined with the end-of-line character ("\n") at execution.
    Remember that the text written in standard input does not appear in the standard output.
    >>> c = run(["python3", "-c", "who = input('Who are you? '); print(f'Hello {who}!')"], stdin=["World"], normalize_carriage_return=True)
    >>> c.successful
    True
    >>> c.stdout
    'Who are you? Hello World!\\n'

    The number of elements given in `stdin` is not verified by Aurornis, it is up to you to verify that the command
    has the expected behavior.
    >>> c = run(["python3", "-c", "who = input('Who are you? '); print(f'Hello {who}!')"], normalize_carriage_return=True)
    >>> c.successful
    False
    >>> c.stdout
    'Who are you? '
    >>> c.stderr
    'Traceback (most recent call last):\\n  File "<string>", line 1, in <module>\\nEOFError: EOF when reading a line\\n'
    """

    def _remove_colors(from_text: str) -> str:
        # Remove escape sequences.
        # They have the "\e[(mode);(ten)(unit)m" form.
        # On Windows, "\e" is replaced by the Esc character.
        # See: https://man7.org/linux/man-pages/man5/terminal-colors.d.5.html

        new_str = from_text

        for escape_char in [UNIX_ESC_CHAR, WINDOWS_ESC_CHAR]:
            for mode in range(6):
                for ten in [3, 4]:
                    for unit in range(0, 8):
                        seq = f"{escape_char}[{mode};{ten}{unit}m"
                        new_str = new_str.replace(seq, "")

            new_str = new_str.replace(f"{escape_char}[0m", "")

        return new_str

    def _get_execution_environment(
        user_environment: {str: str}, remove_colors: bool
    ) -> {str: str}:
        exec_env = {"LANG": "C"}

        if platform == "win32":
            exec_env["SystemRoot"] = environ.get("SystemRoot")
        else:
            exec_env["PATH"] = environ.get("PATH")

        if user_environment is not None:
            for key in user_environment:
                exec_env[key] = user_environment[key]

        if remove_colors:
            exec_env["NO_COLOR"] = "1"

        return exec_env

    if stdin is not None and len(stdin) > 0:
        input = "\n".join(stdin).encode("utf-8")
    else:
        input = None

    start_time = datetime.now()

    process = subprocess.Popen(
        command,
        env=_get_execution_environment(environment, remove_colors),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, stderr = process.communicate(input)

    stdout = stdout.decode()
    stderr = stderr.decode()

    if normalize_carriage_return is None:
        normalize_carriage_return = False
        warnings.warn(
            "The normalize_carriage_return argument of the run() function the will default to True in version 2.0. "
            "Set it to False manually to keep the current behavior.",
            DeprecationWarning,
        )

    if normalize_carriage_return:
        stdout = stdout.replace("\r\n", "\n")
        stderr = stderr.replace("\r\n", "\n")

    exec_time = (datetime.now() - start_time).microseconds

    if remove_colors:
        stdout, stderr = _remove_colors(stdout), _remove_colors(stderr)

    return CommandResult(command, process.returncode, stdout, stderr, exec_time)
