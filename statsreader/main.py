from statsutils import StatsReader
from configparser import ConfigParser
from argparse import ArgumentParser
import schedule

def read_args():
    parser = ArgumentParser()
    parser.add_argument('-c','--config',type=str,help='path to config file',default='stats.config')
    # parser.add_argument('-r','--refresh',type=int,help='interval in seconds of scheduled Fail2ban stats refresh', default=60)
    # parser.add_argument('-t','--time',type=str,help='interval start date', default=now)
    return parser.parse_args()

def read_config(config_path):
    config = ConfigParser()
    readfiles = config.read(config_path)
    if readfiles:
        # print(config['CONFIG']['Fail2banHosts'])
        return config['CONFIG']
    else:
        raise Exception('No config files found')

def setup_scheduled_refresh(config):
    reader = StatsReader(config)
    bans = reader.getBans()
    print(bans)


def main():
    args = read_args()
    config = read_config(args.config)
    setup_scheduled_refresh(config)

if __name__ == '__main__':
    main()
