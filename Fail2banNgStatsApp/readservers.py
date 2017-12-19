import sys
import csv
import json
from rest_framework.views import APIView
from rest_framework.response import Response


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



class ServerListReader(APIView):
    def get(self, request, format=None):
        csv.register_dialect("Dial", delimiter='/')
        csvfile = open('ServerList.csv', 'r')
        jsonOut = {
            "dataset":[]
        }
        fieldnames = ("Number", "Address", "Port", "Bans")
        reader = csv.DictReader(csvfile, fieldnames, dialect="Dial")
        for row in reader:
            jsonOut["dataset"].append(row)
        #     print(row)
        # print(jsonOut["dataset"])
        return Response(jsonOut)



