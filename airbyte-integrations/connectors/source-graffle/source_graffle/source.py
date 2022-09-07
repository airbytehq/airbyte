import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_events import (
    MintedEvents,
    PurchasedEvents,
    FullfilledEvents,
    FullfilledErrorEvents,
    RequeuedEvents,
    OpenedEvents,
    PackRevealEvents,
    DepositEvents,
    WithdrawEvents,
    SaleEvents,
    RoyaltyEvents
)

class SourceGraffle(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, str]:
        test_transaction_id = "7c6296030687a4b1af157b3d2369e8bcd7750c645c2648e7f1a933cc76e78272"
        url_param = f"api/company/{config['company_id']}/search?transactionId={test_transaction_id}"
        url = f"https://prod-main-net-dashboard-api.azurewebsites.net/{url_param}"
        response = requests.get(url)
        try:
            _ = response.json()
            return True, "accepted"
        except:
            return False, "error"


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            MintedEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Minted"),
            PurchasedEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Purchased"),
            FullfilledEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Fulfilled"),
            FullfilledErrorEvents(config, "A.30cf5dcf6ea8d379.AeraPack.FulfilledError"),
            RequeuedEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Requeued"),
            OpenedEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Opened"),
            PackRevealEvents(config, "A.30cf5dcf6ea8d379.AeraPack.PackReveal"),
            DepositEvents(config, "A.30cf5dcf6ea8d379.AeraNFT.Deposit"),
            WithdrawEvents(config, "A.30cf5dcf6ea8d379.AeraNFT.Withdraw"),
            SaleEvents(config, "A.097bafa4e0b48eef.FindMarketSale.Sale"),
            RoyaltyEvents(config, "A.097bafa4e0b48eef.FindMarket.RoyaltyPaid")
        ]
