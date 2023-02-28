import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Card } from "components";
import { DashIcon } from "components/icons/DashIcon";
import { TickIcon } from "components/icons/TickIcon";
import { Separator } from "components/Separator";
import { Row, Cell } from "components/SimpleTableComponents";

import { ProductItem, ProcessedPackageMap } from "core/domain/product";

import EnterpriseCell from "./EnterpriseCell";
import ProfessionalCell from "./ProfessionalCell";

interface IProps {
  onSelectPlan?: () => void;
  selectPlanBtnDisability: boolean;
  product?: ProductItem;
  paymentLoading: boolean;
  packagesMap: ProcessedPackageMap;
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

const FeaturesCard: React.FC<IProps> = ({
  onSelectPlan,
  selectPlanBtnDisability,
  product,
  paymentLoading,
  packagesMap,
}) => {
  return (
    <Card withPadding roundedBottom>
      <CardContainer>
        <Row borderBottom="1px solid #E5E7EB">
          <HeaderCell>
            <FormattedMessage id="feature.header.plan" />
          </HeaderCell>
          <HeaderCell>
            <FormattedMessage id="feature.header.professional" />
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
            <ProfessionalCell
              price={product?.price}
              selectPlanBtnDisability={selectPlanBtnDisability}
              paymentLoading={paymentLoading}
              onSelectPlan={onSelectPlan}
            />
          </BodyCell>
          <BodyCell>
            <EnterpriseCell />
          </BodyCell>
        </Row>
        <Separator height="30px" />
        <HighlightedRow borderTop="1px solid #E5E7EB" borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.feature.heading" />
          </HeaderCell>
        </HighlightedRow>
        {packagesMap.features.map((item) => (
          <FeatureBodyRow borderBottom="1px solid #E5E7EB">
            <FeatureBodyCell>{item.itemName}</FeatureBodyCell>
            <FeatureBodyCell>{item.professional?.itemScopeLang}</FeatureBodyCell>
            <FeatureBodyCell>{item.enterprise?.itemScopeLang}</FeatureBodyCell>
          </FeatureBodyRow>
        ))}
        <HighlightedRow borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.dataReplication.heading" />
          </HeaderCell>
        </HighlightedRow>
        {packagesMap.dataReplication.map((item) => (
          <FeatureBodyRow borderBottom="1px solid #E5E7EB">
            <FeatureBodyCell>{item.itemName}</FeatureBodyCell>
            <FeatureBodyCell>{item.professional?.itemScopeLang}</FeatureBodyCell>
            <FeatureBodyCell>{item.enterprise?.itemScopeLang}</FeatureBodyCell>
          </FeatureBodyRow>
        ))}
        <HighlightedRow borderBottom="1px solid #E5E7EB">
          <HeaderCell padding="12px 16px">
            <FormattedMessage id="plan.support.heading" />
          </HeaderCell>
        </HighlightedRow>
        {packagesMap.support.map((item) => (
          <FeatureBodyRow borderBottom="1px solid #E5E7EB">
            <FeatureBodyCell>{item.itemName}</FeatureBodyCell>
            <FeatureBodyCell>
              {item.professional?.itemScope === "false" || item.professional?.itemScope === "true" ? (
                item.professional?.itemScope === "false" ? (
                  <DashIcon />
                ) : (
                  <TickIcon />
                )
              ) : (
                item.professional?.itemScopeLang
              )}
            </FeatureBodyCell>
            <FeatureBodyCell>
              {item.enterprise?.itemScope === "false" || item.enterprise?.itemScope === "true" ? (
                item.enterprise?.itemScope === "false" ? (
                  <DashIcon />
                ) : (
                  <TickIcon />
                )
              ) : (
                item.enterprise?.itemScopeLang
              )}
            </FeatureBodyCell>
          </FeatureBodyRow>
        ))}
      </CardContainer>
    </Card>
  );
};

export default FeaturesCard;
