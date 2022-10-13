import React from "react";
import { components, SingleValueProps as ReactSelectSingleValueProps } from "react-select";
import styled from "styled-components";

import { DropDownText } from "./DropDownText";
import { DropDownOptionDataItem } from "./Option";

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

export const SingleValue = React.memo(
  <T extends { data: { img: string } }>(props: React.PropsWithChildren<SingleValueProps<T>>) => {
    return (
      <SingleValueView>
        {props.data.img ? <SingleValueIcon>{props.data.img}</SingleValueIcon> : null}
        <DropDownText>
          <components.SingleValue {...props}>{props.children}</components.SingleValue>
        </DropDownText>
      </SingleValueView>
    );
  }
);
