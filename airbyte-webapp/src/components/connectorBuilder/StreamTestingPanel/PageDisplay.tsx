import { Tab } from "@headlessui/react";
import classNames from "classnames";
import { useField } from "formik";
import { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { StreamReadInferredSchema, StreamReadSlicesItemPagesItem } from "core/request/ConnectorBuilderClient";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./PageDisplay.module.scss";
import { formatJson } from "./utils";

interface PageDisplayProps {
  page: StreamReadSlicesItemPagesItem;
  inferredSchema: StreamReadInferredSchema;
  className?: string;
}

interface TabData {
  title: string;
  key: string;
  content: string;
}

export const PageDisplay: React.FC<PageDisplayProps> = ({ page, className, inferredSchema }) => {
  const { formatMessage } = useIntl();

  const { testStreamIndex } = useConnectorBuilderState();
  const [field, , helpers] = useField(`streams[${testStreamIndex}].schema`);

  const formattedRecords = useMemo(() => formatJson(page.records), [page.records]);
  const formattedRequest = useMemo(() => formatJson(page.request), [page.request]);
  const formattedResponse = useMemo(() => formatJson(page.response), [page.response]);
  const formattedSchema = useMemo(() => formatJson(inferredSchema), [inferredSchema]);

  let defaultTabIndex = 0;
  const tabs: TabData[] = [
    {
      title: `${formatMessage({ id: "connectorBuilder.recordsTab" })} (${page.records.length})`,
      key: "records",
      content: formattedRecords,
    },
  ];
  if (page.request) {
    tabs.push({
      title: formatMessage({ id: "connectorBuilder.requestTab" }),
      key: "request",
      content: formattedRequest,
    });
  }
  if (page.response) {
    tabs.push({
      title: formatMessage({ id: "connectorBuilder.responseTab" }),
      key: "response",
      content: formattedResponse,
    });

    if (page.response.status >= 400) {
      defaultTabIndex = tabs.length - 1;
    }
  }

  tabs.push({
    title: formatMessage({ id: "connectorBuilder.schemaTab" }),
    key: "schema",
    content: formattedSchema,
  });

  return (
    <div className={classNames(className)}>
      <Tab.Group defaultIndex={defaultTabIndex}>
        <Tab.List className={styles.tabList}>
          {tabs.map((tab) => (
            <Tab className={styles.tab} key={tab.key}>
              {({ selected }) => (
                <Text className={classNames(styles.tabTitle, { [styles.selected]: selected })}>{tab.title}</Text>
              )}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels className={styles.tabPanelContainer}>
          {tabs.map((tab) => (
            <Tab.Panel className={styles.tabPanel} key={tab.key}>
              {tab.key === "schema" && (
                <Button
                  variant="secondary"
                  disabled={field.value === formattedSchema}
                  onClick={() => {
                    helpers.setValue(formattedSchema);
                  }}
                >
                  <FormattedMessage
                    id={
                      field.value === formattedSchema || !field.value
                        ? "connectorBuilder.useSchemaButton"
                        : "connectorBuilder.overwriteSchemaButton"
                    }
                  />
                </Button>
              )}
              <pre>{tab.content}</pre>
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};
