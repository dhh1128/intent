#!/usr/bin/env python

import os, sys, subprocess, shlex, tempfile

def detect(compiler='clang++'):
    possible = 'integer,undefined,unsigned-integer-overflow,address,thread,memory,dataflow'.split(',')
    folder = tempfile.mkdtemp()
    available = []
    try:
        cpp = '''int main() { return 0; }'''
        cpp_path = os.path.join(folder, 'x.cpp') 
        with open(cpp_path, 'w') as f:
            f.write(cpp)
        try:
            for candidate in possible:
                try:
                    subprocess.check_output([compiler, '-fsanitize=%s' % candidate, cpp_path], stderr=subprocess.STDOUT)
                    available.append(candidate)
                except subprocess.CalledProcessError:
                    pass
        finally:
            os.remove(cpp_path)
        return available
    finally:
        os.rmdir(folder)

if __name__ == '__main__':
    compiler = 'clang++'
    if len(sys.argv) == 2:
        compiler = sys.argv[1]
    print(' '.join(detect(compiler)))

