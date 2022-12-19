export interface ProductItem {
  id: string;
  itemName: string;
  price: number;
}

export interface ProductItemsList {
  data: ProductItem[];
}
