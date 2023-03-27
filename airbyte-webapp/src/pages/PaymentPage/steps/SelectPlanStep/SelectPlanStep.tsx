import _ from "lodash";
import React from "react";
import styled from "styled-components";

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

const CardSeperator = styled.div`
  width: 100%;
  height: 30px;
`;

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
      <CardSeperator />
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
