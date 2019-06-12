import os
import re
from setuptools import setup, find_packages
from distutils.version import StrictVersion
import acdsl_cli

def read(fname: str) -> str:
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

version = acdsl_cli.__version__
StrictVersion(version)

dependencies = ['argparse']

setup(
    name='acdsl_cli',
    version=version,
    description='a command line interface for Amazon Cloud Drive Shared Link',
    long_description=read('README.md'),
    license='GPLv2+',
    author='hwiorn',
    author_email='hwiorn@mail.com',
    keywords=['amazon cloud drive', 'amazon cloud drive shared link', 'clouddrive'],
    url='https://github.com/top-catt/testacdsl_cli',
    download_url='https://github.com/top-catt/testacdsl_cli/archive/master.zip' + version,
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    test_suite='tests.get_suite',
    scripts=['acdsl_cli.py'],
    entry_points={'console_scripts': ['acdsl_cli = acdsl_cli:main', 'acdslcli = acdsl_cli:main'],
                  # 'acdsl_cli.plugins': ['stream = plugins.stream',
                  # 'template = plugins.template']
                  },
    install_requires=dependencies,
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 4 - Beta',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Filesystems'
    ]
)
