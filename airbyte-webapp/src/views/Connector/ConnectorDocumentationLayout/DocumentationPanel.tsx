import type { Url } from "url";

import { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { PluggableList } from "react-markdown/lib/react-markdown";
import { useLocation } from "react-router-dom";
import { useUpdateEffect } from "react-use";
import rehypeSlug from "rehype-slug";
import urls from "rehype-urls";

import { LoadingPage } from "components";
import { Markdown } from "components/ui/Markdown";
import { PageHeader } from "components/ui/PageHeader";

import { useConfig } from "config";
import { useDocumentation } from "hooks/services/useDocumentation";
import { isCloudApp } from "utils/app";
import { links } from "utils/links";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./DocumentationPanel.module.scss";

const OSS_ENV_MARKERS = /<!-- env:oss -->([\s\S]*?)<!-- \/env:oss -->/gm;
const CLOUD_ENV_MARKERS = /<!-- env:cloud -->([\s\S]*?)<!-- \/env:cloud -->/gm;

export const prepareMarkdown = (markdown: string, env: "oss" | "cloud"): string => {
  return env === "oss" ? markdown.replaceAll(CLOUD_ENV_MARKERS, "") : markdown.replaceAll(OSS_ENV_MARKERS, "");
};

export const DocumentationPanel: React.FC = () => {
  const { formatMessage } = useIntl();
  const config = useConfig();
  const { setDocumentationPanelOpen, documentationUrl } = useDocumentationPanelContext();
  const { data: docs, isLoading, error } = useDocumentation(documentationUrl);

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
        return `${links.docsLink}/${docPath}`;
      }
      return url.href;
    };
    return [[urls, sanitizeLinks], [rehypeSlug]];
  }, [config.integrationUrl]);

  const location = useLocation();

  useUpdateEffect(() => {
    setDocumentationPanelOpen(false);
  }, [setDocumentationPanelOpen, location.pathname]);

  return isLoading || documentationUrl === "" ? (
    <LoadingPage />
  ) : (
    <div className={styles.container}>
      <PageHeader withLine title={<FormattedMessage id="connector.setupGuide" />} />
      <Markdown
        className={styles.content}
        content={
          docs && !error
            ? prepareMarkdown(docs, isCloudApp() ? "cloud" : "oss")
            : formatMessage({ id: "connector.setupGuide.notFound" })
        }
        rehypePlugins={urlReplacerPlugin}
      />
    </div>
  );
};
