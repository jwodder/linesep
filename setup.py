from   os.path    import dirname, join
import re
from   setuptools import setup

with open(join(dirname(__file__), 'linesep.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

with open(join(dirname(__file__), 'README.rst')) as fp:
    long_desc = fp.read()

setup(
    name='linesep',
    version=version,
    packages=['linesep'],
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='linesep@varonathe.org',
    keywords='linebreak line break separator line-ending newline delimiters',
    description='Reading lines with arbitrary separators',
    long_description=long_desc,
    url='https://github.com/jwodder/linesep',

    install_requires=[],

    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        # Python 2.6+ only, because this uses `next()`
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],

)