import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub >= 1.51',
]

setuptools.setup(
    name='forks-sync',
    version='1.0.0',
    description='Keep all your forks up to date with the remote master branch.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/forks',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': [
            'pylint >= 2.5.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'forks=forks.sync:main'
        ]
    },
    python_requires='>=3.6',
)
