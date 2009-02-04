try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='monthly_i18n_reminder',
    author='Asheesh Laroia <asheesh@creativecommons.org>',
    install_requires=['setuptools',
                      'lxml>=2.0',
                      ],
    packages=find_packages(exclude=['ez_setup',]),
)
