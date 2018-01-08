import csv
import asyncio
import itertools

class StatsReader():
    def __init__(self, config):
        self.hosts = []
        self.getFail2banHosts(config)

    def get(self, request):
        responses = []
        async def _get(host):
            print('get {} from {}'.format(request, str(host)))
            try:
                reader, writer = await asyncio.open_connection(**host)
            except:
                print('Failed to connect ', str(host))
            else:
                print('connected ', str(host))
                msg = (request+'\n').encode()
                writer.write(msg)
                await writer.drain()
                print('sent ', request, str(host))
                response = await reader.readuntil('\n\n'.encode())
                # "filter bool" removes empty strings
                response = list(filter(bool, response.decode().split('\n')))
                responses.append((host, response))
                print('from {}: {}'.format(str(host), str(response)))
                writer.close()
                
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = []
        for host in self.hosts:
            tasks.append(asyncio.ensure_future(_get(host)))
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

        return responses

    def getBans(self):
        return self.get('BANS')

    def getLocations(self):
        return self.get('LOCATIONS')

    def getFail2banHosts(self, config):
        def hoststr_to_dict(hoststr):
            print(hoststr)
            host = hoststr.split(':')
            return {'host':host[0], 'port':host[1]}
        self.hosts = list(map(hoststr_to_dict, config['Fail2banHosts'].split('\n')))


class RefreshContext():
    def __init__(self, statsreader, savetodb=False):
        self._reader = statsreader
        self._savetodb = savetodb
        if savetodb:
            from .djangodb import StatsDatabase
            self._database = StatsDatabase()

    def refresh(self):
        bans = self._reader.getBans()
        if self._savetodb:
            self._database.saveBans(bans)
        # todo log in debug
        print(bans)
