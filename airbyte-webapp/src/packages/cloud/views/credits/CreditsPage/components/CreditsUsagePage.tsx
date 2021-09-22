import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BarChart from "components/BarChart";

export const ChartWrapper = styled.div`
  width: 100%;
  height: 260px;
  padding: 0 50px 24px 0;
`;

const CreditsUsagePage: React.FC = () => {
  // TODO: add real data. Format ?
  const data = [
    {
      name: "01",
      uv: 75,
    },
    {
      name: "02",
      uv: 58,
    },
    {
      name: "03",
      uv: 62,
    },
    {
      name: "04",
      uv: 49,
    },
    {
      name: "05",
      uv: 77,
    },
    {
      name: "06",
      uv: 42,
    },
    {
      name: "07",
      uv: 77,
    },
    {
      name: "08",
      uv: 82,
    },
    {
      name: "09",
      uv: 75,
    },
    {
      name: "10",
      uv: 85,
    },
    {
      name: "11",
      uv: 90,
    },
    {
      name: "12",
      uv: 97,
    },
    {
      name: "13",
      uv: 67,
    },
    {
      name: "14",
      uv: 63,
    },
    {
      name: "15",
      uv: 79,
    },
    {
      name: "01",
      uv: 75,
    },
    {
      name: "02",
      uv: 58,
    },
    {
      name: "03",
      uv: 62,
    },
    {
      name: "04",
      uv: 49,
    },
    {
      name: "05",
      uv: 77,
    },
    {
      name: "06",
      uv: 42,
    },
    {
      name: "07",
      uv: 77,
    },
    {
      name: "08",
      uv: 82,
    },
    {
      name: "09",
      uv: 75,
    },
    {
      name: "10",
      uv: 85,
    },
    {
      name: "11",
      uv: 90,
    },
    {
      name: "12",
      uv: 97,
    },
    {
      name: "13",
      uv: 67,
    },
    {
      name: "14",
      uv: 63,
    },
    {
      name: "15",
      uv: 79,
    },
  ];

  return (
    <ContentCard title={<FormattedMessage id="credits.totalUsage" />} $light>
      <ChartWrapper>
        <BarChart data={data} />
      </ChartWrapper>
    </ContentCard>
  );
};

export default CreditsUsagePage;
