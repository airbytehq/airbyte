#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_exact.streams import (
    CRMAccountClassificationNames,
    CRMAccountClassifications,
    SyncCashflowPaymentTerms,
    SyncCRMAccounts,
    SyncCRMAddresses,
    SyncCRMContacts,
    SyncCRMQuotationHeaders,
    SyncCRMQuotationLines,
    SyncCRMQuotations,
    SyncDeleted,
    SyncDocumentsDocumentAttachments,
    SyncDocumentsDocuments,
    SyncFinancialGLAccounts,
    SyncFinancialGLClassifications,
    SyncFinancialTransactionLines,
    SyncHRMLeaveAbsenceHoursByDay,
    SyncInventoryItemWarehouses,
    SyncInventorySerialBatchNumbers,
    SyncInventoryStockPositions,
    SyncInventoryStockSerialBatchNumbers,
    SyncInventoryStorageLocationStockPositions,
    SyncLogisticsItems,
    SyncLogisticsPurchaseItemPrices,
    SyncLogisticsSalesItemPrices,
    SyncLogisticsSupplierItem,
    SyncProjectProjectPlanning,
    SyncProjectProjects,
    SyncProjectProjectWBS,
    SyncProjectTimeCostTransactions,
    SyncPurchaseOrderPurchaseOrders,
    SyncSalesInvoiceSalesInvoices,
    SyncSalesOrderGoodsDeliveries,
    SyncSalesOrderGoodsDeliveryLines,
    SyncSalesOrderSalesOrderHeaders,
    SyncSalesOrderSalesOrderLines,
    SyncSalesOrderSalesOrders,
    SyncSalesSalesPriceListVolumeDiscounts,
    SyncSubscriptionSubscriptionLines,
    SyncSubscriptionSubscriptions,
)


# Source
class SourceExact(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        access_token = (config or {}).get("credentials", {}).get("access_token")
        refresh_token = (config or {}).get("credentials", {}).get("refresh_token")
        divisions = (config or {}).get("divisions", [])

        if not access_token or not refresh_token:
            return False, "Missing access or refresh token"
        if not divisions:
            return False, "Missing divisions"

        # TODO: check with airbyte whether control messages are handled during connection check (for token refresh)
        # try:
        #     headers = {
        #         "Authorization": f"Bearer {access_token}",
        #         "Accept": "application/json",
        #     }

        #     response = requests.get(
        #         "https://start.exactonline.nl/api/v1/current/Me",
        #         headers=headers,
        #         timeout=15,
        #     )

        #     response.raise_for_status()
        #     logger.info(f"Connection check successful. Details:\n{json.dumps(response.json())}")
        # except requests.RequestException as exc:
        #     return (
        #         False,
        #         f"Exception happened during connection check. Validate that the access_token is still valid at this point. Details\n{exc}",
        #     )

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            SyncCashflowPaymentTerms(config),
            SyncCRMAccounts(config),
            SyncCRMAddresses(config),
            SyncCRMContacts(config),
            SyncCRMQuotationHeaders(config),
            SyncCRMQuotationLines(config),
            SyncCRMQuotations(config),
            SyncDeleted(config),
            SyncDocumentsDocumentAttachments(config),
            SyncDocumentsDocuments(config),
            SyncFinancialGLAccounts(config),
            SyncFinancialGLClassifications(config),
            SyncFinancialTransactionLines(config),
            SyncHRMLeaveAbsenceHoursByDay(config),
            SyncInventoryItemWarehouses(config),
            SyncInventorySerialBatchNumbers(config),
            SyncInventoryStockPositions(config),
            SyncInventoryStockSerialBatchNumbers(config),
            SyncInventoryStorageLocationStockPositions(config),
            SyncLogisticsItems(config),
            SyncLogisticsPurchaseItemPrices(config),
            SyncLogisticsSalesItemPrices(config),
            SyncLogisticsSupplierItem(config),
            SyncProjectProjectPlanning(config),
            SyncProjectProjects(config),
            SyncProjectProjectWBS(config),
            SyncProjectTimeCostTransactions(config),
            SyncPurchaseOrderPurchaseOrders(config),
            SyncSalesSalesPriceListVolumeDiscounts(config),
            SyncSalesInvoiceSalesInvoices(config),
            SyncSalesOrderGoodsDeliveries(config),
            SyncSalesOrderGoodsDeliveryLines(config),
            SyncSalesOrderSalesOrderHeaders(config),
            SyncSalesOrderSalesOrderLines(config),
            SyncSalesOrderSalesOrders(config),
            SyncSubscriptionSubscriptionLines(config),
            SyncSubscriptionSubscriptions(config),
            CRMAccountClassifications(config),
            CRMAccountClassificationNames(config),
        ]
