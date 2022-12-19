import _ from "lodash";
import React from "react";
import styled from "styled-components";

import { ProcessedPackageMap, ProductItem } from "core/domain/product";

import FeaturesCard from "./components/FeaturesCard";
import RangeCard from "./components/RangeCard";

interface IProps {
  product?: ProductItem;
  setProduct: (item: ProductItem) => void;
  selectedProduct?: ProductItem;
  paymentLoading: boolean;
  productItems: ProductItem[];
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
  productItems,
  packagesMap,
  onSelectPlan,
}) => {
  return (
    <>
      <RangeCard products={productItems} product={product} setProduct={setProduct} />
      <CardSeperator />
      <FeaturesCard
        product={product}
        selectPlanBtnDisability={_.isEqual(product, selectedProduct)}
        onSelectPlan={onSelectPlan}
        paymentLoading={paymentLoading}
        packagesMap={packagesMap}
      />
    </>
  );
};

export default SelectPlanStep;
