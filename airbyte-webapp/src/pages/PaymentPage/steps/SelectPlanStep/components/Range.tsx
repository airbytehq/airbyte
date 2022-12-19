import React from "react";
import styled from "styled-components";

import { ProductItem } from "core/domain/product";

import RangeMark from "./RangeMark";

interface IRange {
  min?: number;
  max?: number;
}

interface IProps extends IRange {
  marks: ProductItem[];
  selectedMark?: ProductItem;
  onSelect: (item: ProductItem) => void;
}

const SliderContainer = styled.div<IRange>`
  width: ${({ min, max }) => (((max as number) - (min as number)) / ((max as number) - (min as number))) * 100}%;
  height: 10px;
  border-radius: 15px;
  background: #e4e8ef;
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
`;

const Slider: React.FC<IProps> = ({ min = 0, max = 100, marks, selectedMark, onSelect }) => {
  return (
    <SliderContainer min={min} max={max}>
      {marks.map((mark) => (
        <RangeMark label={mark.itemName} isActive={selectedMark?.id === mark.id} onSelect={() => onSelect(mark)} />
      ))}
    </SliderContainer>
  );
};

export default Slider;
