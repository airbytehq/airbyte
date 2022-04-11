import type { Url } from "url";

import urls from "rehype-urls";
import { PluggableList } from "react-markdown/lib/react-markdown";
import rehypeSlug from "rehype-slug";
import { FormattedMessage } from "react-intl";

import { LoadingPage } from "components";
import Markdown from "components/Markdown/Markdown";
import { Body } from "components/SideView/styled";

import { useDocumentation } from "hooks/services/useDocumentation";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";
import { useConfig } from "config";

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
        <div>
          <Body>
            <Markdown content={docs} rehypePlugins={urlReplacerPlugin} />
          </Body>
        </div>
      ) : (
        <FormattedMessage id="docs.notFoundError" />
      )}
    </>
  );
};

export default DocumentationPanel;
