import React from "react";
import styled from "styled-components";

import Text from "./Text";

export type IProps = {
  item: {
    disabled: boolean;
    index: number;
    item: IDataItem;
  } & IDataItem;
  fullText?: boolean;
};

export type IDataItem = {
  text: string;
  value: string;
  groupValue?: string;
  groupValueText?: string;
  img?: React.ReactNode;
  primary?: boolean;
  secondary?: boolean;
};

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const ListItem: React.FC<IProps> = ({ item, fullText }) => {
  return (
    <ItemView data-id={item.value}>
      <Text
        primary={item.primary}
        secondary={item.secondary}
        fullText={fullText}
      >
        {item.text}
      </Text>
      {item.item.img || null}
    </ItemView>
  );
};

export const defaultDataItemSort = (a: IDataItem, b: IDataItem): number => {
  if (a.text < b.text) return -1;
  if (a.text > b.text) return 1;
  return 0;
};

export default ListItem;
