import sys
from setuptools import Extension, setup
from Cython.Build import cythonize

def create_extension(extension_name):
    return Extension(extension_name, [extension_name + ".pyx"],
                     include_dirs=sys.path,
                     libraries=["gmp"])

setup(name="cython_gmpy2_matrix_F2_impl",
      ext_modules=cythonize([
                                create_extension("cmatrix64"),                          
                                create_extension("cmatrix128"),                          
                                create_extension("cmatrixN"),                          
                            ], 
      include_path=sys.path)
)