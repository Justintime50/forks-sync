import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub == 1.*',
]

DEV_REQUIREMENTS = [
    'coveralls == 3.*',
    'flake8',
    'pytest == 6.*',
    'pytest-cov == 2.*',
]

setuptools.setup(
    name='forks-sync',
    version='2.3.0',
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
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'forks-sync=forks_sync.sync:main',
        ],
    },
    python_requires='>=3.7',
)
