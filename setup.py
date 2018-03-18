from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name="peakdet",
    version=__version__,
    description="A physiological peak detection system",
    maintainer="Ross Markello",
    maintainer_email="rossmarkello@gmail.com",
    url="http://github.com/rmarkello/peakdet",
    install_requires=['numpy',
                      'scipy',
                      'matplotlib',
                      'gooey'],
    entry_points={'console_scripts': [
        'peakdet=peakdet.cli.run:main'
    ]},
    packages=find_packages(exclude=['peakdet/tests']),
    package_data={'peakdet.tests': ['data/*']},
    tests_require=['pytest'],
    license='MIT')
