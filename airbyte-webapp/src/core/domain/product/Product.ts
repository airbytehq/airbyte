export interface Product {
  id: string;
  itemName: string;
  price: number;
}

export interface ProductList {
  products: Product[];
}
