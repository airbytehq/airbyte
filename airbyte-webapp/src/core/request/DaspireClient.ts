import { ProductList } from "../domain/product";
import { apiOverride } from "./apiOverride";

type SecondParameter<T extends (...args: any) => any> = T extends (config: any, args: infer P) => any ? P : never;

/**
 * @summary List all products registered in the current Daspire deployment
 */
export const listProducts = (options?: SecondParameter<typeof apiOverride>) => {
  return apiOverride<ProductList>({ url: `/product/item/rows`, method: "get" }, options);
};
