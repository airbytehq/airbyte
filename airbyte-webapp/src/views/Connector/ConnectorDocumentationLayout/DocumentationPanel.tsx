import type { Url } from "url";

import { faArrowDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { PluggableList } from "react-markdown/lib/react-markdown";
import { useLocation } from "react-router-dom";
import { useUpdateEffect } from "react-use";
import rehypeSlug from "rehype-slug";
import urls from "rehype-urls";
import { match } from "ts-pattern";

import { LoadingPage } from "components";
import { Button } from "components/ui/Button";
import { Markdown } from "components/ui/Markdown";
import { PageHeader } from "components/ui/PageHeader";
import { StepsMenu } from "components/ui/StepsMenu";
import { Text } from "components/ui/Text";

import { useConfig } from "config";
import { SourceDefinitionRead } from "core/request/AirbyteClient";
import { useDocumentation } from "hooks/services/useDocumentation";
import { isCloudApp } from "utils/app";
import { links } from "utils/links";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./DocumentationPanel.module.scss";
import octaviaWorker from "./octavia-worker.png";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";

const OSS_ENV_MARKERS = /<!-- env:oss -->([\s\S]*?)<!-- \/env:oss -->/gm;
const CLOUD_ENV_MARKERS = /<!-- env:cloud -->([\s\S]*?)<!-- \/env:cloud -->/gm;

export const prepareMarkdown = (markdown: string, env: "oss" | "cloud"): string => {
  return env === "oss" ? markdown.replaceAll(CLOUD_ENV_MARKERS, "") : markdown.replaceAll(OSS_ENV_MARKERS, "");
};

const ResourceNotAvailable: React.FC<
  React.PropsWithChildren<{ activeTab: "erd" | "schema"; setRequested: (val: boolean) => void }>
> = ({ activeTab, setRequested }) => {
  const { selectedConnectorDefinition } = useDocumentationPanelContext();
  const { trackRequest } = useAnalyticsTrackFunctions();
  return (
    <>
      <Text size="lg">
        <FormattedMessage id="sources.request.prioritize" />
      </Text>
      <FontAwesomeIcon icon={faArrowDown} />
      <Button
        variant="primary"
        onClick={() => {
          trackRequest({
            sourceDefinitionId: (selectedConnectorDefinition as SourceDefinitionRead).sourceDefinitionId,
            connectorName: selectedConnectorDefinition.name,
            requestType: activeTab,
          });
          setRequested(true);
        }}
      >
        <FormattedMessage id={`sources.request.button.${activeTab}`} />
      </Button>
    </>
  );
};

export const DocumentationPanel: React.FC = () => {
  const { formatMessage } = useIntl();
  const config = useConfig();
  const { setDocumentationPanelOpen, documentationUrl, selectedConnectorDefinition } = useDocumentationPanelContext();
  const isSource = Object.hasOwn(selectedConnectorDefinition, "sourceDefinitionId");

  const [isSchemaRequested, setIsSchemaRequested] = useState(false);
  const [isERDRequested, setIsERDRequested] = useState(false);

  const { data: docs, isLoading, error } = useDocumentation(documentationUrl);

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

  const [activeTab, setActiveTab] = useState("docs");
  const tabs = [
    {
      id: "docs",
      name: <FormattedMessage id="sources.documentationPanel.tabs.docs" />,
    },
    {
      id: "schema",
      name: <FormattedMessage id="sources.documentationPanel.tabs.schema" />,
    },
    {
      id: "erd",
      name: <FormattedMessage id="sources.documentationPanel.tabs.erd" />,
    },
  ];

  return isLoading || documentationUrl === "" ? (
    <LoadingPage />
  ) : (
    <div className={styles.container}>
      <PageHeader withLine title={<FormattedMessage id="connector.setupGuide" />} />
      {isSource && <StepsMenu lightMode data={tabs} onSelect={setActiveTab} activeStep={activeTab} />}

      {match(activeTab)
        .with("docs", () => (
          <Markdown
            className={styles.content}
            content={
              docs && !error
                ? prepareMarkdown(docs, isCloudApp() ? "cloud" : "oss")
                : formatMessage({ id: "connector.setupGuide.notFound" })
            }
            rehypePlugins={urlReplacerPlugin}
          />
        ))
        .with("schema", () => (
          <div className={styles.requestContainer}>
            <img src={octaviaWorker} alt="" className={styles.emptyListImage} />
            {isSchemaRequested ? (
              <Text size="lg">
                <FormattedMessage id="sources.request.thankYou" />{" "}
              </Text>
            ) : (
              <ResourceNotAvailable activeTab="schema" setRequested={setIsSchemaRequested} />
            )}
          </div>
        ))
        .with("erd", () => {
          <div className={styles.requestContainer}>
            <img src={octaviaWorker} alt="" className={styles.emptyListImage} />
            {isERDRequested ? (
              <Text size="lg">
                <FormattedMessage id="sources.request.thankYou" />
              </Text>
            ) : (
              <ResourceNotAvailable activeTab="erd" setRequested={setIsERDRequested} />
            )}
          </div>;
        })
        .otherwise(() => null)}
    </div>
  );
};
