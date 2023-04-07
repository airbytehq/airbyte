import _ from "lodash";
import React from "react";

import { Separator } from "components/Separator";

import { ProcessedPackageMap, ProductItem, ProductOptionItem } from "core/domain/product";

import FeaturesCard from "./components/FeaturesCard";
import RangeCard from "./components/RangeCard";

interface IProps {
  product?: ProductOptionItem;
  setProduct: (item: ProductOptionItem) => void;
  selectedProduct?: ProductItem;
  paymentLoading: boolean;
  productOptions: ProductOptionItem[];
  packagesMap: ProcessedPackageMap;
  onSelectPlan: () => void;
}

const SelectPlanStep: React.FC<IProps> = ({
  product,
  setProduct,
  selectedProduct,
  paymentLoading,
  productOptions,
  packagesMap,
  onSelectPlan,
}) => {
  return (
    <>
      <RangeCard productOptions={productOptions} product={product} setProduct={setProduct} />
      <Separator height="30px" />
      <FeaturesCard
        product={product}
        selectPlanBtnDisability={_.isEqual(product?.id, selectedProduct?.id)}
        onSelectPlan={onSelectPlan}
        paymentLoading={paymentLoading}
        packagesMap={packagesMap}
      />
    </>
  );
};

export default SelectPlanStep;
