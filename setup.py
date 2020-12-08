import setuptools
import gacha_elper

LONG_DESC = open('README.md').read()
VERSION = gacha_elper.__version__

setuptools.setup(
    name='gacha-elper',
    version=VERSION,
    author='cytopz',
    author_email='cytopz@protonmail.com',
    description='A small utility to help automate mobile (Android) video games',
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url='https://github.com/cytopz/gacha-elper',
    packages=setuptools.find_packages(),
    install_requires=['opencv-python', 'scipy', 'numpy'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6'
)
