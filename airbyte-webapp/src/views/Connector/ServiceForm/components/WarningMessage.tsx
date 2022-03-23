import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ReleaseStage } from "core/domain/connector";
import { useConfig } from "config";

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

type WarningMessageProps = {
  stage: ReleaseStage.ALPHA | ReleaseStage.BETA;
};

const WarningMessage: React.FC<WarningMessageProps> = ({ stage }) => {
  const config = useConfig();
  return (
    <Content>
      <FormattedMessage
        id={`connector.connectorsInDevelopment.${stage}`}
        values={{
          lnk: (node: React.ReactNode) => (
            <Link
              href={config.ui.productReleaseStages}
              target="_blank"
              rel="noreferrer"
            >
              {node}
            </Link>
          ),
        }}
      />
    </Content>
  );
};

export { WarningMessage };
