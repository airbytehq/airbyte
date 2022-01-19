import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
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
  const { formatMessage, formatDate } = useIntl();

  const { workspaceId } = useCurrentWorkspace();
  const { data } = useGetUsage(workspaceId);

  const chartData = useMemo(
    () =>
      data?.creditConsumptionByDay?.map(({ creditsConsumed, date }) => ({
        name: formatDate(
          new Date(date[0], date[1] - 1 /* zero-indexed */, date[2]),
          {
            month: "short",
            day: "numeric",
          }
        ),
        value: creditsConsumed,
      })),
    [data, formatDate]
  );

  return (
    <>
      <ContentCard title={<FormattedMessage id="credits.totalUsage" />} light>
        <ChartWrapper>
          {data && data.creditConsumptionByDay.length ? (
            <BarChart
              data={chartData}
              legendLabels={LegendLabels}
              xLabel={formatMessage({
                id: "credits.date",
              })}
              yLabel={formatMessage({
                id: "credits.amount",
              })}
            />
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
