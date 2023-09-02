from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(10000)  # Defina o limite para um valor maior (por exemplo, 10000).
from kivy_deps import sdl2, glew

# Informações sobre o seu aplicativo
# ...

# Lista das extensões que devem ser incluídas
build_exe_options = {
    'packages': ['kivy', 'kivy.app', 'kivy.uix', 'kivy.clock', 'kivy.graphics'],
    'excludes': ['tkinter'],
    'include_msvcr': True
}

executables = [Executable("main.py")]

# Adicione o módulo kivy.weakmethod manualmente
# options = {
#     'build_exe': {
#         'packages': ['kivy.weakmethod'],
#         'include_files': ['path/para/arquivo/kivy/_weakproxy.pyx']  # Substitua pelo caminho correto
#     }
# }

# Lista das extensões Cython que devem ser compiladas
ext_modules = [
    Executable("main.py", base="Win32GUI")
]


setup(
    name="Barcode",
    version="1.0",
    description="Scanner de Código de Barras",
    options={"build_exe": build_exe_options},
    executables=ext_modules
)
