import React from "react";
import styled from "styled-components";
import { components, SingleValueProps, OptionTypeBase } from "react-select";

import { IDataItem } from "./Option";
import Text from "./Text";

export type IProps = {
  data?: IDataItem;
} & SingleValueProps<OptionTypeBase>;

const ItemView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: left;
  align-items: center;
`;

const Icon = styled.div`
  margin-right: 6px;
  display: inline-block;
`;

const SingleValue: React.FC<IProps> = (props) => {
  return (
    <ItemView>
      {props.data.img ? <Icon>{props.data.img}</Icon> : null}
      <Text>
        <components.SingleValue {...props}>
          {props.children}
        </components.SingleValue>
      </Text>
    </ItemView>
  );
};

export default React.memo(SingleValue);
