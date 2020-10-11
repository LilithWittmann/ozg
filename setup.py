import setuptools
import os
    
with open("README.md", "r") as fh:
    long_description = fh.read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name="ozg", # Replace with your own username
    version="0.0.4",
    author="Lilith Wittmann",
    author_email="mail@lilithwittmann.de",
    include_package_data=True,
    description="Parsers/Tools to build Onlinezugangsgesetz stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LilithWittmann/ozg  ",
    install_requires=[
        'untangle',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)