from setuptools import setup

setup(name='repast',
      description      = 'A REST/HTTP request manipulator',
      author           = 'Ryan Jung',
      author_email     = 'gradysghost@gmail.com',
      version          = '0.0.1',
      url              = 'https://github.com/gradysghost/repast',
      license          = 'LICENSE',
      long_description = open('README.md').read(),
      install_requires = [
        'flask',
        'pyyaml',
        'requests',
        'sqlalchemy'
      ],
      packages         = [ 'repast' ]
)

