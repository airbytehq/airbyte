import React from "react";
import { FormattedMessage } from "react-intl";
// import styled from "styled-components";

import ContentCard from "components/ContentCard";

const CreditsUsagePage: React.FC = () => {
  return (
    <ContentCard title={<FormattedMessage id="credits.totalUsage" />} $light>
      CHART
    </ContentCard>
  );
};

export default CreditsUsagePage;
