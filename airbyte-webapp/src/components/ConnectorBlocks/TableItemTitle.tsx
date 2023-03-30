import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button, DropDownRow } from "components";
import { Popout } from "components/base/Popout/Popout";

import { ReleaseStage } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

interface TableItemTitleProps {
  type: "source" | "destination";
  dropDownData: DropDownRow.IDataItem[];
  onSelect: (item: DropDownRow.IDataItem) => void;
  entity: string;
  entityName: string;
  entityIcon?: React.ReactNode;
  releaseStage?: ReleaseStage;
  num: number;
  btnText: React.ReactNode;
}

const Content = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0 20px 0;
`;

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
`;

const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  color: #ffffff;
`;

const LeftPanel = styled.div`
  font-weight: 500;
  font-size: 16px;
  line-height: 30px;
  color: #27272a;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;

const TableItemTitle: React.FC<TableItemTitleProps> = ({ type, dropDownData, onSelect, btnText, num }) => {
  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);
  const { formatMessage } = useIntl();
  const options = [
    {
      label: formatMessage({
        id: `tables.${type}AddNew`,
      }),
      value: "create-new-item",
      primary: true,
    },
    ...dropDownData,
  ];

  return (
    <>
      {/* <EntityInfo>
        {entityIcon && <EntityIcon>{entityIcon}</EntityIcon>}
        <div>
          <H3 bold>{entityName}</H3>
          <EntityType>
            <span>{entity}</span>
            <ReleaseStageBadge stage={releaseStage} />
          </EntityType>
        </div>
      </EntityInfo> */}
      <Content>
        <LeftPanel>
          <FormattedMessage id={`tables.${type}ConnectWithNum`} values={{ num }} />
        </LeftPanel>

        <Popout
          data-testid={`select-${type}`}
          options={options}
          isSearchable={false}
          styles={{
            menuPortal: (base) => ({
              ...base,
              "margin-left": "-70px",
            }),
          }}
          onChange={onSelect}
          targetComponent={({ onOpen }) => (
            <Button onClick={onOpen} disabled={!allowCreateConnection}>
              <BtnInnerContainer>
                <BtnIcon icon={faPlus} />
                <BtnText>{btnText}</BtnText>
              </BtnInnerContainer>
            </Button>
          )}
        />
      </Content>
    </>
  );
};

export default TableItemTitle;
