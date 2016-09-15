from setuptools import setup

__version__ = '0.0.1'

setup(
    name="peakdet",
    version=__version__,
    decsription="A peak detection system",
    maintainer="Ross Markello",
    maintainer_email="rossmarkello@gmail.com",
    url="http://github.com/rmarkello/peakdet",
    packages='peakdet',
    package_data={'peakdet' : ['/data/*']},
    install_requires=['numpy','scipy'],
    license='MIT'
    )
