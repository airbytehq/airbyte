export interface ProductItem {
  id: string;
  itemName: string;
  price: number;
  cloudProviderName?: string;
  instanceSizeName?: string;
  region?: string;
  regionItemId?: string;
  instanceItemId?: string;
  cloudItemId?: string;
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
