import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Row, Cell } from "components";
import { Separator } from "components/Separator";

import { NotificationItem } from "core/request/DaspireClient";

import { AddIcon } from "../icons";
import { FirstHeaderText, HeaderText, FirstCellFlexValue, BodyCell } from "./StyledTable";
import { UsageTableRow } from "./UsageTableRow";

interface IProps {
  usageList: NotificationItem[];
  usageNotificationList: NotificationItem[];
  createNotificationSetting: () => void;
  saveNotificationSetting: (data: NotificationItem) => void;
  updateLoading: boolean;
  updateNotificationSetting: (data: NotificationItem) => void;
  deleteNotificationSetting: (notificationSettingId: string) => void;
}

const ButtonContentContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const AddButton = styled.button`
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  margin: 0;
`;

const AddButtonText = styled.div`
  font-style: normal;
  font-weight: 500;
  font-size: 14px;
  line-height: 16px;
  color: #4f46e5;
  margin-left: 11px;
`;

export const UsageTable: React.FC<IProps> = ({
  usageList,
  usageNotificationList,
  createNotificationSetting,
  saveNotificationSetting,
  updateLoading,
  updateNotificationSetting,
  deleteNotificationSetting,
}) => {
  return (
    <>
      {/* Table Header Row */}
      <Row>
        <Cell flex={FirstCellFlexValue}>
          <FirstHeaderText>
            <FormattedMessage id="usageTable.cell.usage" />
          </FirstHeaderText>
        </Cell>
        <BodyCell>
          <HeaderText>
            <FormattedMessage id="usageTable.cell.email" />
          </HeaderText>
        </BodyCell>
        <BodyCell>
          <HeaderText>
            <FormattedMessage id="usageTable.cell.inApp" />
          </HeaderText>
        </BodyCell>
      </Row>
      {/* Table Body Rows */}
      {usageNotificationList
        .slice(0)
        .reverse()
        .sort((x, y) => Number(y.defaultFlag) - Number(x.defaultFlag))
        .map((usageItem) => (
          <>
            <Separator />
            <UsageTableRow
              usageItem={usageItem}
              saveNotificationSetting={saveNotificationSetting}
              updateLoading={updateLoading}
              updateNotificationSetting={updateNotificationSetting}
              deleteNotificationSetting={deleteNotificationSetting}
            />
          </>
        ))}
      {usageNotificationList.length === usageList.length && (
        <>
          <Separator />
          <Row>
            <Cell>
              <AddButton onClick={createNotificationSetting}>
                <ButtonContentContainer>
                  <AddIcon />
                  <AddButtonText>
                    <FormattedMessage id="usageTable.cell.addBtn.text" />
                  </AddButtonText>
                </ButtonContentContainer>
              </AddButton>
            </Cell>
          </Row>
        </>
      )}
    </>
  );
};
