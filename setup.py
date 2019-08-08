import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MechOS",
    version="0.0.1",
    author="David Pierc Walker-Howell",
    author_email="piercedhowell@gmail.com",
    description="Mechatronics operating system for modular robotic systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mechatronics-SDSU/MechOS",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
