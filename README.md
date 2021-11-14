# Aurornis - The Command Line Program Test Helper

Aurornis is a small, yet powerful library designed to help testing command line programs.
The name is a reference to the [_aurornis xui_](https://en.wikipedia.org/wiki/Aurornis), a prehistoric bird that lived 10 millions ago.

## Installation

Aurornis is available in PyPI, so all you need is to install it with PIP:

```bash
pip install --user aurornis
```

If you are using Pipenv, it is recommended to install it as a development dependency:

```bash
pipenv install --dev aurornis
```

## Usage

Aurornis provides a package with only one function to run a command, that returns an object with the result of the command:

```python
import aurornis

command_result = aurornis.run(["ls", "-la", "/"])
# <CommandResult command="ls -la /" return_code=0 stdout="total 68 ..." stderr="">
```

For better security and reproducibility, the environment variables of your system are not reproduced.

If you need to specify environment variables before you run the command, add them to the `run` function:

```python
import aurornis

command_result = aurornis.run(["ls", "-l", "$HOME"], environment={"HOME": "/home/deuchnord"})
```

By default, the `LANG` environment variable (used for internationalization) is reset to `C` (default system language, commonly English). You can change it if you want another language of execution.

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

## FAQ/Troubleshooting

### My tests fail in virtual environments

If you are using Aurornis in a virtual environment, you will need to add the path of its `bin` folder in the environment variable:

```python
import aurornis

aurornis.run(["python", "my-script.py"], environment={"PATH": "path/to/the/venv/bin"})
```

Note: if you use Pipenv, you can get this path with `pipenv --venv` and add `/bin` at the end of the returned path.
