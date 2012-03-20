
import sys, os
from logging.config import fileConfig
from ConfigParser import SafeConfigParser
from windmill.generator import Generator

usage = '''
Usage:
    windmill generate INI_FILE
    '''

def command():
    if len(sys.argv) != 3:
        print 'Invalid arguments'
        print usage
        sys.exit(1)

    command = sys.argv[1]
    config_file = sys.argv[2]
    if not os.path.isfile(config_file):
        print 'Invalid Config File'
        print usage
        sys.exit(1)

    config_file = os.path.abspath(config_file)
    parser = SafeConfigParser()
    parser.read([config_file])
    fileConfig([config_file]) # TODO: This should check for loggin config
                              #       and if not present set to sane defaults

    if parser.has_option('generate:main', 'base'):
        base = parser.get_option('generate:main', 'base')
    else:
        base = os.path.dirname(config_file)

    # Override other ini options here!
    g = Generator(base)
    g.update()
