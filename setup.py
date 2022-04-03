import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub == 1.*',
    'woodchips == 0.2.*',
]

DEV_REQUIREMENTS = [
    'black',
    'coveralls == 3.*',
    'flake8',
    'isort',
    'mypy',
    'pytest == 7.*',
    'pytest-cov == 3.*',
]

setuptools.setup(
    name='forks-sync',
    version='3.0.4',
    description='Keep all your git forks up to date with the remote default branch.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/forks-sync',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={'forks_sync': ['py.typed']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'forks-sync=forks_sync.cli:main',
        ],
    },
    python_requires='>=3.7, <4',
)
