import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { BarChart } from "components/ui/BarChart";
import { Card } from "components/ui/Card";

import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetCloudWorkspaceUsage } from "packages/cloud/services/workspaces/CloudWorkspacesService";

import UsagePerConnectionTable from "./UsagePerConnectionTable";

export const ChartWrapper = styled.div`
  width: 100%;
  height: 260px;
  padding: 0 50px 24px 0;
`;

const CardBlock = styled(Card)`
  margin: 10px 0 20px;
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

const CreditsUsage: React.FC = () => {
  const { formatMessage, formatDate } = useIntl();

  const { workspaceId } = useCurrentWorkspace();
  const data = useGetCloudWorkspaceUsage(workspaceId);

  const chartData = useMemo(
    () =>
      data?.creditConsumptionByDay?.map(({ creditsConsumed, date }) => ({
        name: formatDate(new Date(date[0], date[1] - 1 /* zero-indexed */, date[2]), {
          month: "short",
          day: "numeric",
        }),
        value: creditsConsumed,
      })),
    [data, formatDate]
  );

  return (
    <>
      <Card title={<FormattedMessage id="credits.totalUsage" />} lightPadding>
        <ChartWrapper>
          {data?.creditConsumptionByDay?.length ? (
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
      </Card>

      <CardBlock title={<FormattedMessage id="credits.usagePerConnection" />} lightPadding>
        {data?.creditConsumptionByConnector?.length ? (
          <UsagePerConnectionTable creditConsumption={data.creditConsumptionByConnector} />
        ) : (
          <Empty>
            <FormattedMessage id="credits.noData" />
          </Empty>
        )}
      </CardBlock>
    </>
  );
};

export default CreditsUsage;
