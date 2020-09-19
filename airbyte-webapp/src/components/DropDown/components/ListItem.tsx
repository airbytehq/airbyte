import React from "react";
import styled from "styled-components";

import Text from "./Text";
import ImageBlock from "../../ImageBlock";

export type IProps = {
  item: IDataItem;
};

export type IDataItem = {
  text: string;
  value: string;
  img?: string;
};

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const ListItem: React.FC<IProps> = ({ item }) => {
  return (
    <ItemView>
      <Text>{item.text}</Text>
      {item.img ? <ImageBlock img={item.img} /> : null}
    </ItemView>
  );
};

export default ListItem;
