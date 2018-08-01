import sys
import csv
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from Fail2banNgStatsApp.models import BansTableData
from rest_framework import generics

from .statsreader import read_config
from .statsutils import StatsReader
from .serializers import BansTableDataSerializer

# class ServerListReader(APIView):
#
#     def get(self, request, format=None):
#         ServerList = genfromtxt('ServerList.csv', delimiter='/', dtype=None)
#         numberList = ServerList[:, 1]
#         addressList = ServerList[:, 2]
#         portList = ServerList[:, 3]
#         sys.stdout.write(numberList)
#         sys.stdout.flush()
#         data = {
#             "numberList": numberList,
#             "addressList": addressList,
#             "portList": portList
#         }
#         return Response(data)


# ServerListReader
class ServerListReader(generics.ListAPIView):
    serializer_class = BansTableDataSerializer
    def get_queryset(self):
        jsonOut = {
            "dataset": []
        }
        config = read_config('stats.config')
        reader = StatsReader(config)
        hosts = reader.hosts
        for host in hosts:
            host["bans"] = BansTableData.objects.filter(recived_from_address=host['host'],
                                                        recived_from_port=host['port']).count()
            jsonOut["dataset"].append(host)

        jsonOut["dataset"] = sorted(jsonOut["dataset"], key=lambda k: k['bans'], reverse=True)
        return Response(jsonOut)
