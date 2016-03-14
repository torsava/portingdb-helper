#!/usr/bin/python3

import itertools
import re
import sh
import pyperclip
import pyautogui
import argparse
import time
import logging

# User settings
def switch_to_browser():
    # pyautogui.hotkey('alt', 'h')
    pyautogui.hotkey('alt', 'tab')

def switch_back_to_terminal():
    # pyautogui.hotkey('alt', 'l')
    pyautogui.hotkey('alt', 'tab')


# Setup logging
logging.basicConfig(filename='helper.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Create and populate a set of PyPI packages.
pypi_all = set()
pypi_p3 = set()

with open('pypi-all-packages') as pypi:
    pypi_all.update([pkg.strip().lower() for pkg in pypi])

with open('pypi-p3-combined') as pypi:
    pypi_p3.update([pkg.strip().lower() for pkg in pypi])

with open('copypasta.txt') as copypasta:
    bugreport_msg = copypasta.read().strip()


# Let's parse cmd line arguments
parser = argparse.ArgumentParser(description='Process portingdb packages.')
parser.add_argument('-a', '--after', dest='after', nargs=1, help='start after package')
parser.add_argument('-f', '--from', dest='start', nargs=1, help='start from package')
parser.add_argument('-o', '--only', dest='only', nargs=1, help='process only one package')
parser.add_argument('-p', '--package', dest='package', nargs=1, help='process only package named PACKAGE')
args = parser.parse_args()

ready = not (args.after or args.start or args.only)


# Let's start going through the packages
url_buglist = "https://apps.fedoraproject.org/packages/%s/bugs"
url_newbug = "https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&version=rawhide&component=%s"
url_pkgdb = "https://admin.fedoraproject.org/pkgdb/package/rpms/%s"

with open('portingdb-waiting-live') as pdb:
    if args.package:
        pdb = [args.package[0]]

    for pkg in pdb:
        pkg = pkg.strip()

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

        print("\n\n=================== %s ====================" % pkg)

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

        if pypi3:
            sh.google_chrome("https://pypi.python.org/pypi?:action=browse&c=533&show=all")

        sh.google_chrome(url_buglist % pkg)
        sh.google_chrome(url_pkgdb % pkg)
        switch_back_to_terminal()

        response = input("Loaded?   (Press [Enter]; [s]kip) ")
        if response != 's':
            switch_to_browser()
            # pyautogui.typewrite(['/'], interval=0.25)
            pyautogui.hotkey('ctrl', 'f')
            pyautogui.typewrite("upstream")
            pyautogui.typewrite(['esc'], interval=0.25)
            pyautogui.hotkey('ctrl', 'enter')
            # pyautogui.hotkey('ctrl', 'shift', 'tab')
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            pyperclip.copy('python')

        response = input("Next?   ([enter] to continue)")

        # # Interactive phase
        # response = input("Fill out new bug report?   " +
        #         "(Skip=leave empty; Yes=non empty; already [e]xists) ")

        # if response == 'e':
        #     logger.info("Already exists: %s" % pkg)
        #     pyperclip.copy('1285816')
        #     os.popen('xsel','wp').write(bugreport_msg)
        # elif response:
        #     # Fill out the bug report
        #     switch_to_browser()
        #     pyautogui.typewrite(['esc'])
        #     pyautogui.typewrite('gi')
        #     pyautogui.typewrite(['tab', 'tab'])
        #     pyautogui.typewrite("%s: Provide a Python 3 subpackage" % pkg)
        #     pyautogui.typewrite(['tab'])
        #     pyautogui.hotkey('ctrl', 'a')
        #     pyperclip.copy(bugreport_msg)
        #     pyautogui.hotkey('ctrl', 'v')
        #     pyautogui.typewrite(['esc'])
        #     time.sleep(0.5)
        #     pyautogui.typewrite(['G', 'f'], interval=0.25)
        #     pyperclip.copy('1285816')

        #     response = input("Log as successful Bug filing?   " +
        #             "(Yes=leave empty) ")
        #     if not response:
        #         logger.info("Filed: %s" % pkg)
        #     else:
        #         # User chose not to fill out a bug report.
        #         logger.info("Skipped: %s" % pkg)
        # else:
        #     # User chose not to fill out a bug report.
        #     logger.info("Skipped: %s" % pkg)

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

