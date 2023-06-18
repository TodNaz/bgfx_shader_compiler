import subprocess
import os
import sys
import shutil
import zipfile

DEF_PATHS = []

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

class installation_program:
    def __init__(self, path):
        self.path = path

    def run(self, popenargs):
        return subprocess.run([self.path] + popenargs)

def find_installation_win32_impl(program_name):
    DEF_PATHS_FINDING = os.getenv('PATH').split(';') + DEF_PATHS
    for dir in DEF_PATHS_FINDING:
        if not os.path.exists(dir):
            continue
        for file in os.listdir(dir):
            full_path = dir + '/' + file
            if os.path.basename(file) == program_name:
                return installation_program(os.path.abspath(full_path))

    return None

def find_installation_linux_impl(program_name):
    DEF_PATHS_FINDING = os.getenv('PATH').split(':') + DEF_PATHS
    for dir in DEF_PATHS_FINDING:
        for file in os.listdir(dir):
            full_path = dir + '/' + file
            if os.path.basename(file) == program_name:
                return installation_program(os.path.abspath(full_path))

    return None

def find_installation_impl(program_name):
    if sys.platform == 'win32':
        if type(program_name) is list:
            for pn in program_name:
                return find_installation_win32_impl(pn + '.exe')
        else:
            return find_installation_win32_impl(program_name + '.exe')
    elif sys.platform == 'linux':
        if type(program_name) is list:
            for pn in program_name:
                return find_installation_linux_impl(pn)
        else:
            return find_installation_linux_impl(program_name)

def find_installation(program_name: str or list, require: bool = True):
    installation = find_installation_impl(program_name)

    if installation is None:
        if require == True:
            print(bcolors.FAIL + 'ERROR' + bcolors.ENDC + ': The "' + str(program_name) + '" нужна для продолжения!!')
            sys.exit(-1)
        else:
            print(bcolors.WARNING + 'WARNING' + bcolors.ENDC + ': The "' + str(program_name) + '" не важна, скип.')
            return None

    print(bcolors.OKBLUE + 'INFO' + bcolors.ENDC + ': "' + installation.path + '" найдена.')

    return installation