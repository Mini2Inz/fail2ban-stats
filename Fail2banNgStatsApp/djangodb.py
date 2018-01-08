def int_try_parse(string, default = 0):
    try:
        return int(string)
    except ValueError:
        return default

def try_get(list, idx, length = -1, default = None):
    length = len(list) if length == -1 else length
    return list[idx] if idx < length else default

class StatsDatabase():
    
    @staticmethod
    def initDjango():
        import django
        import os
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            "Fail2banNgStats.settings"
            )
        django.setup()

    def saveBans(self, bans):
        from .models import BansTableData
        for bantuple in bans:
            host, banslist = bantuple
            for rawban in banslist:
                ban_data = rawban.split(',')
                datalen = len(ban_data)
                if datalen < 2: 
                    # todo log
                    continue

                ban = BansTableData()
                ban.jail = ban_data[0]
                ban.ip = ban_data[1]
                if datalen > 2: 
                    ban.timeofban = int_try_parse(ban_data[2])
                if datalen > 3:
                    ban.bantime = int_try_parse(ban_data[3])
                ban.recived_from_address = host['host']
                ban.recived_from_port = host['port']
                ban.save()

    def saveLocations(self, locations):
        pass