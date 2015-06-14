from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from setuptools.command.develop import develop as _develop


# The following mixin and classes will install our hook into site-packages.
# The hook was designed so that it will fail relatively gracefully if the
# package is uninstalled, so we don't bother making sure that the hook itself
# is uninstalled.

class install_mixin:
    def run(self):
        self._install_base.run(self)
        import sitehooks
        sitehooks.install(self.install_dir,
            module='sitehooks',
            func='trigger',
            append_path=self._sitehook_append_path,
            verbose=True,
        )

class install_lib(install_mixin, _install_lib):
    _sitehook_append_path = False
    _install_base = _install_lib

class develop(install_mixin, _develop):
    _sitehook_append_path = True
    _install_base = _develop


setup(
    
    name='sitehooks',
    version='0.1.0',
    description='Customize your Python startup sequence.',
    url='http://github.com/mikeboers/sitehooks',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    
    author='Mike Boers',
    author_email='sitehooks@mikeboers.com',
    license='BSD-3',

    entry_points={
        'console_scripts': {
            'sitehooks-install = sitehooks:main',
        },
    },

    cmdclass={
        'install_lib': install_lib,
        'develop': develop,
    },


)
