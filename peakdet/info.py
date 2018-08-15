
__version__ = '0.0.1'

NAME = 'peakdet'
MAINTAINER = 'Ross Markello'
VERSION = __version__
LICENSE = 'MIT'
DESCRIPTION = 'A physiological peak detection system'
DOWNLOAD_URL = 'http://github.com/rmarkello/peakdet'

INSTALL_REQUIRES = [
    'matplotlib',
    'numpy',
    'scikit-learn',
    'scipy',
]

TESTS_REQUIRE = [
    'pytest',
    'pytest-cov'
]

PACKAGE_DATA = {
    'peakdet.tests': [
        'data/*'
    ]
}
