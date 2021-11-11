#!/usr/bin/env python3

import subprocess


class CommandResult:
    def __init__(self, command: [str], return_code: int, stdout: str, stderr: str):
        self._command = command
        self._return_code = return_code
        self._stdout = stdout
        self._stderr = stderr

    @property
    def command(self) -> [str]:
        return self._command

    @property
    def return_code(self) -> int:
        return self._return_code

    @property
    def stdout(self) -> str:
        return self._stdout

    @property
    def stderr(self) -> str:
        return self._stderr

    def is_successful(self) -> bool:
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


def run(command: [str], environment: {str: str} = None) -> CommandResult:
    """Execute the given command and return an object ready to check its result.

    >>> run(["mkdir", "-p", "/tmp/aurornis"])
    <CommandResult command="mkdir -p /tmp/aurornis" return_code=0 stdout="" stderr="">

    If the command fails, then the is_successful() method will tell it:
    >>> c = run(["touch", "/tmp/aurornis/path/in/an/inexistent/folder.txt"])
    >>> c.is_successful()
    False

    You can get the text returned to the standard output and error:
    >>> c.stdout
    ''
    >>> c.stderr
    "touch: cannot touch '/tmp/aurornis/path/in/an/inexistent/folder.txt': No such file or directory\\n"

    By default, the command runs without any environment variable. You can set them with the second argument:
    >>> c = run(["touch", "/tmp/aurornis/path/in/an/inexistent/folder.txt"], environment={"LANG": "fr_FR.utf8"})
    >>> c.stderr
    "touch: impossible de faire un touch '/tmp/aurornis/path/in/an/inexistent/folder.txt': Aucun fichier ou dossier de ce type\\n"
    """
    process = subprocess.run(command, capture_output=True, check=False, env=environment)
    return CommandResult(
        command, process.returncode, process.stdout.decode(), process.stderr.decode()
    )
