import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { useConfig } from "config";
import { ReleaseStage } from "core/request/AirbyteClient";

const Content = styled.div`
  padding: 13px 16px;
  background: ${({ theme }) => theme.warningBackgroundColor};
  border-radius: 8px;
  font-size: 12px;
  white-space: break-spaces;
  margin-top: 16px;
`;

const Link = styled.a`
  color: ${({ theme }) => theme.darkPrimaryColor};

  &:hover,
  &:focus {
    color: ${({ theme }) => theme.darkPrimaryColor60};
  }
`;

interface WarningMessageProps {
  stage: typeof ReleaseStage.alpha | typeof ReleaseStage.beta;
}

const WarningMessage: React.FC<WarningMessageProps> = ({ stage }) => {
  const config = useConfig();
  return (
    <Content>
      <FormattedMessage id={`connector.releaseStage.${stage}.description`} />{" "}
      <FormattedMessage
        id="connector.connectorsInDevelopment.docLink"
        values={{
          lnk: (node: React.ReactNode) => (
            <Link href={config.links.productReleaseStages} target="_blank" rel="noreferrer">
              {node}
            </Link>
          ),
        }}
      />
    </Content>
  );
};

export { WarningMessage };
