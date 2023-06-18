import os
import sys
import modules.findinst
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class shader_type:
    vertex = 'v'
    fragment = 'f'

class token:
    word : str = ''
    line : int = 0
    pos : int = 0

    def __init__(self, word, line, pos):
        self.word = word
        self.line = line
        self.pos = pos

    def __str__(self) -> str:
        return str(self.line) + ':' + str(self.pos) + ' \"' + self.word + '\"'

operators = [
    '$', '%', '.', ',', ';', '*', '-', '/', '\\', '@', '#',
    '!', '^', '&', '|', '?', '(', ')', '{', '}', '[', ']'
]
def has_operator(e : str) -> bool:
    return e in operators
def tokens(content : str) -> list[str]:
    line = 1
    pos = 0
    i = 0
    prev = 0

    result = []

    for i in range(len(content)):
        e = content[i]
        if has_operator(e):
            if prev != i:
                word = content[prev:i]
                result.append(token(word, line, pos))

            result.append(token(e, line, pos))
            prev = i + 1
        elif e == ' ':
            if prev != i:
                word = content[prev:i]
                if ' ' not in word:
                    result.append(token(word, line, pos))
                prev = i + 1
        elif e == '\n':
            if prev != i:
                word = content[prev:i]
                result.append(token(word, line, pos))

            line += 1
            pos = -1
            prev = i + 1

        pos += 1

    return result
def fmt_quat(a : str, prev : str):
    return has_operator(a) or prev == '.' or prev == '(' or prev == '$' or prev == '/'
def compile_from_tokens(tokens : list[token]) -> str:
    result1 = ''
    prev_line = 1
    begin_line = False
    prev_word = ''

    for e in tokens:
        if prev_line != e.line:
            result1 = result1 + '\n'

            prev_line = e.line
            begin_line = True

        if fmt_quat(e.word, prev_word) or begin_line:
            result1 = result1 + e.word
            begin_line = False
        else:
            result1 = result1 + ' ' + e.word

        prev_word = e.word

    return result1

def format_shader(path : str) -> list[str]:
    if not os.path.exists('.cache'):
        os.mkdir('.cache')

    vertex = '.cache/' + os.path.basename(path) + '.vert.sc'
    fragment = '.cache/' + os.path.basename(path) + '.frag.sc'
    varying = '.cache/varying.def.sc'

    if os.path.exists(vertex):
        os.remove(vertex)
    if os.path.exists(fragment):
        os.remove(fragment)
    if os.path.exists(varying):
        os.remove(varying)

    file = open(path)

    ts = tokens(file.read())

    v_ts = []
    f_ts = []
    vg_ts = []

    file.close()

    io_mode = 0
    io_index = 0

    i_names = []
    o_names = []

    # 0 - declare layout
    # 1 - vertex layout
    # 2 - fragment layout
    parse_mode = 0

    i = 0
    while i != len(ts):
        e = ts[i]

        if io_mode != 0:
            if io_mode == 1:
                if e.word == 'decl':
                    io_mode = 2
                elif e.word == 'vertex':
                    parse_mode = 1
                    i += 1
                    io_mode = 0
                    continue
                elif e.word == 'fragment':
                    parse_mode = 2
                    i += 1
                    io_mode = 0
                    continue
                else:
                    io_mode = 0
            elif io_mode == 2:
                if e.word == 'input':
                    for j in range(i, len(ts)):
                        ej = ts[j]
                        if ej.word == ';':
                            dd = ts[io_index+2:j+1]
                            vg_ts = vg_ts + dd
                            i_names = i_names + [dd[1].word]
                            ts = ts[0:io_index - 1] + ts[j+1:len(ts)]
                            i = io_index - 2
                            io_mode = 0
                            io_index = 0
                            break
                        else:
                            continue
                elif e.word == 'output':
                    for j in range(i, len(ts)):
                        ej = ts[j]
                        if ej.word == ';':
                            dd = ts[io_index+2:j+1]
                            vg_ts = vg_ts + dd
                            o_names = o_names + [dd[1].word]
                            ts = ts[0:io_index - 1] + ts[j+1:len(ts)]
                            i = io_index - 2
                            io_mode = 0
                            io_index = 0
                            break
                        else:
                            continue
                else:
                    print("Ошибка (" + str(e.line) + ':' + str(e.pos) + ')!')
                    sys.exit(-1)
        else:
            if e.word == '$':
                io_mode = 1
                io_index = i + 1
                i += 1
                continue
            else:
                if parse_mode == 0:
                    if (e.word == '/' and ts[i + 1].word == '/'):
                        prev_line = e.line
                        for j in range(i, len(ts)):
                            ej = ts[j]
                            if ej.line != prev_line:
                                i = j - 1
                                break
                        i += 1
                        continue

                    if (e.word == '/' and ts[i + 1].word == '*'):
                        for j in range(i, len(ts)):
                            ej = ts[j]
                            ejn = ts[j + 1]
                            if ej.word + ejn.word == '*/':
                                i = j + 1
                                break
                        i += 1
                        continue

                    vg_ts = vg_ts + [e]
                elif parse_mode == 1:
                    v_ts = v_ts + [e]
                elif parse_mode == 2:
                    f_ts = f_ts + [e]

        i += 1

    vertex_source = compile_from_tokens(v_ts)
    fragment_source = compile_from_tokens(f_ts)
    varying_source = compile_from_tokens(vg_ts)

    if len(i_names) != 0:
        temp_source = '$input'
        for e in i_names:
            temp_source = temp_source + ' ' + e + ','
        vertex_source = temp_source[0:len(temp_source) - 1] + vertex_source

    if len(o_names) != 0:
        temp_source = '$output'
        temp_source2 = '$input'
        for e in o_names:
            temp_source = temp_source + ' ' + e + ','
            temp_source2 = temp_source2 + ' ' + e + ','
        vertex_source = temp_source[0:len(temp_source) - 1] + '\n' + vertex_source
        fragment_source = temp_source2[0:len(temp_source2) - 1] + '\n' + fragment_source

    print('----- VERTEX   ----- ')
    print(vertex_source)
    print('----- FRAGMENT ----- ')
    print(fragment_source)
    print('----- VARYING  ----- ')
    print(varying_source)
    print('----- END      ----- ')

    sources = [vertex_source, fragment_source, varying_source]
    files = [vertex, fragment, varying]

    for i in range(3):
        file = open(files[i], 'w')
        file.write(sources[i])
        file.close()

    return files

class shader_compiler:
    def __init__(self, program : modules.findinst.installation_program):
        self.program_handle = program

    def compile_shader(self, path : str, out_dir : str = None):
        if out_dir == None:
            out_dir = 'shaders/bin'
        if not os.path.exists('out_dir'):
            os.makedirs(out_dir, exist_ok=True)

        print(bcolors.OKBLUE + 'INFO' + bcolors.ENDC + ': ' + 'Компилируем шейдер ' + path + '...')
        print(bcolors.OKBLUE + 'INFO' + bcolors.ENDC + ': ' + 'Форматируем...')
        files = format_shader(path)

        print(bcolors.OKBLUE + 'INFO' + bcolors.ENDC + ': ' + 'Вызывавем компилятор...')

        types = ['v', 'f']

        for i in range(2):
            out = out_dir + '/' + os.path.basename(files[i]) + '.bin'
            program = self.program_handle.run(
                [
                    '-f', files[i], '-o', out,
                    '--type', types[i], '---varyingdef', files[2]
                ]
            )

            if program.returncode != 0:
                print("ERROR: " + path + " неправильный шейдер!!")

            os.remove(files[i])

        os.remove(files[2])