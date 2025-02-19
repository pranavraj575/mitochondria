from distutils.core import setup
from setuptools import find_packages

setup(
    name='polyhedra_cut_locus',
    version='6.9.0',
    packages=find_packages(),
    install_requires=['numpy<2',
                      'scipy',
                      'matplotlib',
                      'sympy'
                      ],
    license='Liscence to Krill',
)
