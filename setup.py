from distutils.core import setup

with open("README.md", "r") as f:
    README = f.read()

setup(
    name="aurornis",
    version="v1.1.0",
    packages=["aurornis"],
    scripts=[],
    url="https://github.com/Deuchnord/Aurornis",
    license="AGPL-3.0",
    author="Jérôme Deuchnord",
    author_email="jerome@deuchnord.fr",
    description="The Command Line Program Test Helper",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=[],
    python_requires=">=3.7",
)
