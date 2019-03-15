from miscoto.miscoto_instance import cmd_instance
from miscoto.miscoto_mincom import cmd_mincom
from miscoto.miscoto_scopes import cmd_scopes
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def main_instance(args=None):
    cmd_instance()

def main_mincom(args=None):
    cmd_mincom()

def main_scopes(args=None):
    cmd_scopes()
