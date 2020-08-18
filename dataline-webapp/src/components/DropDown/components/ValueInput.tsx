import React from "react";
import styled from "styled-components";

import { IDataItem } from "./ListItem";
import Text from "./Text";
import ImageBlock from "../../ImageBlock";

export type IProps = {
  item: IDataItem;
};

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: left;
  align-items: center;
`;

const PaddedText = styled(Text)`
  padding-left: 6px;
`;

const ValueInput: React.FC<IProps> = ({ item }) => {
  return (
    <ItemView>
      {item.img ? <ImageBlock img={item.img} /> : null}
      <PaddedText>{item.text}</PaddedText>
    </ItemView>
  );
};

export default ValueInput;
