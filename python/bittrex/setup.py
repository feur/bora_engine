from setuptools import setup

setup(name='aurade',
      version='0.1',
      description='aurade',
      author='ammo',
      author_email='',
      license='',
      install_requires=[
          'requests','MySQL-python', 'python_bittrex'
      ],
      dependency_links=['https://codeload.github.com/ericsomdahl/python-bittrex/zip/master#egg=python_bittrex-0.2.0'],
      zip_safe=False)
