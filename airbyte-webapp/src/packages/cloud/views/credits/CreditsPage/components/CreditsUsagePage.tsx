import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BarChart from "components/BarChart";
// import { useCurrentWorkspace } from "hooks/services/useWorkspace";
// import { useGetUsage } from "packages/cloud/services/workspaces/WorkspacesService";

export const ChartWrapper = styled.div`
  width: 100%;
  height: 260px;
  padding: 0 50px 24px 0;
`;

const CreditsUsagePage: React.FC = () => {
  // TODO: add real data
  // const { workspaceId } = useCurrentWorkspace();
  // const { data } = useGetUsage(workspaceId);

  const data = {
    workspaceId: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    creditConsumptionByConnector: [
      {
        connectionId: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        creditsConsumed: 0,
      },
    ],
    creditConsumptionByDay: [
      {
        date: "2021-09-22",
        creditsConsumed: 80,
      },
      {
        date: "2021-09-23",
        creditsConsumed: 30,
      },
      {
        date: "2021-09-24",
        creditsConsumed: 40,
      },
      {
        date: "2021-09-25",
        creditsConsumed: 56,
      },
      {
        date: "2021-09-26",
        creditsConsumed: 67,
      },
      {
        date: "2021-09-27",
        creditsConsumed: 42,
      },
    ],
  };

  const chartData = data.creditConsumptionByDay.map((item) => ({
    name: item.date,
    creditsConsumed: item.creditsConsumed,
  }));

  return (
    <ContentCard title={<FormattedMessage id="credits.totalUsage" />} $light>
      <ChartWrapper>
        <BarChart data={chartData} legendLabels={["creditsConsumed"]} />
      </ChartWrapper>
    </ContentCard>
  );
};

export default CreditsUsagePage;
