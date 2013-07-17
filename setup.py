import os
from distutils.core import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

__version__ = ''
with open('meze/__init__.py') as inp:
    for line in inp:
        if (line.startswith('__version__')):
            exec(line.strip())
            break

setup(
    name='mezzanine-meze',
    version=__version__,
    packages=['meze'],
    license='BSD License',
    description='A Mezzanine app to convert reStructuredText into HTML using Sphinx',
    long_description=README,
    url='http://github.com/abakan/meze',
    author='Ahmet Bakan',
    author_email='lordnapi@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    requires=['Sphinx'],
)
