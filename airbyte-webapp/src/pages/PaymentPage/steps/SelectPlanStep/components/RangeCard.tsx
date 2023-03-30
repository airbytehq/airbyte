import Slider from "@mui/material/Slider";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ProductOptionItem } from "core/domain/product";

interface IProps {
  productOptions: ProductOptionItem[];
  product?: ProductOptionItem;
  setProduct: (item: ProductOptionItem) => void;
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

const RangeCard: React.FC<IProps> = ({ productOptions, product, setProduct }) => {
  const valueLabelFormat = (value: any) => {
    return productOptions.findIndex((option) => option.value === value) + 1;
  };

  const getSinglePrice = (event: any) => {
    const matchingOptions = productOptions.filter((option) => {
      return option.value === event.target.value;
    });
    setProduct(matchingOptions[0]);
  };

  return (
    <CardContainer>
      <Title>
        <FormattedMessage id="plan.rows.card.title" />
      </Title>
      <RangeContainer>
        <Slider
          aria-label="Restricted values"
          valueLabelFormat={(value) => valueLabelFormat(value)}
          value={typeof Number(product?.value) === "number" ? Number(product?.value) : 100}
          step={null}
          valueLabelDisplay="off"
          marks={productOptions}
          onChange={getSinglePrice}
          sx={{
            height: 18,
            color: "#fff",
            padding: "13px 0 0 0",
            "& .MuiSlider-track": {
              background: "#E4E8EF",
              opacity: 1,
            },
            "& .MuiSlider-thumb": {
              height: 22,
              width: 22,
              borderRadius: "50%",
              color: "#4F46E5",
            },
            "& .MuiSlider-thumb::before": {
              boxShadow: "none",
            },
            "& .MuiSlider-thumb::after": {
              width: 10,
              height: 10,
              background: "#fff",
            },
            "& .MuiSlider-thumb:hover": {
              boxShadow: "none",
            },
            "& .MuiSlider-thumb.Mui-focusVisible": {
              boxShadow: "none",
            },
            "& .MuiSlider-thumb.Mui-selected": {
              boxShadow: "none",
            },
            "& .MuiSlider-thumb.Mui-active": {
              boxShadow: "none",
            },
            "& .MuiSlider-mark": {
              width: 10,
              height: 10,
              borderRadius: "50%",
              opacity: 1,
            },
            "& .MuiSlider-rail": {
              background: "#E4E8EF",
              opacity: 1,
            },
            "& .MuiSlider-markLabel": {
              transform: "translateX(-40%)",
            },
          }}
        />
      </RangeContainer>
      <NoteContainer>
        <FormattedMessage id="plan.rows.card.note" />
      </NoteContainer>
    </CardContainer>
  );
};

export default RangeCard;
