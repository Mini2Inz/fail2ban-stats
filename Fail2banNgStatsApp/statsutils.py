import csv
import asyncio
import itertools

class StatsReader():
    def __init__(self, config):
        self.hosts = []
        self.update_hosts(config)

    def get(self, request):
        responses = []
        async def _get(host):
            print('get {} from {}'.format(request, str(host)))
            try:
                reader, writer = await asyncio.open_connection(**host)
                connected = True
            except:
                print('Failed to connect ', str(host))
                connected = False
            
            if not connected: return

            print('connected ', str(host))
            msg = (request+'\n').encode()
            writer.write(msg)
            await writer.drain()
            print('sent ', request, str(host))
            firstbyte = await reader.read(1)
            if firstbyte == b'\n':
                print("No data from ", str(host))
                writer.close()
                return

            response = await reader.readuntil('\n\n'.encode())
            response = firstbyte.decode() + response.decode()
            # "filter bool" removes empty strings
            response = list(filter(bool, response.split('\n')))
            responses.append((host, response))
            print('from {}: {}'.format(str(host), str(response)))

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

    def update_hosts(self, config):
        def hoststr_to_dict(hoststr):
            print(hoststr)
            host = hoststr.split(':')
            return {'host':host[0], 'port':host[1]}
        self.hosts = list(map(hoststr_to_dict, config['Fail2banHosts'].split('\n')))


class RefreshContext():
    def __init__(self, statsreader, savetodb=False):
        self.__reader = statsreader
        self.__savetodb = savetodb
        if savetodb:
            from .djangodb import StatsDatabase
            self.__database = StatsDatabase()

    def refreshBans(self):
        bans = self.__reader.getBans()
        if bans and self.__savetodb:
            self.__database.saveBans(bans)
        print(bans)

    def refreshLocations(self):
        locations = self.__reader.getLocations()
        if locations and self.__savetodb:
            self.__database.saveLocations(locations)
        print(locations)

    def refresh_all(self):
        self.refreshBans()
        self.refreshLocations()
