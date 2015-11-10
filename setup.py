#!/usr/bin/env python

from setuptools import setup  # , find_packages
from aiomotorengine import __version__

tests_require = [
    'nose',
    'coverage',
    'rednose',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'mongoengine',
    'docutils',
    'jinja2',
    'sphinx',
]

setup(
    name='aiomotorengine',
    version=__version__,
    description='MotorEngine is a port of the amazing MongoEngine Mapper. Instead of using pymongo, MotorEngine uses Motor.',
    long_description='''
MotorEngine is a port of the amazing MongoEngine Mapper. Instead of using pymongo, MotorEngine uses Motor.
''',
    keywords='database mongodb asyncio python',
    author='Bernardo Heynemann',
    # author_email='heynemann@gmail.com',
    # url='http://github.com/heynemann/aiomotorengine/',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    # packages=find_packages(),
    packages=['aiomotorengine'],
    include_package_data=True,
    install_requires=[
        'pymongo==2.8',
        'motor==0.5.dev0',
        'six',
        'easydict'
    ],
    dependency_links=[
        'https://github.com/mongodb/motor/archive/master.zip#egg=motor-0.5.dev0'
    ],
    use_2to3=True,
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
