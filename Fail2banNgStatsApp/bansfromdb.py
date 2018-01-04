from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BansTableData

import itertools


class BansListReader(APIView):
    def get(self, request, format=None):
        allEntries = {
            "dateset": [{

            }]
        }
        for b in BansTableData.objects.all():
            print(b.jail)
            print(b.ip)
            print(b.bantime)
            print(b.timeofban)
            row = {
                "jail": b.jail,
                "ip": b.ip,
                "bantime": b.bantime,
                "timeofban": b.timeofban
            }
            allEntries["dateset"].append(row)
        return Response(allEntries)
