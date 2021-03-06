from configparser import ConfigParser
from argparse import ArgumentParser
import os
import sys
from threading import Event, current_thread, main_thread
import logging

import schedule

from .statsutils import StatsReader, RefreshContext, get_logger

CONFIG_PATH = '/etc/fail2ban-ng/stats.config'

def read_args():
    """Setup process arguments"""
    parser = ArgumentParser(description='Process refreshing bans data from fail2ban instances')
    parser.add_argument('-c', '--config', type=str, help='path to config file, default: {}'.format(CONFIG_PATH),
                        default=CONFIG_PATH)
    parser.add_argument('-d', '--database', action='store_true', help='use django database')
    # parser.add_argument('-s', '--schedule', action='store_true',
    #                     help='start scheduled job that requests data from fail2ban hosts')
    parser.add_argument('-t', '--time', type=str, help='time of day to refresh data '+
                        '(format: <hours>:<minutes> - hours in [0,23], minutes in [0,59])',
                        default='')
    parser.add_argument('-i', '--interval', type=str, help='time intervals between refreshing data'+
                        ' (format: <hours>:<minutes>:<seconds>, hours*3600 + minutes*60 + seconds '+
                        'must be greater then 0)',
                        default='')
    return parser.parse_args()

def read_config(config_path=CONFIG_PATH):
    """Read configuration file"""
    logger = get_logger(__name__)
    config = ConfigParser()
    if not config_path:
        msg = 'Config path empty'
        logger.error(msg)
        raise Exception(msg)

    if config_path[0] != '/':
        config_path = os.path.realpath(__file__).replace("statsreader.py", config_path)

    logger.debug("Config: {}".format(str(config_path)))
    readfiles = config.read(config_path)
    if readfiles:
        return config['config']
    else:
        msg = 'No config files found'
        logger.error(msg)
        raise Exception(msg)

def refresh_job(config, savetodb):
    """Get bans and locations from all fail2ban instances"""
    reader = StatsReader(config)
    ctx = RefreshContext(reader, savetodb)
    ctx.refresh_all()

def parse_interval(interval):
    """Parse interval argument"""
    logger = get_logger(__name__)
    try:
        interval = list(map(int, interval.split(':')))
        if len(interval) == 0:
            logger.error('Failed to parse interval {}'.format(str(interval)))
            return 0
        elif len(interval) == 1:
            return interval[0]
        elif len(interval) == 2:
            return interval[0]*60 + interval[1]
        elif len(interval) == 3:
            return interval[0]*3600 + interval[1]*60 + interval[2]
        #elif len(interval) > 3:
        logger.error('To many interval parts')
        return 0

    except ValueError:
        logger.error('Failed to parse interval {}'.format(str(interval)))
        return 0

def setup_signal_handlers(exit_event):
    def quit(signo, _frame):
        logger = get_logger(__name__)
        logger.debug('Interrupted by %d' % signo)
        exit_event.set()

    import signal
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit)

def setup_scheduled_refresh(job, args, config):
    """
    Setup scheduled refreshing of data from fail2ban instances.
    Pull data in either time intervals or at specific time of day.
    """
    logger = get_logger(__name__)
    if not args.interval and not args.time:
        logger.debug('Reading time and interval from config')
        args.interval = config['interval']
        args.time = config['time']
        if not args.interval and not args.time:
            logger.error('Refresh interval and time not specified')
            return False

    if args.interval and args.time:
        logger.debug('Please specify only one way to refresh data')
        return False

    if args.time:
        try:
            schedule.every().day.at(args.time).do(job)
        except Exception as e:
            logger.error('Failed to setup schedule with time {}'.format(str(args.time)))
            logger.debug(str(e))
            return False
        logger.info('Job scheduled every day at {}'.format(str(args.time)))

    if args.interval:
        interval = parse_interval(args.interval)
        if interval < 0:
            logger.error('Interval value is less than 0')
            return False
        schedule.every(interval).seconds.do(job)
        logger.info('Refreshing interval set to %d seconds' % interval)
    return True

def run_scheduled_refresh(args, config):
    logger = get_logger(__name__)
    reader = StatsReader(config)
    ctx = RefreshContext(reader, args.database)

    def job():
        old_hosts = reader.hosts
        try:
            config = read_config(args.config)
            reader.update_hosts(config)
        except:
            reader.hosts = old_hosts
        ctx.refresh_all()

    if not setup_scheduled_refresh(job, args, config):
        return

    exit_event = config['event'] if 'event' in config else Event()
    
    if current_thread() is main_thread():
        setup_signal_handlers(exit_event)

    while not exit_event.is_set():
        idle = schedule.idle_seconds()
        if idle > 0:
            exit_event.wait(idle)
            if exit_event.is_set():
                return

        logger.debug('Run refresh')
        schedule.run_pending()

def main():
    args = read_args()
    config = read_config(args.config)
    run_scheduled_refresh(args, config)

if __name__ == '__main__':
    main()
