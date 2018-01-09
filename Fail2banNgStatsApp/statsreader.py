from configparser import ConfigParser
from argparse import ArgumentParser
import os
import time
import schedule
from .statsutils import StatsReader, RefreshContext


def read_args():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='path to config file',
                        default='stats.config')
    parser.add_argument('-d', '--database', action='store_true', help='use django database')
    parser.add_argument('-s', '--schedule', action='store_true',
                        help='start scheduled job that requests data from fail2ban hosts')
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
    ctx.refresh_all()

def setup_scheduled_refresh(args, config):
    reader = StatsReader(config)
    ctx = RefreshContext(reader, args.database)
    #schedule.every().day.at("05:00").do(ctx.refresh)
    schedule.every(1).minutes.do(ctx.refresh_all)
    refreshcount=0
    while refreshcount<10:
        schedule.run_pending()
        time.sleep(60)
        refreshcount+=1

def main():
    args = read_args()
    config = read_config(args.config)
    if args.schedule:
        setup_scheduled_refresh(args, config)
    else:
        refresh_job(config, args.database)

if __name__ == '__main__':
    main()
