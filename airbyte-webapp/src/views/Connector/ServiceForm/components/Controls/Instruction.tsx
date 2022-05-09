import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { getDocumentationType } from "hooks/services/useDocumentation";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationContext";

interface InstructionProps {
  selectedService: SourceDefinition | DestinationDefinition;
  documentationUrl: string;
}

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

const DocumentationLinkContent = styled.a`
  cursor: pointer;
  margin-top: 5px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  display: inline-block;

  color: ${({ theme }) => theme.primaryColor};
`;

export const DocumentationLink: React.FC<InstructionProps> = ({ documentationUrl }) => {
  const { documentationPanelOpen, setDocumentationPanelOpen } = useDocumentationPanelContext();

  const docType = getDocumentationType(documentationUrl);

  return (
    <>
      {docType === "internal" && (
        <SideViewButton type="button" onClick={() => setDocumentationPanelOpen(!documentationPanelOpen)}>
          <FormattedMessage id="form.setupGuide" />
        </SideViewButton>
      )}
      {docType === "external" && (
        <DocumentationLinkContent href={documentationUrl} target="_blank" rel="noopener noreferrer">
          <FormattedMessage id="form.setupGuide" />
        </DocumentationLinkContent>
      )}
    </>
  );
};
