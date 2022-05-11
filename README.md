# Aurornis - A command line program test helper

[![Coverage Status](https://coveralls.io/repos/github/Deuchnord/Aurornis/badge.svg?branch=main)](https://coveralls.io/github/Deuchnord/Aurornis?branch=main)

Aurornis is a small, yet powerful library designed to help testing command line programs.
The name is a reference to the [_aurornis xui_](https://en.wikipedia.org/wiki/Aurornis), a prehistoric bird that lived 10 millions ago.

## Installation

Aurornis is available in PyPI, so all you need is to install it with PIP:

```bash
pip install --user aurornis
```

If you are using Pipenv or Poetry, it is recommended to install it as a development dependency:

```bash
pipenv install --dev aurornis
poetry add --dev aurornis
```

**Important note:** this library has not been tested on a production environment. For security reasons, it recommended to use it for development tests only.
This might evolve in the future.

## Main features

- One simple function: give it the command, and it will take care of all the complexity for you
- Supports the standard input, output and error
- Computes the execution time of the command, so you can test its global performance directly
- Provides a way to clean the colors to make testing simpler (with native support of the [`NO_COLOR` standard](https://no-color.org/))
- Supports Linux, macOS and Windows. Probably also works on FreeBSD.

## Basic usage

Aurornis provides a package with only one function to run a command, that returns an object with the result of the command:

```python
import aurornis

command_result = aurornis.run(["ls", "-la", "/"])
# <CommandResult command="ls -la /" return_code=0 stdout="total 68 ..." stderr="">
```

For better security and reproducibility, the environment variables of your system are not reproduced, with the exception of `$PATH` on UNIX and `SystemRoot` on Windows.

If you need to specify environment variables (or even overwrite some of them) before you run the command, add them to the `run` function:

```python
import aurornis

command_result = aurornis.run(["env"], environment={"HOME": "/home/deuchnord"})
```

By default, the `LANG` environment variable (used for internationalization) is reset to `C` (default system language, commonly English). You can change it if you want to test with another locale.

Once you get the result, all you need to do is to use your favorite unit test framework to check it returned what you expected it to return:

```python
import aurornis
import unittest

class CommandTest(unittest.TestCase):
    def test_ls_home(self):
        command_result = aurornis.run(["ls", "-l", "$HOME"], environment={"HOME": "/home/deuchnord"})
        # You can check quickly the command was successful:
        self.assertTrue(command_result.is_successful())
        # Or if you expected a more specific return value:
        self.assertEqual(2, command_result.return_code) # ls returns 2 if the file does not exist
        
        # Then, check the text returned in standard output and standard error:
        self.assertEqual("""total 6
drwxr-xr-x 1 deuchnord deuchnord 40 27 May 13:19 Desktop
drwxr-xr-x 1 deuchnord deuchnord 40 14 Oct 18:08 Documents
drwxr-xr-x 1 deuchnord deuchnord 40  1 Sep 16:52 Downloads
drwxr-xr-x 1 deuchnord deuchnord 40 29 Sep 09:11 Pictures
drwxr-xr-x 1 deuchnord deuchnord 40 11 Jun  2020 Music
drwxr-xr-x 1 deuchnord deuchnord 40 10 Nov 11:32 Videos""", command_result.stdout)
        self.assertEqual("", command_result.stderr)
```

If your command returns colors in your standard output or standard error, you can ask Aurornis to automatically remove them:

```python
import aurornis

aurornis.run(["echo", "-e", r'\e[0;32mHello World!\e[0m'], remove_colors=True)
```

This option also automatically sets [the standard `NO_COLOR` environment variable](https://no-color.org). If your application shows colors, you may want to handle this environment variable to facilitate their deactivation by end users.

## FAQ/Troubleshooting

### How to handle correctly the return lines when my tests are executed on both Windows and non-Windows systems? 

Since version 1.4, the `run()` function provides a way to handle it for you. To activate it, set the `normalize_carriage_return` argument to `True`.

If you use a previous version, you can reproduce this behavior easily by replacing the `\r\n` characters with `\n` on both `stdout` and `stderr`.
