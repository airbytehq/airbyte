import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

const SideViewButton = styled.button`
  cursor: pointer;
  margin-top: 5px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  display: inline-block;
  background: none;
  border: none;
  padding: 0;

  color: ${({ theme }) => theme.primaryColor};
`;

export const DocumentationLink: React.FC = () => {
  const { documentationPanelOpen, setDocumentationPanelOpen } = useDocumentationPanelContext();

  return (
    <SideViewButton type="button" onClick={() => setDocumentationPanelOpen(!documentationPanelOpen)}>
      <FormattedMessage id="connector.setupGuide" />
    </SideViewButton>
  );
};
