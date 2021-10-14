import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BarChart from "components/BarChart";
import UsagePerConnectionTable from "./UsagePerConnectionTable";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetUsage } from "packages/cloud/services/workspaces/WorkspacesService";

export const ChartWrapper = styled.div`
  width: 100%;
  height: 260px;
  padding: 0 50px 24px 0;
`;

const CardBlock = styled(ContentCard)`
  margin-top: 10px;
`;

const Empty = styled.div`
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
  padding-bottom: 20px;
`;

const LegendLabels = ["value"];

const CreditsUsagePage: React.FC = () => {
  const { workspaceId } = useCurrentWorkspace();
  const { data } = useGetUsage(workspaceId);

  const chartData = useMemo(
    () =>
      data?.creditConsumptionByDay?.map((item) => ({
        name: item.date?.[2],
        value: item.creditsConsumed,
      })),
    [data]
  );

  return (
    <>
      <ContentCard title={<FormattedMessage id="credits.totalUsage" />} light>
        <ChartWrapper>
          {data && data.creditConsumptionByDay.length ? (
            <BarChart data={chartData} legendLabels={LegendLabels} />
          ) : (
            <Empty>
              <FormattedMessage id="credits.noData" />
            </Empty>
          )}
        </ChartWrapper>
      </ContentCard>
      <CardBlock
        title={<FormattedMessage id="credits.usagePerConnection" />}
        light
      >
        {data && data.creditConsumptionByConnector.length ? (
          <UsagePerConnectionTable
            creditConsumption={data.creditConsumptionByConnector}
          />
        ) : (
          <Empty>
            <FormattedMessage id="credits.noData" />
          </Empty>
        )}
      </CardBlock>
    </>
  );
};

export default CreditsUsagePage;
