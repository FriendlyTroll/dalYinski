from setuptools import setup, find_packages
setup(
    name = 'dalyinski',
    version = '0.1',
    description = 'Server for dalYinski Android app',
    license='GPL v3',
    author = 'antisa',
    packages = find_packages(),
    entry_points={
        'console_scripts': [
    'dalyinski-server = server.run:main']}
)
