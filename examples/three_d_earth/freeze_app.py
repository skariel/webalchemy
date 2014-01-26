import sys
import os

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from webalchemy import server
from three_d_earth import ThreeDEarth as app

if __name__ == '__main__':

    server.generate_static(app)
