#!/usr/bin/python3

import itertools
import re
import sh
import pyperclip  # Key values: http://pyautogui.readthedocs.org/en/latest/keyboard.html?highlight=ctrl
import pyautogui
import argparse
import time
import logging
import os

# User settings
def switch_to_browser():
    pyautogui.hotkey('alt', 'h')
    # pyautogui.hotkey('alt', 'tab')

def switch_back_to_terminal():
    pyautogui.hotkey('alt', 'l')
    # pyautogui.hotkey('alt', 'tab')

# Here usually you want 'ctrl', but I have highly remapped keyboard.
CTRL_KEY_IDENTIFIER = 'ctrl'


# Setup logging
logging.basicConfig(filename='output/helper.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Taken from: https://pypi.python.org/pypi?%3Aaction=index
pypi_all = set()
with open('data/pypi-all-packages') as pypi:
    pypi_all.update([pkg.strip().lower() for pkg in pypi])

# Taken from:
# * Python 3: https://pypi.python.org/pypi?:action=browse&c=533&show=all
# * Python 3.5: https://pypi.python.org/pypi?:action=browse&show=all&c=607
# * Python 3.4: https://pypi.python.org/pypi?:action=browse&show=all&c=587
# * Python 3.3: https://pypi.python.org/pypi?:action=browse&c=566
# If you want you can also use:
# * Python 3.2: https://pypi.python.org/pypi?:action=browse&show=all&c=538
# * Python 3.1: https://pypi.python.org/pypi?:action=browse&show=all&c=535
# * Python 3.0: https://pypi.python.org/pypi?:action=browse&show=all&c=534
pypi_p3 = set()
with open('data/pypi-python3-packages') as pypi:
    pypi_p3.update([pkg.strip().lower() for pkg in pypi])

with open('data/copypasta.txt') as copypasta:
    bugreport_msg = copypasta.read().strip()


# Let's parse cmd line arguments
parser = argparse.ArgumentParser(description='Process portingdb packages.')
parser.add_argument('-p', '--package', dest='package', nargs=1, help='process only package named PACKAGE')
parser.add_argument('-b', '--bug', dest='bug', nargs=1, help='solely file a bug for package named PACKAGE')
parser.add_argument('-f', '--file', dest='file', nargs=1, help='work with packages from FILE')
parser.add_argument('-a', '--after', dest='after', nargs=1, help='start after package')
parser.add_argument('-s', '--start', dest='start', nargs=1, help='start from package')
parser.add_argument('-o', '--only', dest='only', nargs=1, help='process only one package')
args = parser.parse_args()

ready = not (args.after or args.start or args.only)


# Let's start going through the packages
url_buglist = "https://apps.fedoraproject.org/packages/%s/bugs"
url_newbug = "https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&version=rawhide&component=%s"
url_pkgdb = "https://admin.fedoraproject.org/pkgdb/package/rpms/%s"
url_portingdb = "http://fedora.portingdb.xyz/pkg/%s"
url_specfile = "http://pkgs.fedoraproject.org/cgit/rpms/%s.git/tree/%s.spec"

if args.package:
    packages = [args.package[0]]
elif args.bug:
    packages = [args.bug[0]]
elif args.file:
    packages = open(args.file[0])
else:
    print("May I suggest you forgot something?")
    packages = []

for index, element in enumerate(packages):
    segments = element.strip().split()
    if len(segments) == 0:
        print("This line has no segments.")
        continue

    pkg = segments[0]
    pkglink = segments[1] if len(segments) >= 2 else None

    # Figure out where to start from
    if not ready:
        if args.after and args.after[0] == pkg:
            ready = True
            continue
        elif args.start and args.start[0] == pkg:
            ready = True
        elif args.only and args.only[0] == pkg:
            # Continue processing this package, but don't set ready.
            pass
        else:
            continue

    print("\n\n=================== %s (%s) ===================="
            % (pkg, index))

    # Search through PyPI:
    pkg_core = pkg.lower()
    pkg_core = re.sub("(?i)^python\d?-?", '', pkg_core)
    pkg_core = re.sub("(?i)^py-?", '', pkg_core)
    print("Searching PyPI for package: %s" % pkg_core)

    pypi3 = False
    print()
    for pypi_pkg in pypi_all:
        if pkg_core in pypi_pkg:
            if pypi_pkg in pypi_p3:
                print("\tFound Python3 capable package: %s" % pypi_pkg)
                pypi3 = True
            else:
                print("\tFound p2 pkg: %s" % pypi_pkg)
    print()

    sh.google_chrome(url_newbug % pkg)
    sh.google_chrome(url_buglist % pkg)
    # sh.google_chrome(url_pkgdb % pkg)
    if pkglink:
        sh.google_chrome(pkglink)
    sh.google_chrome(url_specfile % (pkg, pkg))
    sh.google_chrome(url_portingdb % pkg)
    if pypi3:
        sh.google_chrome("https://pypi.python.org/pypi?:action=browse&c=533&show=all")
    if not args.bug:
        sh.google_chrome(url_pkgdb % pkg)
        switch_back_to_terminal()
        response = input("Loaded?   (Press [Enter]; [s]kip) ")
        if response != 's':
            switch_to_browser()
            # pyautogui.typewrite(['/'], interval=0.25)
            pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'f')
            pyautogui.typewrite("upstream")
            pyautogui.typewrite(['esc'], interval=0.25)
            pyautogui.hotkey('enter')
            # pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'enter')
            # pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'shift', 'tab')
            # pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'shift', 'tab')
            pyperclip.copy('python')

    # Interactive phase
    # switch_back_to_terminal()
    response = input("Fill out new bug report?   " +
            "(Skip=leave empty; Yes=non empty; already [e]xists (just fill clipboard) ")

    if response == 'e':
        logger.info("Already exists: %s" % pkg)
        # Copy bug id to clipboard
        pyperclip.copy('1285816')
        # Copy bug text to 'Primary selection' on linux
        sh.xsel(sh.cat('data/copypasta.txt'), '-i')
    elif response:
        # Fill out the bug report
        switch_to_browser()
        pyautogui.typewrite(['esc'])
        pyautogui.typewrite('gi')
        pyautogui.typewrite(['tab'] * 17)
        pyautogui.typewrite("%s: Provide a Python 3 subpackage" % pkg)
        pyautogui.typewrite(['tab'])
        pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'a')
        pyperclip.copy(bugreport_msg)
        pyautogui.hotkey(CTRL_KEY_IDENTIFIER, 'v')
        pyautogui.typewrite(['tab'] * 3)
        pyautogui.typewrite("1285816")
        # time.sleep(0.7)
        # pyautogui.typewrite(['esc'])
        # time.sleep(0.7)
        # pyautogui.typewrite(['G', 'f'], interval=0.25)
        pyautogui.typewrite(['esc', 'esc', 'G', 'f'], interval=0.25)

        response = input("Log as successful Bug filing?   " +
                "(Yes=leave empty) ")
        if not response:
            logger.info("Filed: %s" % pkg)
        else:
            # User chose not to fill out a bug report.
            logger.info("Skipped: %s" % pkg)
    else:
        # User chose not to fill out a bug report.
        logger.info("Skipped: %s" % pkg)

    # response = input("Upstream dead?   (NO=leave empty; DEAD=non empty) ")
    # if response:
    #     logger.info("Dead-upstream: %s" % pkg)
    #     with open('portingdb-notes', 'a') as notes:
    #         notes.write("\n\n%s:\n\tdead-upstream: true" % pkg)

if not ready:
    if args.after:
        print("Could not find package: %s" % args.after[0])
    if args.start:
        print("Could not find package: %s" % args.start[1])

