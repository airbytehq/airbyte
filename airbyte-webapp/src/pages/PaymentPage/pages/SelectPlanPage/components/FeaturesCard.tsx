import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Card } from "components";
import { DashIcon } from "components/icons/DashIcon";
import { TickIcon } from "components/icons/TickIcon";
import { Separator } from "components/Separator";
import { Row, Cell } from "components/SimpleTableComponents";

import EnterpriseCell from "./EnterpriseCell";
import ProcessionalCell from "./ProcessionalCell";

interface IProps {
  onSelectPlan?: () => void;
}

const CardContainer = styled.div`
  padding: 10px 20px;
`;

const HeaderCell = styled(Cell)<{ padding?: string }>`
  font-weight: 500;
  font-size: 14px;
  line-height: 20px;
  color: ${({ theme }) => theme.black300};
  padding: ${({ padding }) => (padding ? padding : "0 20px 10px 20px")};
`;

const BodyCell = styled(Cell)`
  font-weight: 400;
  font-size: 14px;
  line-height: 20px;
  color: ${({ theme }) => theme.black300};
  padding: 30px 20px 10px 20px;
`;

const HighlightedRow = styled(Row)`
  background-color: #f9fafb;
  padding: 18px 0;
`;

const FeatureBodyRow = styled(Row)`
  padding: 24px 0;
`;

const FeatureBodyCell = styled(Cell)`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: #6b6b6f;
  padding: 0 24px;
`;

const FeaturesCard: React.FC<IProps> = ({ onSelectPlan }) => {
  return (
    <Card withPadding roundedBottom>
      <CardContainer>
        <Row borderBottom="1px solid #E5E7EB">
          <HeaderCell>
            <FormattedMessage id="feature.header.plan" />
          </HeaderCell>
          <HeaderCell>
            <FormattedMessage id="feature.header.processional" />
          </HeaderCell>
          <HeaderCell>
            <FormattedMessage id="feature.header.enterprise" />
          </HeaderCell>
        </Row>
        <Row alignItems="flex-start" height="auto">
          <BodyCell>
            <FormattedMessage id="feature.cell.pricing" />
          </BodyCell>
          <BodyCell>
            <ProcessionalCell price={58} onSelectPlan={onSelectPlan} />
          </BodyCell>
          <BodyCell>
            <EnterpriseCell />
          </BodyCell>
        </Row>
        <Separator height="30px" />
        {/* Features Table */}
        <HighlightedRow borderTop="1px solid #E5E7EB" borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.feature.heading" />
          </HeaderCell>
        </HighlightedRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>No. of Users</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>No. of Data Source</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>No. of Destinations</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow>
          <FeatureBodyCell>No. of Connections</FeatureBodyCell>
          <FeatureBodyCell>50</FeatureBodyCell>
          <FeatureBodyCell>Unlimited</FeatureBodyCell>
        </FeatureBodyRow>
        {/* Data Replication Table */}
        <HighlightedRow borderTop="1px solid #E5E7EB" borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.dataReplication.heading" />
          </HeaderCell>
        </HighlightedRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>No. of Concurrent Jobs</FeatureBodyCell>
          <FeatureBodyCell>5</FeatureBodyCell>
          <FeatureBodyCell>10</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>Replication Frequency</FeatureBodyCell>
          <FeatureBodyCell>From 5 minutes to 24 hours</FeatureBodyCell>
          <FeatureBodyCell>From 5 minutes to 24 hours</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow>
          <FeatureBodyCell>Replication Types</FeatureBodyCell>
          <FeatureBodyCell>Full</FeatureBodyCell>
          <FeatureBodyCell>Full & incremental</FeatureBodyCell>
        </FeatureBodyRow>
        {/* Support Table */}
        <HighlightedRow borderTop="1px solid #E5E7EB" borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.support.heading" />
          </HeaderCell>
        </HighlightedRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>Support</FeatureBodyCell>
          <FeatureBodyCell>Standard email support (response within 48 hours)</FeatureBodyCell>
          <FeatureBodyCell>Priority email support (response within 24 hours)</FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>Audit log</FeatureBodyCell>
          <FeatureBodyCell>
            <DashIcon />
          </FeatureBodyCell>
          <FeatureBodyCell>
            <TickIcon />
          </FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>SLA</FeatureBodyCell>
          <FeatureBodyCell>
            <DashIcon />
          </FeatureBodyCell>
          <FeatureBodyCell>
            <TickIcon />
          </FeatureBodyCell>
        </FeatureBodyRow>
        <FeatureBodyRow borderBottom="1px solid #E5E7EB">
          <FeatureBodyCell>SSO</FeatureBodyCell>
          <FeatureBodyCell>
            <DashIcon />
          </FeatureBodyCell>
          <FeatureBodyCell>
            <TickIcon />
          </FeatureBodyCell>
        </FeatureBodyRow>
      </CardContainer>
    </Card>
  );
};

export default FeaturesCard;
