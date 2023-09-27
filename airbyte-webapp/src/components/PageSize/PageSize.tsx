import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDown, DropDownRow } from "components";

interface IProps {
  totalPage: number;
  onChange: (size: number) => void;
  currentPageSize: number;
}

const Container = styled.div`
  display: flex;
  color: #6b7280;
  align-items: center;
  padding: 0 26px;
  font-weight: 500;
  line-height: 30px;
`;

const DropDownContainer = styled.div`
  width: 100px;
  margin-left: 8px;
`;

export const PageSize: React.FC<IProps> = ({ totalPage, onChange, currentPageSize }) => {
  const pageSizeOptons: DropDownRow.IDataItem[] = [
    {
      value: 10,
      label: "10",
    },
    {
      value: 20,
      label: "20",
    },
    {
      value: 50,
      label: "50",
    },
    {
      value: 100,
      label: "100",
    },
  ];

  if (totalPage <= 1) {
    return null;
  }

  return (
    <Container>
      <FormattedMessage id="table.page.size.label" />
      <DropDownContainer>
        <DropDown
          $withBorder
          $background="white"
          value={currentPageSize}
          options={pageSizeOptons}
          onChange={(option: DropDownRow.IDataItem) => onChange(option.value)}
        />
      </DropDownContainer>
    </Container>
  );
};
