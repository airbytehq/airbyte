from typing import Optional, List

from pydantic import BaseModel


class GetStocksWarehouseStock(BaseModel):
    sku: str
    amount: int


class GetStocksWarehouseStockResponse(BaseModel):
    stocks: Optional[List[GetStocksWarehouseStock]]


class GetStocksWarehouseStockErrorResponse(BaseModel):
    code: str
    message: str
    data: Optional[dict]
