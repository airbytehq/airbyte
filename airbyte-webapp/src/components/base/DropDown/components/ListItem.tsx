import React from "react";
import styled from "styled-components";

import Text from "./Text";

export type IProps = {
  disabled: boolean;
  index: number;
  fullText?: boolean;
} & IDataItem;

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

const ListItem: React.FC<IProps> = ({
  value,
  primary,
  secondary,
  text,
  img,
  fullText,
}) => {
  return (
    <ItemView data-id={value}>
      <Text primary={primary} secondary={secondary} fullText={fullText}>
        {text}
      </Text>
      {img || null}
    </ItemView>
  );
};

export const defaultDataItemSort = (a: IDataItem, b: IDataItem): number => {
  if (a.text < b.text) return -1;
  if (a.text > b.text) return 1;
  return 0;
};

export default ListItem;
