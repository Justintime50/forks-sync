import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub >= 1.51',
]

setuptools.setup(
    name='forks-sync',
    version='2.1.0',
    description='Keep all your git forks up to date with the remote main branch.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/forks-sync',
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
            'pytest >= 6.0.0',
            'pytest-cov >= 2.10.0',
            'coveralls >= 2.1.2',
            'flake8 >= 3.8.0',
            'mock >= 4.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'forks-sync=forks_sync.sync:main'
        ]
    },
    python_requires='>=3.6',
)
