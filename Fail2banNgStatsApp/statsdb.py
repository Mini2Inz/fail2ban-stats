from datetime import datetime, date
from .statsutils import get_logger

def int_try_parse(string, default = 0):
    try:
        return int(string)
    except ValueError:
        return default

def try_get(list, idx, length = -1, default = None):
    length = len(list) if length == -1 else length
    return list[idx] if idx < length else default

class StatsDatabase():
    def __init__(self):
        self.logger = get_logger(__name__)

    @staticmethod
    def initDjango():
        import django
        import os
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            "Fail2banNgStats.settings"
            )
        django.setup()

    def __save(self, data, data_handler):
        for data_tuple in data:
            host, data_list = data_tuple
            for data_item in data_list:
                parsed_data = data_item.split(',')
                datalen = len(parsed_data)
                if datalen < 2:
                    self.logger.warning('Not enough data: {}'.format(str(data_item)))
                data_handler(host, parsed_data, datalen)

    def saveBans(self, bans):
        from .models import BansTableData
        def saveBan(host, ban_data, datalen):
            ban = BansTableData()
            ban.jail = ban_data[0]
            ban.ip = ban_data[1]
            if datalen > 2: 
                ban.timeofban = int_try_parse(ban_data[2])
            if datalen > 3:
                ban.bantime = int_try_parse(ban_data[3])
            ban.recived_from_address = host['host']
            ban.recived_from_port = host['port']
            ban.timeOfArrival = datetime.now()
            ban.save()

        self.__save(bans, saveBan)


    def saveLocations(self, locationsData):
        from .models import LocationTableData
        
        today = date.today()
        today = datetime(today.year, today.month, today.day)

        LocationTableData.objects.filter(dateTime=today).delete()

        def saveLoc(host, loc_data, datalen):
            loc = LocationTableData.objects \
                .filter(code=loc_data[0], dateTime=today) \
                .first()
            if loc is None:
                loc = LocationTableData()
                loc.code = loc_data[0]
                loc.name = loc_data[1]
                loc.dateTime = today
                loc.dayOfTheWeek = today.weekday()
                loc.banscount = 0

            if datalen >= 3:
                loc.banscount += int(loc_data[2])
            loc.save()

        self.__save(locationsData, saveLoc)

