#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import source_google_analytics_v4


class SourceGoogleAnalyticsV4ServiceAccountOnly(source_google_analytics_v4.SourceGoogleAnalyticsV4):
    """Updating of default source logic
    This connector shouldn't work with OAuth authentication method.
    The base logic of this connector is implemented in the "source-source_google_analytics_v4" connector.
    """
