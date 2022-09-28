import React from "react";
import { components, SingleValueProps as ReactSelectSingleValueProps } from "react-select";
import styled from "styled-components";

import { DropDownOptionDataItem } from "./Option";
import Text from "./Text";

export type SingleValueProps<T> = {
  data?: DropDownOptionDataItem;
} & ReactSelectSingleValueProps<T>;

export const SingleValueView = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: left;
  align-items: center;
`;

export const SingleValueIcon = styled.div`
  margin-right: 6px;
  display: inline-block;
`;

const SingleValue = <T extends { data: { img: string } }>(props: React.PropsWithChildren<SingleValueProps<T>>) => {
  return (
    <SingleValueView>
      {props.data.img ? <SingleValueIcon>{props.data.img}</SingleValueIcon> : null}
      <Text>
        <components.SingleValue {...props}>{props.children}</components.SingleValue>
      </Text>
    </SingleValueView>
  );
};

export default React.memo(SingleValue);
