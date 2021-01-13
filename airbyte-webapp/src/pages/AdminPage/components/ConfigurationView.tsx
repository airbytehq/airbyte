import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Button from "../../../components/Button";
import ContentCard from "../../../components/ContentCard";
import config from "../../../config";
import Link from "../../../components/Link";

const Content = styled.div`
  max-width: 813px;
  margin: 4px auto;
`;

const ControlContent = styled(ContentCard)`
  margin-top: 12px;
  padding: 29px 28px 27px;
  display: flex;
  align-items: center;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
  flex: 1 0 0;
`;

const DocLink = styled(Link).attrs({ as: "a" })`
  text-decoration: none;
  display: inline-block;
`;

const Warning = styled.div`
  font-weight: bold;
`;

const ConfigurationView: React.FC = () => {
  return (
    <Content>
      <ControlContent>
        <Button>
          <FormattedMessage id="admin.exportConfiguration" />
        </Button>
        <Text>
          <FormattedMessage
            id="admin.exportConfigurationText"
            values={{
              lnk: (...lnk: React.ReactNode[]) => (
                <DocLink
                  target="_blank"
                  href={config.ui.configurationArchiveLink}
                  as="a"
                >
                  {lnk}
                </DocLink>
              )
            }}
          />
        </Text>
      </ControlContent>

      <ControlContent>
        <Button>
          <FormattedMessage id="admin.importConfiguration" />
        </Button>
        <Text>
          <FormattedMessage
            id="admin.importConfigurationText"
            values={{
              b: (...b: React.ReactNode[]) => <Warning>{b}</Warning>
            }}
          />
        </Text>
      </ControlContent>
    </Content>
  );
};

export default ConfigurationView;
