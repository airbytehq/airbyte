import React from "react";
import { FormattedMessage } from "react-intl";

import { Row, Cell } from "components";
import { Separator } from "components/Separator";

import { NotificationItem } from "core/request/DaspireClient";

import { NotificationFlag } from "./NotificationFlag";
import { FirstHeaderText, HeaderText, BodyRow, FirstCellFlexValue, BodyCell } from "./StyledTable";

interface IProps {
  paymentFail: NotificationItem;
  updateLoading: boolean;
  updateNotificationSetting: (editNotificationBody: NotificationItem) => void;
}

export const PaymentTable: React.FC<IProps> = React.memo(
  ({ paymentFail, updateNotificationSetting, updateLoading }) => {
    return (
      <>
        <Row>
          <Cell flex={FirstCellFlexValue}>
            <FirstHeaderText>
              <FormattedMessage id="paymentTable.cell.payment" />
            </FirstHeaderText>
          </Cell>
        </Row>
        <Separator />
        <BodyRow>
          <Cell flex={FirstCellFlexValue}>
            <HeaderText>
              <FormattedMessage id="paymentTable.cell.fail" />
            </HeaderText>
          </Cell>
          <BodyCell>
            <NotificationFlag isLoading={updateLoading} isActive={paymentFail.emailFlag} />
          </BodyCell>
          <BodyCell>
            <NotificationFlag
              isLoading={updateLoading}
              isActive={paymentFail.appsFlag}
              onClick={() => {
                updateNotificationSetting({
                  id: paymentFail.id,
                  type: paymentFail.type,
                  value: paymentFail.value,
                  emailFlag: paymentFail.emailFlag,
                  appsFlag: !paymentFail.appsFlag,
                });
              }}
            />
          </BodyCell>
        </BodyRow>
      </>
    );
  }
);
