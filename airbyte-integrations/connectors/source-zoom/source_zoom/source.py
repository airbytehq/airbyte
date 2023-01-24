#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceZoom(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})





x=["airbyte-integrations/connectors/source-activecampaign/source_activecampaign/source.py",
"airbyte-integrations/connectors/source-aha/source_aha/source.py",
"airbyte-integrations/connectors/source-alpha-vantage/source_alpha_vantage/source.py",
"airbyte-integrations/connectors/source-ashby/source_ashby/source.py",
"airbyte-integrations/connectors/source-braze/source_braze/source.py",
"airbyte-integrations/connectors/source-breezometer/source_breezometer/source.py",
"airbyte-integrations/connectors/source-callrail/source_callrail/source.py",
"airbyte-integrations/connectors/source-chartmogul/source_chartmogul/source.py",
"airbyte-integrations/connectors/source-clickup-api/source_clickup_api/source.py",
"airbyte-integrations/connectors/source-close-com/source_close_com/source_lc.py",
"airbyte-integrations/connectors/source-coin-api/source_coin_api/source.py",
"airbyte-integrations/connectors/source-coingecko-coins/source_coingecko_coins/source.py",
"airbyte-integrations/connectors/source-coinmarketcap/source_coinmarketcap/source.py",
"airbyte-integrations/connectors/source-configcat/source_configcat/source.py",
"airbyte-integrations/connectors/source-convertkit/source_convertkit/source.py",
"airbyte-integrations/connectors/source-courier/source_courier/source.py",
"airbyte-integrations/connectors/source-datascope/source_datascope/source.py",
"airbyte-integrations/connectors/source-dremio/source_dremio/source.py",
"airbyte-integrations/connectors/source-emailoctopus/source_emailoctopus/source.py",
"airbyte-integrations/connectors/source-facebook-pages/source_facebook_pages/source.py",
"airbyte-integrations/connectors/source-getlago/source_getlago/source.py",
"airbyte-integrations/connectors/source-gnews/source_gnews/source.py",
"airbyte-integrations/connectors/source-gocardless/source_gocardless/source.py",
"airbyte-integrations/connectors/source-gong/source_gong/source.py",
"airbyte-integrations/connectors/source-google-pagespeed-insights/source_google_pagespeed_insights/source.py",
"airbyte-integrations/connectors/source-google-webfonts/source_google_webfonts/source.py",
"airbyte-integrations/connectors/source-greenhouse/source_greenhouse/source.py",
"airbyte-integrations/connectors/source-gutendex/source_gutendex/source.py",
"airbyte-integrations/connectors/source-instatus/source_instatus/source.py",
"airbyte-integrations/connectors/source-intruder/source_intruder/source.py",
"airbyte-integrations/connectors/source-ip2whois/source_ip2whois/source.py",
"airbyte-integrations/connectors/source-k6-cloud/source_k6_cloud/source.py",
"airbyte-integrations/connectors/source-launchdarkly/source_launchdarkly/source.py",
"airbyte-integrations/connectors/source-lokalise/source_lokalise/source.py",
"airbyte-integrations/connectors/source-mailerlite/source_mailerlite/source.py",
"airbyte-integrations/connectors/source-mailersend/source_mailersend/source.py",
"airbyte-integrations/connectors/source-mailjet-mail/source_mailjet_mail/source.py",
"airbyte-integrations/connectors/source-mailjet-sms/source_mailjet_sms/source.py",
"airbyte-integrations/connectors/source-metabase/source_metabase/source.py",
"airbyte-integrations/connectors/source-monday/source_monday/source.py",
"airbyte-integrations/connectors/source-n8n/source_n8n/source.py",
"airbyte-integrations/connectors/source-news-api/source_news_api/source.py",
"airbyte-integrations/connectors/source-newsdata/source_newsdata/source.py",
"airbyte-integrations/connectors/source-nytimes/source_nytimes/source.py",
"airbyte-integrations/connectors/source-omnisend/source_omnisend/source.py",
"airbyte-integrations/connectors/source-oura/source_oura/source.py",
"airbyte-integrations/connectors/source-partnerstack/source_partnerstack/source.py",
"airbyte-integrations/connectors/source-pexels-api/source_pexels_api/source.py",
"airbyte-integrations/connectors/source-plausible/source_plausible/source.py",
"airbyte-integrations/connectors/source-pocket/source_pocket/source.py",
"airbyte-integrations/connectors/source-polygon-stock-api/source_polygon_stock_api/source.py",
"airbyte-integrations/connectors/source-posthog/source_posthog/source.py",
"airbyte-integrations/connectors/source-postmarkapp/source_postmarkapp/source.py",
"airbyte-integrations/connectors/source-prestashop/source_prestashop/source.py",
"airbyte-integrations/connectors/source-punk-api/source_punk_api/source.py",
"airbyte-integrations/connectors/source-pypi/source_pypi/source.py",
"airbyte-integrations/connectors/source-recreation/source_recreation/source.py",
"airbyte-integrations/connectors/source-recruitee/source_recruitee/source.py",
"airbyte-integrations/connectors/source-reply-io/source_reply_io/source.py",
"airbyte-integrations/connectors/source-rocket-chat/source_rocket_chat/source.py",
"airbyte-integrations/connectors/source-sap-fieldglass/source_sap_fieldglass/source.py",
"airbyte-integrations/connectors/source-secoda/source_secoda/source.py",
"airbyte-integrations/connectors/source-sendinblue/source_sendinblue/source.py",
"airbyte-integrations/connectors/source-senseforce/source_senseforce/source.py",
"airbyte-integrations/connectors/source-smaily/source_smaily/source.py",
"airbyte-integrations/connectors/source-smartengage/source_smartengage/source.py",
"airbyte-integrations/connectors/source-sonar-cloud/source_sonar_cloud/source.py",
"airbyte-integrations/connectors/source-spacex-api/source_spacex_api/source.py",
"airbyte-integrations/connectors/source-square/source_square/source.py",
"airbyte-integrations/connectors/source-statuspage/source_statuspage/source.py",
"airbyte-integrations/connectors/source-survey-sparrow/source_survey_sparrow/source.py",
"airbyte-integrations/connectors/source-the-guardian-api/source_the_guardian_api/source.py",
"airbyte-integrations/connectors/source-tmdb/source_tmdb/source.py",
"airbyte-integrations/connectors/source-toggl/source_toggl/source.py",
"airbyte-integrations/connectors/source-tvmaze-schedule/source_tvmaze_schedule/source.py",
"airbyte-integrations/connectors/source-twilio-taskrouter/source_twilio_taskrouter/source.py",
"airbyte-integrations/connectors/source-twitter/source_twitter/source.py",
"airbyte-integrations/connectors/source-tyntec-sms/source_tyntec_sms/source.py",
"airbyte-integrations/connectors/source-vantage/source_vantage/source.py",
"airbyte-integrations/connectors/source-vitally/source_vitally/source.py",
"airbyte-integrations/connectors/source-waiteraid/source_waiteraid/source.py",
"airbyte-integrations/connectors/source-whisky-hunter/source_whisky_hunter/source.py",
"airbyte-integrations/connectors/source-wikipedia-pageviews/source_wikipedia_pageviews/source.py",
"airbyte-integrations/connectors/source-woocommerce/source_woocommerce/source.py",
"airbyte-integrations/connectors/source-workable/source_workable/source.py",
"airbyte-integrations/connectors/source-workramp/source_workramp/source.py",
"airbyte-integrations/connectors/source-zapier-supported-storage/source_zapier_supported_storage/source.py",
"airbyte-integrations/connectors/source-zoom/source_zoom/source.py"]

for e in x: 
    y=e.split('/')[:-1]
    old_name = "/".join(y + [f"{y[-1]}.yaml".replace("source_", "")])
    new_name = "/".join(y + ["manifest.yaml"])
    # print(old_name, new_name)
    os.rename(old_name, new_name)
    # print(first)
    # print(os.listdir("/".join(y)))