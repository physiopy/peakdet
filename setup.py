from setuptools import setup, find_packages

__version__ = '0.0.1a'

setup(
    name="peakdet",
    version=__version__,
    description="A peak detection system",
    maintainer="Ross Markello",
    maintainer_email="rossmarkello@gmail.com",
    url="http://github.com/rmarkello/peakdet",
    install_requires=['numpy','scipy'],
    packages=find_packages(exclude=['peakdet/tests']),
    package_data={'peakdet' : ['data/*'],
                  'peakdet.tests' : ['data/*']},
    tests_require=['pytest'],
    download_url="https://github.com/rmarkello/peakdet/archive/{0}.tar.gz".format(__version__),
    license='MIT')
