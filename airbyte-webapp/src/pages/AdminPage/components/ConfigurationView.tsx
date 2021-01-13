import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Button from "../../../components/Button";

const Content = styled.div`
  text-align: center;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const ConfigurationView: React.FC = () => {
  return (
    <Content>
      <ButtonWithMargin>
        <FormattedMessage id="admin.exportConfiguration" />
      </ButtonWithMargin>
      <Button>
        <FormattedMessage id="admin.importConfiguration" />
      </Button>
    </Content>
  );
};

export default ConfigurationView;
