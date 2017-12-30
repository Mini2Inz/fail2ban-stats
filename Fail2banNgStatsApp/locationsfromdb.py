from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LocationTableData

import itertools


class LocationListReader(APIView):
    def get(self, request, format=None):
        allEntries = {
            "dateset": [{

            }]
        }
        for l in LocationTableData.objects.all():
            print(l.code)
            print(l.name)
            print(l.banscount)
            row = {
                "code": l.code,
                "name": l.name,
                "banscount": l.banscount
            }
            allEntries["dateset"].append(row)
        return Response(allEntries)
