import React from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { Card } from "components/ui/Card";

import LogsContent from "./components/LogsContent";

const ConfigurationsPage: React.FC = () => {
  return (
    <>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "admin.configuration" }]} />
      <Card title={<FormattedMessage id="admin.logs" />}>
        <LogsContent />
      </Card>
    </>
  );
};

export default ConfigurationsPage;
