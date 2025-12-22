from setuptools import setup

setup(name='cbpi4-mail-notifications',
      version='0.0.1',
      description='CraftBeerPi Plugin to send notifications via mail',
      author='Max Sidenstjärna',
      author_email='',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-mail-notifications': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-mail-notifications'],
     )
