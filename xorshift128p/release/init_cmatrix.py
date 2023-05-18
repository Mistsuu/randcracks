# ========================================================================
# =                     Buiding Cython's functions
# ========================================================================

import sys
import os
def buildCythonModules():
    print("[i] Cython modules are not built yet! Let me take a moment to build it, please :)")
    
    currentPath = os.path.abspath(os.getcwd())
    pythonPath = sys.executable
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(os.path.join(scriptDir, 'cython'))
    os.system(f"\"{pythonPath}\" setup.py build_ext --build-lib lib/ --build-temp tmp/")
    os.chdir(currentPath)
    
    print("[i] Cython modules are built! Please restart the script to take effect. Sorry for the inconvinience!")
    exit(0)

try:
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    includePath = os.path.join(scriptDir, 'cython/lib')
    sys.path.append(includePath)
    import cmatrix64
    import cmatrix128
    import cmatrixN

except ModuleNotFoundError as err:
    buildCythonModules()