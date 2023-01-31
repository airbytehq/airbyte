#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys
from destination_yandex_metrica_offline_conv import DestinationYandexMetricaOfflineConv


if __name__ == "__main__":
    DestinationYandexMetricaOfflineConv().run(sys.argv[1:])
