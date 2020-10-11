import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ozg", # Replace with your own username
    version="0.0.1",
    author="Lilith Wittmann",
    author_email="mail@lilithwittmann.de",
    description="Parsers/Tools to build Onlinezugangsgesetz stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LilithWittmann/ozg  ",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)