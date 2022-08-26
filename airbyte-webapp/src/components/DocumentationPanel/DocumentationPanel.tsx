import type { Url } from "url";

import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useIntl } from "react-intl";
import { PluggableList } from "react-markdown/lib/react-markdown";
import { ReflexElement } from "react-reflex";
import { useLocation } from "react-router-dom";
import { useUpdateEffect } from "react-use";
import rehypeSlug from "rehype-slug";
import urls from "rehype-urls";
import styled from "styled-components";

import { LoadingPage, PageTitle } from "components";
import Markdown from "components/Markdown/Markdown";

import { useConfig } from "config";
import { useDocumentation } from "hooks/services/useDocumentation";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

export const DocumentationContainer = styled.div`
  padding: 0px 0px 20px;
  background-color: #ffffff;
  min-height: 100vh;
`;

export const DocumentationContent = styled(Markdown)`
  padding: 0px 35px 20px;
`;

export const DocumentationPanel: React.FC = () => {
  const config = useConfig();

  const { setDocumentationPanelOpen, documentationUrl } = useDocumentationPanelContext();

  const { data: docs, isLoading } = useDocumentation(documentationUrl);
  const { formatMessage } = useIntl();
  // @ts-expect-error rehype-slug currently has type conflicts due to duplicate vfile dependencies
  const urlReplacerPlugin: PluggableList = useMemo<PluggableList>(() => {
    const sanitizeLinks = (url: Url, element: Element) => {
      // Relative URLs pointing to another place within the documentation.
      if (url.path?.startsWith("../../")) {
        if (element.tagName === "img") {
          // In images replace relative URLs with links to our bundled assets
          return url.path.replace("../../", `${config.integrationUrl}/`);
        }
        // In links replace with a link to the external documentation instead
        // The external path is the markdown URL without the "../../" prefix and the .md extension
        const docPath = url.path.replace(/^\.\.\/\.\.\/(.*?)(\.md)?$/, "$1");
        return `${config.links.docsLink}/${docPath}`;
      }
      return url.href;
    };
    return [[urls, sanitizeLinks], [rehypeSlug]];
  }, [config.integrationUrl, config.links.docsLink]);

  const location = useLocation();

  useUpdateEffect(() => {
    setDocumentationPanelOpen(false);
  }, [setDocumentationPanelOpen, location.pathname]);

  return isLoading || documentationUrl === "" ? (
    <LoadingPage />
  ) : docs ? (
    <DocumentationContainer>
      <PageTitle withLine title={<FormattedMessage id="connector.setupGuide" />} />
      {!docs.includes("<!DOCTYPE html>") ? (
        <DocumentationContent content={docs} rehypePlugins={urlReplacerPlugin} />
      ) : (
        <DocumentationContent content={formatMessage({ id: "connector.setupGuide.notFound" })} />
      )}
    </DocumentationContainer>
  ) : (
    <ReflexElement className="right-pane" maxSize={1000}>
      <FormattedMessage id="connector.setupGuide.notFound" />
    </ReflexElement>
  );
};
