import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BarChart from "components/BarChart";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useGetUsage } from "packages/cloud/services/workspaces/WorkspacesService";

export const ChartWrapper = styled.div`
  width: 100%;
  height: 260px;
  padding: 0 50px 24px 0;
`;

const LegendLabels = ["value"];

const CreditsUsagePage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  const { workspaceId } = useCurrentWorkspace();
  const { data } = useGetUsage(workspaceId);

  const chartData = useMemo(
    () =>
      data?.creditConsumptionByDay?.map((item) => ({
        name: `${item.date?.[2]}.${item.date?.[1]}`,
        value: item.creditsConsumed,
      })),
    [data]
  );

  return (
    <ContentCard title={<FormattedMessage id="credits.totalUsage" />} $light>
      <ChartWrapper>
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
      </ChartWrapper>
    </ContentCard>
  );
};

export default CreditsUsagePage;
