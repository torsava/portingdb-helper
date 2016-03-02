#!/usr/bin/python3

import itertools
import re
import sh
import pyperclip
import pyautogui
import argparse
import time
import logging

# Setup logging
logging.basicConfig(filename='helper.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Create and populate a set of all python3 listed packages on PyPI
python3 = set()

with open('pypi-p3') as pypi:
    python3.update([pkg.strip().lower() for pkg in pypi])
    # print(len(python3))

with open('pypi-p3.5') as pypi:
    python3.update([pkg.strip().lower() for pkg in pypi])
    # print(len(python3))

with open('pypi-p3.4') as pypi:
    python3.update([pkg.strip().lower() for pkg in pypi])
    # print(len(python3))

with open('pypi-p3.3') as pypi:
    python3.update([pkg.strip().lower() for pkg in pypi])
    # print(len(python3))

with open('copypasta.txt') as copypasta:
    bugreport_msg = copypasta.read().strip()


# Go through each portingdb waiting package
# nPkgTotal = 0
# nPython3 = 0
# with open('portingdb-waiting-live') as pdb:
#     # for pkg in itertools.islice(pdb, 10):
#     for pkg in pdb:
#         pkg = pkg.strip()
#         nPkgTotal += 1
#         if pkg in python3 or re.sub("^python\d?-", '', pkg) in python3:
#             print("\tPython3 ready: %s" % pkg)
#             nPython3 += 1
#     print("\nPython3 ready total %s out of %s" % (nPython3, nPkgTotal))


# Let's parse cmd line arguments
parser = argparse.ArgumentParser(description='Process portingdb packages.')
parser.add_argument('-a', '--after', dest='after', nargs=1, help='start after package')
parser.add_argument('-f', '--from', dest='start', nargs=1, help='start from package')
parser.add_argument('-o', '--only', dest='only', nargs=1, help='process only one package')
args = parser.parse_args()

ready = not (args.after or args.start or args.only)


# Let's start going through the packages
url_buglist = "https://apps.fedoraproject.org/packages/%s/bugs"
url_newbug = "https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&version=rawhide&component=%s"
url_pkgdb = "https://admin.fedoraproject.org/pkgdb/package/rpms/%s"

with open('portingdb-waiting-live') as pdb:
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
        pkg_core = re.sub("(?i)^python\d?-?", '', pkg)
        pkg_core = re.sub("(?i)^py-?", '', pkg_core)
        print("Searching PyPI for package: %s" % pkg_core)

        pypi3 = False
        for p3 in python3:
            if pkg_core in p3:
                print("\tFound: %s" % p3)
                pypi3 = True

        sh.google_chrome(url_newbug % pkg)

        if pypi3:
            sh.google_chrome("https://pypi.python.org/pypi?:action=browse&c=533&show=all")

        sh.google_chrome(url_buglist % pkg)
        sh.google_chrome(url_pkgdb % pkg)
        pyautogui.hotkey('alt', 'l')

        input("Loaded?   (Press [Enter]) ")
        pyautogui.hotkey('alt', 'h')
        pyautogui.typewrite(['/'], interval=0.25)
        pyautogui.typewrite("upstream")
        pyautogui.typewrite(['enter'], interval=0.25)
        pyautogui.hotkey('ctrl', 'enter')
        # pyautogui.hotkey('ctrl', 'shift', 'tab')
        pyautogui.hotkey('ctrl', 'shift', 'tab')
        pyperclip.copy('python')


        # Interactive phase
        response = input("Fill out new bug report?   " +
                "(Skip=leave empty; Yes=non empty; already [e]xists) ")

        if response == 'e':
            logger.info("Already exists: %s" % pkg)
            pyperclip.copy('1285816')
            os.popen('xsel','wp').write(bugreport_msg)
        elif response:
            # Fill out the bug report
            pyautogui.hotkey('alt', 'h')
            pyautogui.typewrite(['esc'])
            pyautogui.typewrite('gi')
            pyautogui.typewrite(['tab', 'tab'])
            pyautogui.typewrite("%s: Provide a Python 3 subpackage" % pkg)
            pyautogui.typewrite(['tab'])
            pyautogui.hotkey('ctrl', 'a')
            pyperclip.copy(bugreport_msg)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.typewrite(['esc'])
            time.sleep(0.5)
            pyautogui.typewrite(['G', 'f'], interval=0.25)
            pyperclip.copy('1285816')

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

        response = input("Upstream dead?   (NO=leave empty; DEAD=non empty) ")
        if response:
            logger.info("Dead-upstream: %s" % pkg)
            with open('portingdb-notes', 'a') as notes:
                notes.write("\n\n%s:\n\tdead-upstream: true" % pkg)

    if not ready:
        if args.after:
            print("Could not find package: %s" % args.after[0])
        if args.start:
            print("Could not find package: %s" % args.after[1])

