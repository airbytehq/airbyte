import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { HeadTitle } from "components/common/HeadTitle";
import { Card } from "components/ui/Card";

import LogsContent from "./components/LogsContent";

const Content = styled.div`
  max-width: 813px;
`;

const ControlContent = styled(Card)`
  margin-top: 12px;
`;

const ConfigurationsPage: React.FC = () => {
  return (
    <Content>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "admin.configuration" }]} />
      <ControlContent title={<FormattedMessage id="admin.logs" />}>
        <LogsContent />
      </ControlContent>
    </Content>
  );
};

export default ConfigurationsPage;
