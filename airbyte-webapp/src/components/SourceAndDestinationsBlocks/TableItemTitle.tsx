import React from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";

import { H5, DropDown } from "../../components";
import { IDataItem } from "../DropDown/components/ListItem";

type IProps = {
  type: "source" | "destination";
  dropDownData: IDataItem[];
  onSelect: (item: IDataItem) => void;
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px 18px 27px;
`;

const TableItemTitle: React.FC<IProps> = ({ type, dropDownData, onSelect }) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <Content>
      <H5>
        <FormattedMessage id={`tables.${type}s`} />
      </H5>
      <DropDown
        onSelect={onSelect}
        data={[
          {
            text: formatMessage({
              id: `tables.${type}AddNew`
            }),
            value: "create-new-item",
            primary: true
          },
          ...dropDownData
        ]}
        hasFilter
        withButton
        textButton={formatMessage({
          id: `tables.${type}Add`
        })}
      />
    </Content>
  );
};

export default TableItemTitle;
