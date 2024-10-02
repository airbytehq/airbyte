ADVERTISERS_QUERY = "SELECT advertiser_homepage, affiliateId \
                    FROM `rewardstyle`.`Advertisers` \
                    WHERE SOURCE = 39 and active = 1 \
                    ORDER BY `name`;"
SHOPIFY_ACCESS_TOKEN_PATH = "prod/shopify/{0}/shopify_access_token"