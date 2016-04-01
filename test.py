#!/usr/bin/python3

# import re

# # Create and populate a set of all python3 listed packages on PyPI
# python3 = set()

# with open('pypi-p3') as pypi:
#     python3.update([pkg.strip().lower() for pkg in pypi])
#     # print(len(python3))

# with open('pypi-p3.5') as pypi:
#     python3.update([pkg.strip().lower() for pkg in pypi])
#     # print(len(python3))

# with open('pypi-p3.4') as pypi:
#     python3.update([pkg.strip().lower() for pkg in pypi])
#     # print(len(python3))

# with open('pypi-p3.3') as pypi:
#     python3.update([pkg.strip().lower() for pkg in pypi])
#     # print(len(python3))

# pkg = 'Python-Py-pdns'

# pkg_core = pkg.lower()
# pkg_core = re.sub("(?i)^python\d?-?", '', pkg)
# pkg_core = re.sub("(?i)^py-?", '', pkg_core)

# print(pkg_core)

# # if pkg in python3:
# #     print("a")
# for p3 in python3:
#     if pkg_core in p3:
#         print("b - %s" % p3)

# import subprocess
# p = subprocess.Popen(['xsel','-pi'], stdin=subprocess.PIPE)
# p.communicate(input="Hello, World")

# from subprocess import Popen, PIPE
# p = Popen(['xsel','-pi'], stdin=PIPE)
# p.communicate(input='Hello, World')

import sh

sh.xsel(sh.cat('data/copypasta.txt'), '-i')
