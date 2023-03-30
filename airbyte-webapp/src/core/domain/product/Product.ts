export interface ProductItem {
  id: string;
  itemName: string;
  price: number;
}

export interface ProductItemsList {
  data: ProductItem[];
}

export interface ProductOptionItem {
  id?: string;
  itemName?: string;
  value: number;
  label?: string;
  price: string;
}
