import type { Url } from "url";

import { FormattedMessage } from "react-intl";
import { PluggableList } from "react-markdown/lib/react-markdown";
import { ReflexElement } from "react-reflex";
import rehypeSlug from "rehype-slug";
import urls from "rehype-urls";
import styled from "styled-components";

import { LoadingPage, PageTitle } from "components";
import { Card } from "components/base";
import Markdown from "components/Markdown/Markdown";

import { useConfig } from "config";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { useDocumentation } from "hooks/services/useDocumentation";

export const DocumentationContainer = styled(Card)`
  padding: 0px 0px 20px;
  background-color: #ffffff;
`;

export const DocumentationContent = styled(Markdown)`
  padding: 0px 35px 20px;
`;

type DocsPanelProps = {
  selectedService: SourceDefinition | DestinationDefinition | undefined;
  documentationUrl: string;
};

const DocumentationPanel: React.FC<{ onClose: () => void } & DocsPanelProps> = ({ documentationUrl }) => {
  const config = useConfig();

  const { data: docs, isLoading } = useDocumentation(documentationUrl);

  const sanitizeLinks = (url: Url, element: Element) => {
    // Relative URLs pointing to another place within the documentation.
    if (url.path?.startsWith("../../")) {
      if (element.tagName === "img") {
        // In images replace relative URLs with links to our bundled assets
        return url.path.replace("../../", `${config.integrationUrl}/`);
      } else {
        // In links replace with a link to the external documentation instead
        // The external path is the markdown URL without the "../../" prefix and the .md extension
        const docPath = url.path.replace(/^\.\.\/\.\.\/(.*?)(\.md)?$/, "$1");
        return `${config.ui.docsLink}/${docPath}`;
      }
    }
    return url.href;
  };

  const urlReplacerPlugin: PluggableList = [
    [urls, sanitizeLinks],
    // @ts-expect-error rehype-slug currently has type conflicts due to duplicate vfile dependencies
    [rehypeSlug],
  ];

  return (
    <>
      {isLoading ? (
        <LoadingPage />
      ) : docs ? (
        <DocumentationContainer>
          <PageTitle withLine title={<FormattedMessage id="connector.setupGuide" />} />
          <DocumentationContent content={docs} rehypePlugins={urlReplacerPlugin} />
        </DocumentationContainer>
      ) : (
        <ReflexElement className="right-pane" maxSize={1000}>
          <FormattedMessage id="docs.notFoundError" />
        </ReflexElement>
      )}
    </>
  );
};

export default DocumentationPanel;
