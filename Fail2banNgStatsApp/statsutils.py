import asyncio
import time
import logging
import sys
import collections

def get_logger(name, args=None, config=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s')
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

class StatsReader():
    def __init__(self, config):
        self.logger = get_logger(__name__)
        self.hosts = []
        self.update_hosts(config)

    def get(self, request):
        responses = []
        async def _get(host):
            self.logger.debug('get {} from {}'.format(request, str(host)))
            try:
                reader, writer = await asyncio.open_connection(**host)
                connected = True
            except:
                self.logger.warning('Failed to connect {}'.format(str(host)))
                connected = False
            
            if not connected: return

            self.logger.info('connected {}'.format(str(host)))
            msg = (request+'\n').encode()
            writer.write(msg)
            await writer.drain()
            self.logger.debug('sent {} {}'.format(request, str(host)))
            firstbyte = await reader.read(1)
            if firstbyte == b'\n':
                self.logger.info("No data from {}".format(str(host)))
                writer.close()
                return

            response = await reader.readuntil('\n\n'.encode())
            response = firstbyte.decode() + response.decode()
            # "filter bool" removes empty strings
            response = list(filter(bool, response.split('\n')))
            responses.append((host, response))
            self.logger.debug('from {}: {}'.format(str(host), str(response)))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = []
        for host in self.hosts:
            tasks.append(asyncio.ensure_future(_get(host)))
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        return responses

    def getBans(self, prev_refresh_time):
        request = 'BANS'
        if prev_refresh_time is not None and isinstance(prev_refresh_time, int):
            request += ' ' + str(prev_refresh_time)
        return self.get(request)

    def getLocations(self):
        return self.get('LOCATIONS')

    def update_hosts(self, config):
        def hoststr_to_dict(hoststr):
            self.logger.debug(hoststr)
            host = hoststr.split(':')
            return {'host':host[0], 'port':host[1]}
        self.hosts = list(map(hoststr_to_dict, config['fail2banhosts'].split('\n')))


RefreshResult = collections.namedtuple('RefreshResult', 'result error')


class RefreshContext():
    def __init__(self, statsreader, savetodb=False):
        self.logger = get_logger(__name__)
        self.__reader = statsreader
        self.__savetodb = savetodb
        self.__prev_refresh_time = None 

        if savetodb:
            from .statsdb import StatsDatabase
            self.__database = StatsDatabase()
            self.__init_last_refresh()
        else:
            self.__database = None
            self.__last_refresh = None

    def __init_last_refresh(self):
        def func():
            from .models import LastRefreshTableData
            last_refresh = LastRefreshTableData.objects.all().first()
            if not last_refresh:
                last_refresh = LastRefreshTableData()
                last_refresh.time = 0
                last_refresh.save()
            self.__last_refresh = last_refresh
        self.__locked(func)

    def __locked(self, func):
        if self.__savetodb:
            from django.conf import settings
            lock = settings.REFRESH_LOCK
            if lock.acquire(blocking=False):
                try:
                    func()
                    result = RefreshResult(result=True, error=None)
                except Exception as ex:
                    result = RefreshResult(result=False, error=ex)
                lock.release()
                return result
            else:
                return RefreshResult(result=False, error='Data is currently refreshed. Try again later.')
        else:
            try:
                func()
                return RefreshResult(result=True, error=None)
            except Exception as ex:
                return RefreshResult(result=False, error=ex)
    
    def __get_prev_refresh_time(self):
        return self.__last_refresh.time if self.__last_refresh else self.__prev_refresh_time

    def __update_refresh_time(self):
        now = int(round(time.time()))
        if self.__last_refresh:
            self.__last_refresh.time = now
            self.__last_refresh.save()
        else:
            self.__prev_refresh_time = now

    def refreshBans(self):
        def func():
            bans = self.__reader.getBans(self.__get_prev_refresh_time())
            self.__update_refresh_time()
            if bans and self.__savetodb:
                self.__database.saveBans(bans)
            self.logger.debug(str(bans))

        return self.__locked(func)

    def refreshLocations(self):
        def func():
            locations = self.__reader.getLocations()
            if locations and self.__savetodb:
                self.__database.saveLocations(locations)
            self.logger.debug(str(locations))

        return self.__locked(func)

    def refresh_all(self):
        self.refreshBans()
        self.refreshLocations()



class ArgsMock():
    """ Class mocking starting arguments.
    All parameters must be strings as described in stats.config and statsreader.py.
    """
    def __init__(self, config_path=None, database=False, interval=None, refresh_time=None):
        self.config = config_path
        self.database = database
        self.interval = interval
        self.time = refresh_time

def get_config_proxy():
    return dict({'interval':0, 'time':'', 'Fail2banHosts':''})
