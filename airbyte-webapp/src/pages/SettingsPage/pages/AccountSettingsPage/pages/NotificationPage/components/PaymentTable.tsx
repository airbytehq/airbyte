import React from "react";
import { FormattedMessage } from "react-intl";

import { Row, Cell } from "components";
import { Separator } from "components/Separator";

import { NotificationItem } from "core/request/DaspireClient";

import { NotificationFlag } from "./NotificationFlag";
import { FirstHeaderText, HeaderText, BodyRow, FirstCellFlexValue, BodyCell } from "./StyledTable";

interface IProps {
  paymentFail: NotificationItem;
}

export const PaymentTable: React.FC<IProps> = React.memo(({ paymentFail }) => {
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
          <NotificationFlag isActive={paymentFail.emailFlag} isDisabled />
        </BodyCell>
        <BodyCell>
          <NotificationFlag isActive={paymentFail.appsFlag} isDisabled />
        </BodyCell>
      </BodyRow>
    </>
  );
});
