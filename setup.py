import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="e-sim-game-scraper",  # https://pypi.org/project/e-sim-game-scraper
    version='0.0.1',
    author="Akiva",
    author_email="akiva0003@gmail.com",
    url=f"https://github.com/akiva0003/e-sim-game-scraper",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["lxml", "requests"],
    packages=setuptools.find_packages(),
)
