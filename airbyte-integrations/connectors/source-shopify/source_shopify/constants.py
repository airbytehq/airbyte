ADVERTISERS_QUERY = "SELECT advertiser_homepage, affiliateId \
                    FROM `rewardstyle`.`Advertisers` \
                    WHERE SOURCE = 39 and active = 1 \
                    ORDER BY `name`;"
SHOPIFY_ACCESS_TOKEN_PATH = "arn:aws:secretsmanager:us-east-1:282492028148:secret:{0}/shopify/{1}/shopify_access_token"