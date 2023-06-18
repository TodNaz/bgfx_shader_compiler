import os
import sys

import modules.findinst
import modules.shaderc

shaderc = modules.findinst.find_installation('shaderc')
compiler = modules.shaderc.shader_compiler(shaderc)

out_dir = None

def compile_dir(dir):
    for file in os.listdir(dir):
        full_path = dir + '/' + file
        if os.path.isfile(full_path):
            ext = os.path.splitext(file)[1]
            if ext in ['.shader', '.glsl']:
                compiler.compile_shader(full_path, out_dir)
            else:
                continue

def compile_file(file):
    compiler.compile_shader(file, out_dir)

class cmd:
    def __init__(self, mode, name):
        self.mode = mode
        self.name = name

parse_mode = 0
commands = []

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        e = sys.argv[i]
        if parse_mode == 0:
            if e == '-d':
                parse_mode = 1
            elif e == '-f':
                parse_mode = 2
            elif e == '-o':
                parse_mode = 3
            elif e == '-h' or e == '--help':
                print('shaders_compile.py - программа для компиляции шейдеров bgfx, расширяя функционал.')
                print('(ПРЕДУПРЕЖДЕНИЕ: не совместим с обычнымы шейдерами)')
                print('Команды:')
                print('-d <папка> - компилировать папку с шейдерами .shader/.glsl')
                print('-f <файл> - компилировать файл с шейдером .shader/.glsl')
                print('-o <папка> - куда отправить результат компилирования (если нет папки, он её создаст)')
                print('Пример: python shaders_compile.py -f particle.glsl -d shaders/ -o bin/shaders')
                exit(0)
        elif parse_mode in [1,2]:
            commands.append(cmd(parse_mode, e))
            parse_mode = 0
        elif parse_mode == 3:
            out_dir = e
            parse_mode = 0
            
for e in commands:
    if e.mode == 1:
        compile_dir(e.name)
    elif e.mode == 2:
        compile_file(e.name)

os.rmdir('.cache')