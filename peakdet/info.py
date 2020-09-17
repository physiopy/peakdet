
__version__ = '0.0.1'

NAME = 'peakdet'
MAINTAINER = 'Ross Markello'
EMAIL = 'rossmarkello@gmail.com'
VERSION = __version__
LICENSE = 'Apache-2.0'
DESCRIPTION = """\
A toolbox for reproducible physiological data analysis\
"""
LONG_DESCRIPTION = 'README.rst'
LONG_DESCRIPTION_CONTENT_TYPE = 'text/x-rst'
URL = 'https://github.com/physiopy/{name}'.format(name=NAME)
DOWNLOAD_URL = ('http://github.com/physiopy/{name}/archive/{ver}.tar.gz'
                .format(name=NAME, ver=__version__))

INSTALL_REQUIRES = [
    'matplotlib',
    'numpy',
    'scipy',
]

TESTS_REQUIRES = [
    'pytest>=3.6',
    'pytest-cov'
]

EXTRAS_REQUIRES = {
    'doc': [
        'pandas',
        'sphinx>=1.2',
        'sphinx_rtd_theme'
    ],
    'tests': TESTS_REQUIRES
}

EXTRAS_REQUIRES['all'] = list(
    set([v for deps in EXTRAS_REQUIRES.values() for v in deps])
)

PACKAGE_DATA = {
    'peakdet.tests': [
        'data/*'
    ]
}

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.6',
]
