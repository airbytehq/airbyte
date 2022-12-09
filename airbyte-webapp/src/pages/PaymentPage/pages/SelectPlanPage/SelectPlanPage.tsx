import React, { useState } from "react";
import styled from "styled-components";

import { NumberNaming } from "core/functions/numberFormatter";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useListProducts } from "services/products/ProductsService";

import { PaymentRoute } from "../../PaymentPage";
import FeaturesCard from "./components/FeaturesCard";
import { IDataRow } from "./components/Range";
import RangeCard from "./components/RangeCard";

const CardSeperator = styled.div`
  width: 100%;
  height: 30px;
`;

const SelectPlanPage: React.FC = () => {
  const { push } = useRouter();

  const [selectedDataRow, setDataRow] = useState<IDataRow | undefined>();

  const products = useListProducts();

  console.log(products);

  const dataRows: IDataRow[] = [
    { id: "1", numberOfRows: 1 * NumberNaming.M },
    { id: "2", numberOfRows: 2 * NumberNaming.M },
    { id: "3", numberOfRows: 3 * NumberNaming.M },
    { id: "4", numberOfRows: 5 * NumberNaming.M },
    { id: "5", numberOfRows: 10 * NumberNaming.M },
    { id: "6", numberOfRows: 20 * NumberNaming.M },
    { id: "7", numberOfRows: 50 * NumberNaming.M },
    { id: "8", numberOfRows: 100 * NumberNaming.M },
  ];

  const onSelectPlan = () => {
    push(`/${RoutePaths.Payment}/${PaymentRoute.BillingPayment}`);
  };

  return (
    <>
      <RangeCard dataRows={dataRows} selectedDataRow={selectedDataRow} setDataRow={setDataRow} />
      <CardSeperator />
      <FeaturesCard onSelectPlan={onSelectPlan} />
    </>
  );
};

export default SelectPlanPage;
