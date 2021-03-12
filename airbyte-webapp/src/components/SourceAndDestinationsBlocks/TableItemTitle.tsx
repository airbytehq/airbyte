import React from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";

import { H3, H5 } from "components/Titles";
import { DropDown } from "components/DropDown";
import { IDataItem } from "components/DropDown/components/ListItem";

type IProps = {
  type: "source" | "destination";
  dropDownData: IDataItem[];
  onSelect: (item: IDataItem) => void;
  entity: string;
  entityName: string;
  entityIcon?: string;
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px 18px 27px;
`;

const EntityType = styled(H5)`
  color: ${({ theme }) => theme.greyColor55};
`;

const EntityInfo = styled(Content)`
  justify-content: left;
  padding-top: 15px;
  padding-bottom: 39px;
`;

const EntityIcon = styled.img`
  margin-right: 15px;
`;

const TableItemTitle: React.FC<IProps> = ({
  type,
  dropDownData,
  onSelect,
  entity,
  entityName,
  entityIcon,
}) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <>
      <EntityInfo>
        {entityIcon && <EntityIcon src={entityIcon} height={40} alt={"ico"} />}
        <div>
          <H3 bold>{entityName}</H3>
          <EntityType>{entity}</EntityType>
        </div>
      </EntityInfo>
      <Content>
        <H5>
          <FormattedMessage id="tables.connections" />
        </H5>
        <DropDown
          onSelect={onSelect}
          data={[
            {
              text: formatMessage({
                id: `tables.${type}AddNew`,
              }),
              value: "create-new-item",
              primary: true,
            },
            ...dropDownData,
          ]}
          hasFilter
          withButton
          textButton={formatMessage({
            id: `tables.${type}Add`,
          })}
        />
      </Content>
    </>
  );
};

export default TableItemTitle;
