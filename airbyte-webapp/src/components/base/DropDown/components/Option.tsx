import React from "react";
import styled from "styled-components";
import { components, OptionProps, OptionTypeBase } from "react-select";

import { naturalComparatorBy } from "utils/objects";
import Text from "./Text";

export type IProps = {
  data: { disabled: boolean; index: number; fullText?: boolean } & IDataItem;
} & OptionProps<OptionTypeBase, boolean>;

export type IDataItem = {
  label?: string;
  value?: any;
  groupValue?: string;
  groupValueText?: string;
  img?: React.ReactNode;
  primary?: boolean;
  secondary?: boolean;
  config?: any;
};

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

const Option: React.FC<IProps> = (props) => {
  return (
    <components.Option {...props}>
      <ItemView data-id={props.data.value}>
        <Text
          primary={props.data.primary}
          secondary={props.data.secondary}
          fullText={props.data.fullText}
        >
          {props.label}
        </Text>
        {props.data.img || null}
      </ItemView>
    </components.Option>
  );
};

export const defaultDataItemSort = naturalComparatorBy<IDataItem>(
  (dataItem) => dataItem.label || ""
);

export default Option;
