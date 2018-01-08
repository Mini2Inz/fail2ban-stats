from Fail2banNgStatsApp.djangodb import StatsDatabase
from Fail2banNgStatsApp.statsreader import main

StatsDatabase.initDjango()
main()
