# This script is still work in progress but development has been stopped because of shifting priorities
# Regenerate no_code_source using SourceRepository.fetch_no_code_sources
#no_code_source=("source-zoom" "source-tvmaze-schedule" "source-mailerlite" "source-gutendex" "source-news-api" "source-survey-sparrow" "source-pendo" "source-recruitee" "source-lokalise" "source-zapier-supported-storage" "source-coingecko-coins" "source-senseforce" "source-tmdb" "source-waiteraid" "source-omnisend" "source-punk-api" "source-oura" "source-apple-search-ads" "source-delighted" "source-postmarkapp" "source-intruder" "source-recreation" "source-smaily" "source-dremio" "source-sendinblue" "source-mailjet-mail" "source-coinmarketcap" "source-sap-fieldglass" "source-k6-cloud" "source-twilio-taskrouter" "source-courier" "source-fullstory" "source-gong" "source-woocommerce" "source-twitter" "source-merge" "source-convertkit" "source-workable" "source-callrail" "source-captain-data" "source-breezometer" "source-launchdarkly" "source-clickup-api" "source-chartmogul" "source-tyntec-sms" "source-yotpo" "source-aircall" "source-google-webfonts" "source-polygon-stock-api" "source-getlago" "source-configcat" "source-google-pagespeed-insights" "source-mailersend" "source-gainsight-px" "source-vantage" "source-workramp" "source-secoda" "source-pexels-api" "source-pypi" "source-ringcentral" "source-newsdata" "source-toggl" "source-emailoctopus" "source-wikipedia-pageviews" "source-activecampaign" "source-tempo" "source-spacex-api" "source-aha" "source-vitally" "source-mailjet-sms" "source-whisky-hunter" "source-gocardless" "source-datascope" "source-n8n" "source-reply-io" "source-ashby" "source-statuspage" "source-smartengage" "source-nytimes" "source-sonar-cloud" "source-metabase" "source-plausible" "source-rocket-chat" "source-coin-api" "source-ip2whois")
no_code_source=("source-zoom")

cd ../../../../..

for source_name in "${no_code_source[@]}"
do
  VERSION=dev ci_credentials $source_name write-to-storage
  cd airbyte-integrations/connectors/$source_name/
  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install -e '.[tests]' && pipacdk && deactivate
  source .venv/bin/activate
  python main.py read --config secrets/config.json >> before-change-spec-ouput.txt
  deactivate
  cd ../../..
done

source airbyte-cdk/python/.venv/bin/activate
python airbyte-cdk/python/airbyte_cdk/connector_builder/migrator/main.py --repository .
deactivate

for source_name in "${no_code_source[@]}"
do
  cd airbyte-integrations/connectors/$source_name/
  python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install -e '.[tests]' && pipacdk && deactivate
  source .venv/bin/activate
  python main.py read --config secrets/config.json >> after-change-spec-ouput.txt
  deactivate
  diff before-change-spec-ouput.txt after-change-spec-ouput.txt > diff.txt
  cd ../../..
done
