import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

// import { Card } from "components";

import { ProductItem } from "core/domain/product";
import { NumberNaming } from "core/functions/numberFormatter";

import Range from "./Range";

interface IProps {
  products: ProductItem[];
  product?: ProductItem;
  setProduct: (item: ProductItem) => void;
}

const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  user-select: none;
`;

const RangeContainer = styled.div`
  padding: 60px;
`;

const CardContainer = styled.div`
  padding: 20px 20px;
  background: #ffffff;
  border-radius: 16px;
`;

const NoteContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: 400;
  font-size: 12px;
  line-height: 30px;
  color: #999999;
`;

const RangeCard: React.FC<IProps> = ({ products, product, setProduct }) => {
  return (
    // <Card withPadding roundedBottom>
    <CardContainer>
      <Title>
        <FormattedMessage id="plan.rows.card.title" />
      </Title>
      <RangeContainer>
        <Range min={0} max={110 * NumberNaming.M} marks={products} selectedMark={product} onSelect={setProduct} />
      </RangeContainer>
      <NoteContainer>
        <FormattedMessage id="plan.rows.card.note" />
      </NoteContainer>
    </CardContainer>
    // </Card>
  );
};

export default RangeCard;
