from configparser import ConfigParser
from argparse import ArgumentParser
import schedule
import os

from .statsutils import StatsReader, RefreshContext


def read_args():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='path to config file',
                        default='stats.config')
    parser.add_argument('-d', '--database', action='store_true',
                        help='flag to specify if process should use django database')
    # parser.add_argument('-r', '--refresh', type=int,
    #   help='interval in seconds of scheduled Fail2ban stats refresh', default=60)
    # parser.add_argument('-t','--time',type=str,help='interval start date', default=now)
    return parser.parse_args()

def read_config(config_path):
    config = ConfigParser()
    config_path = os.path.realpath(__file__).replace('statsreader.py', config_path)
    readfiles = config.read(config_path)
    if readfiles:
        # print(config['CONFIG']['Fail2banHosts'])
        return config['CONFIG']
    else:
        raise Exception('No config files found')

def refresh_job(config, savetodb):
    reader = StatsReader(config)
    ctx = RefreshContext(reader, savetodb)
    ctx.refresh()

def setup_scheduled_refresh(args, config):
    pass

def main():
    args = read_args()
    config = read_config(args.config)
    refresh_job(config, args.database)

if __name__ == '__main__':
    main()
