import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { getDocumentationType } from "hooks/services/useDocumentation";
import { useSidePanelContext } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationContext";

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

const DocumentationLink = styled.a`
  cursor: pointer;
  margin-top: 5px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  display: inline-block;

  color: ${({ theme }) => theme.primaryColor};
`;

export const Instruction: React.FC<InstructionProps> = ({ documentationUrl }) => {
  const { sidePanelStatus, setSidePanelStatus } = useSidePanelContext();

  const docType = getDocumentationType(documentationUrl);

  return (
    <>
      {docType === "internal" && (
        <SideViewButton type="button" onClick={() => setSidePanelStatus(!sidePanelStatus)}>
          <FormattedMessage id="form.setupGuide" />
        </SideViewButton>
      )}
      {docType === "external" && (
        <DocumentationLink href={documentationUrl} target="_blank" rel="noopener noreferrer">
          <FormattedMessage id="form.setupGuide" />
        </DocumentationLink>
      )}
    </>
  );
};
