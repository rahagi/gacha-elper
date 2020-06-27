import setuptools

with open('docs/README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='gacha-elper',
    version='0.0.2',
    author='cytopz',
    author_email='cytopz@protonmail.com',
    description='A small utility to help automate mobile (Android) video games',
    long_description=long_description,
    url='https://github.com/cytopz/gacha-elper',
    packages=setuptools.find_packages(),
    install_requires=['opencv-python', 'scipy', 'numpy'],
    classifier=[
        "Development Status :: 3 - Alpha"
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6'
)