import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useToggle } from "react-use";
import urls from "rehype-urls";
import type { PluggableList } from "react-markdown/lib/react-markdown";

import {
  useDocumentation,
  getDocumentationType,
} from "hooks/services/useDocumentation";
import { LoadingPage } from "components";
import { SideView } from "components/SideView";
import { Markdown } from "components/Markdown";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { useConfig } from "config";

type IProps = {
  selectedService: SourceDefinition | DestinationDefinition;
  documentationUrl: string;
};

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

const HeaderLink = styled.a`
  color: #fff;
  text-decoration: none;
  display: flex;
  height: 40px;
  align-items: center;
  padding: 0 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

const DocumentationPanel: React.FC<{ onClose: () => void } & IProps> = ({
  selectedService,
  documentationUrl,
  onClose,
}) => {
  const config = useConfig();
  const { data: docs, isLoading } = useDocumentation(documentationUrl);

  const removeBaseUrl = (url: { path: string }) => {
    if (url.path.startsWith("../../")) {
      return url.path.replace("../../", `${config.integrationUrl}/`);
    }
    return url.path;
  };

  const urlReplacerPlugin: PluggableList = [[urls, removeBaseUrl]];
  return (
    <SideView
      onClose={onClose}
      headerLink={
        <HeaderLink href={documentationUrl} target="_blank" rel="noreferrer">
          <FormattedMessage
            id="onboarding.instructionsLink"
            values={{ name: selectedService.name }}
          />
        </HeaderLink>
      }
    >
      {isLoading ? (
        <LoadingPage />
      ) : docs ? (
        <Markdown content={docs} rehypePlugins={urlReplacerPlugin} />
      ) : (
        <FormattedMessage id="docs.notFoundError" />
      )}
    </SideView>
  );
};

const Instruction: React.FC<IProps> = ({
  selectedService,
  documentationUrl,
}) => {
  const [isSideViewOpen, setIsSideViewOpen] = useToggle(false);
  const docType = getDocumentationType(documentationUrl);

  return (
    <>
      {isSideViewOpen && (
        <DocumentationPanel
          onClose={() => setIsSideViewOpen(false)}
          selectedService={selectedService}
          documentationUrl={documentationUrl}
        />
      )}

      {docType === "internal" && (
        <SideViewButton onClick={() => setIsSideViewOpen(true)}>
          <FormattedMessage id="form.setupGuide" />
        </SideViewButton>
      )}
      {docType === "external" && (
        <DocumentationLink
          href={documentationUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          <FormattedMessage id="form.setupGuide" />
        </DocumentationLink>
      )}
    </>
  );
};

export default Instruction;
