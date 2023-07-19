#!/usr/bin/env python3

from deprecation import deprecated


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
    def successful(self) -> bool:
        """Return true if and only if the command has been successful (i.e. its return code is zero)

        This property is a facilitator for ``return_code == 0``.
        It does not verify the command has actually correctly done its job, you still need to write your own tests to check it did.
        """
        return self.return_code == 0

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

    @deprecated(
        deprecated_in="1.5.0",
        removed_in="2.0.0",
        details="Use the `successful` property instead.",
    )
    def is_successful(self) -> bool:
        """Return true if and only if the command has been successful (i.e. its return code is zero)

        **Deprecated:** use the ``successful`` property instead.
        """
        return self.successful

    def __repr__(self) -> str:
        return (
            "<CommandResult"
            f' command="{" ".join(self.command)}"'
            f" return_code={self.return_code}"
            f' stdout="{self.stdout}"'
            f' stderr="{self.stderr}"'
            ">"
        )
