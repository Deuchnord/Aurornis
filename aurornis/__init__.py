#!/usr/bin/env python3

import subprocess
from datetime import datetime

LINUX_ESC_CHAR = "\33"
WINDOWS_ESC_CHAR = "\u001b"


class CommandResult:
    """An object containing the result of a command"""

    def __init__(
        self,
        command: [str],
        return_code: int,
        stdout: str,
        stderr: str,
        exec_time_microseconds: int,
    ):
        self._command = command
        self._return_code = return_code
        self._stdout = stdout
        self._stderr = stderr
        self._exec_time_microseconds = exec_time_microseconds

    @property
    def command(self) -> [str]:
        """The command that gave this result"""
        return self._command

    @property
    def return_code(self) -> int:
        """The code returned by the command. Usually a number between 0 and 255 (0 meaning successful)"""
        return self._return_code

    @property
    def stdout(self) -> str:
        """The text that has been returned by the command in the standard output"""
        return self._stdout

    @property
    def stderr(self) -> str:
        """The text that has been returned by the command in the error output"""
        return self._stderr

    @property
    def exec_time_us(self) -> int:
        """The time of execution of the command in microseconds

        This can be useful if you have big constraints and want to guaranty the time execution.
        If you don't need a so precise value, you can use the `exec_time_ms` property instead.
        """
        return self._exec_time_microseconds

    @property
    def exec_time_ms(self) -> int:
        """The time of execution of the command in milliseconds

        This can be useful if you have big constraints and want to guaranty the time execution.
        If you need a more precise value, you can use the `exec_time_us` property instead.
        """
        return int(self._exec_time_microseconds / 1000)

    def is_successful(self) -> bool:
        """Return true if and only if the command has been successful (i.e. its return code is zero)

        This is just a facilitator for `return_code == 0`.
        This does not verify the command has actually correctly done its job, you still need to write your own tests to check this.
        """
        return self.return_code == 0

    def __repr__(self) -> str:
        return (
            "<CommandResult"
            f' command="{" ".join(self.command)}"'
            f" return_code={self.return_code}"
            f' stdout="{self.stdout}"'
            f' stderr="{self.stderr}"'
            ">"
        )


def run(
    command: [str],
    environment: {str: str} = None,
    remove_colors: bool = False,
    stdin: [str] = None,
) -> CommandResult:
    """Execute the given command and return an object ready to check its result.

    >>> run(["mkdir", "-p", "/tmp/aurornis"])
    <CommandResult command="mkdir -p /tmp/aurornis" return_code=0 stdout="" stderr="">

    If the command fails (i.e. it returns a non-zero code), the is_successful() method will tell it:
    >>> c = run(["touch", "/tmp/aurornis/path/in/an/inexistent/folder.txt"])
    >>> c.is_successful()
    False

    You can also check the execution time of your command.
    The object provides two values to facilitate your tests, one in milliseconds:
    >>> assert c.exec_time_ms < 500

    and one in microseconds:
    >>> assert c.exec_time_us < 500000

    You can get the text returned to the standard output and error:
    >>> c.stdout
    ''
    >>> c.stderr
    "touch: cannot touch '/tmp/aurornis/path/in/an/inexistent/folder.txt': No such file or directory\\n"

    By default, the command runs without any environment variable. You can set them with the second argument:
    >>> c = run(["env"], environment={"MY_VERY_COOL_ENV_VARIABLE": "Hello World!"})
    >>> print(c.stdout)
    MY_VERY_COOL_ENV_VARIABLE=Hello World!
    LANG=C
    <BLANKLINE>

    If the command returns colors, you can ask Aurornis to remove them automatically.
    >>> c = run(["echo", "-e", r'\e[0;32mHello World!\e[0m'], remove_colors=True)
    >>> c.stdout
    'Hello World!\\n'

    When `remove_color` is set to True, the `NO_COLOR` environment variable is defined to tell your command it should not output colors.
    It is recommended to take this environment variable in account, as it is becoming a standard.
    For more information, see https://no-color.org.

    If your command reads the standard input, you can give it with the `stdin` argument.
    It is a list of strings, which are joined with the end-of-line character ("\n") at execution.
    Remember that the text written in standard input does not appear in the standard output.
    >>> c = run(["python3", "-c", "who = input('Who are you? '); print(f'Hello {who}!')"], stdin=["World"])
    >>> c.is_successful()
    True
    >>> c.stdout
    'Who are you? Hello World!\\n'

    The number of elements given in `stdin` is not verified by Aurornis, it is up to you to verify that the command
    has the expected behavior.
    >>> c = run(["python3", "-c", "who = input('Who are you? '); print(f'Hello {who}!')"])
    >>> c.is_successful()
    False
    >>> c.stdout
    'Who are you? '
    >>> c.stderr
    'Traceback (most recent call last):\\n  File "<string>", line 1, in <module>\\nEOFError: EOF when reading a line\\n'
    """
    if environment is None:
        environment = {"LANG": "C"}

    if environment.get("LANG") is None:
        environment["LANG"] = "C"

    if remove_colors:
        # Add the standard NO_COLOR environment variable, in case the command takes it in account.
        # See: https://no-color.org/
        environment["NO_COLOR"] = "1"

    if stdin is not None and len(stdin) > 0:
        input = "\n".join(stdin).encode("utf-8")
    else:
        input = None

    start_time = datetime.now()

    process = subprocess.Popen(
        command,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )
    stdout, stderr = process.communicate(input)

    stdout = stdout.decode()
    stderr = stderr.decode()

    exec_time = (datetime.now() - start_time).microseconds

    if remove_colors:
        stdout, stderr = _remove_colors(stdout), _remove_colors(stderr)

    return CommandResult(command, process.returncode, stdout, stderr, exec_time)


def _remove_colors(from_text: str) -> str:
    # Remove escape sequences.
    # They have the "\e[(mode);(ten)(unit)m" form.
    # On Windows, "\e" is replaced by the Esc character.
    # See: https://man7.org/linux/man-pages/man5/terminal-colors.d.5.html

    new_str = from_text

    for escape_char in [LINUX_ESC_CHAR, WINDOWS_ESC_CHAR]:
        for mode in range(6):
            for ten in [3, 4]:
                for unit in range(0, 8):
                    seq = f"{escape_char}[{mode};{ten}{unit}m"
                    new_str = new_str.replace(seq, "")

        new_str = new_str.replace(f"{escape_char}[0m", "")

    return new_str
