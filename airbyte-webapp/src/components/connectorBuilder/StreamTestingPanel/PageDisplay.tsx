import { Tab } from "@headlessui/react";
import classNames from "classnames";
// import { diffLines } from "diff";
import { useField } from "formik";
import { diffString } from "json-diff";
import merge from "lodash/merge";
import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import { StreamReadInferredSchema, StreamReadSlicesItemPagesItem } from "core/request/ConnectorBuilderClient";
import { useConnectorBuilderTestState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./PageDisplay.module.scss";
import { formatJson } from "./utils";

interface PageDisplayProps {
  page: StreamReadSlicesItemPagesItem;
  inferredSchema?: StreamReadInferredSchema;
  className?: string;
}

function getDiff(existingSchema?: string, detectedSchema?: unknown) {
  let existingObject = undefined;
  try {
    existingObject = existingSchema ? JSON.parse(existingSchema) : undefined;
  } catch {}
  return diffString(existingObject, detectedSchema, { color: false, full: true });
}

interface TabData {
  title: string;
  key: string;
  content: string;
}

export const PageDisplay: React.FC<PageDisplayProps> = ({ page, className, inferredSchema }) => {
  const { formatMessage } = useIntl();

  const { testStreamIndex } = useConnectorBuilderTestState();
  const [field, , helpers] = useField(`streams[${testStreamIndex}].schema`);

  const formattedRecords = useMemo(() => formatJson(page.records), [page.records]);
  const formattedRequest = useMemo(() => formatJson(page.request), [page.request]);
  const formattedResponse = useMemo(() => formatJson(page.response), [page.response]);
  const formattedSchema = useMemo(() => inferredSchema && formatJson(inferredSchema), [inferredSchema]);

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

  // TODO only do this as long as the schema panel is open (and probably debounce even then)
  const schemaDiff = getDiff(field.value, inferredSchema);
  console.log(schemaDiff);

  const parsedJSON = (() => {
    try {
      return JSON.parse(field.value);
    } catch {}
  })();

  return (
    <div className={classNames(className)}>
      <Tab.Group defaultIndex={defaultTabIndex}>
        <FlexContainer direction="column">
          <Tab.List className={styles.tabList}>
            {tabs.map((tab) => (
              <Tab className={styles.tab} key={tab.key}>
                {({ selected }) => (
                  <Text className={classNames(styles.tabTitle, { [styles.selected]: selected })}>{tab.title}</Text>
                )}
              </Tab>
            ))}
            {inferredSchema && (
              <Tab className={styles.tab}>
                {({ selected }) => (
                  <Text className={classNames(styles.tabTitle, { [styles.selected]: selected })}>
                    {formatMessage({ id: "connectorBuilder.schemaTab" })}
                  </Text>
                )}
              </Tab>
            )}
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
            {inferredSchema && (
              <Tab.Panel className={styles.tabPanel}>
                <FlexContainer direction="column">
                  {field.value !== formattedSchema && (
                    <FlexContainer>
                      <FlexItem grow>
                        <Button
                          full
                          variant="light"
                          disabled={field.value === formattedSchema}
                          onClick={() => {
                            helpers.setValue(formattedSchema);
                          }}
                        >
                          <FormattedMessage
                            id={
                              !field.value
                                ? "connectorBuilder.useSchemaButton"
                                : "connectorBuilder.overwriteSchemaButton"
                            }
                          />
                        </Button>
                      </FlexItem>
                      <FlexItem grow>
                        <Button
                          full
                          variant="light"
                          onClick={() => {
                            helpers.setValue(formatJson(merge({}, parsedJSON, inferredSchema)));
                          }}
                          disabled={formatJson(merge({}, parsedJSON, inferredSchema)) === field.value}
                        >
                          <FormattedMessage id="connectorBuilder.mergeSchemaButton" />
                        </Button>
                      </FlexItem>
                    </FlexContainer>
                  )}
                  <FlexItem>
                    {schemaDiff.split("\n").map((line, i) => {
                      const added = line[0] === "+";
                      const removed = line[0] === "-";
                      return (
                        <pre
                          className={classNames(
                            {
                              [styles.added]: added,
                              [styles.removed]: removed,
                            },
                            styles.diffLine
                          )}
                          key={i}
                        >
                          {added ? "+" : removed ? "-" : " "}
                          {line}
                        </pre>
                      );
                    })}
                  </FlexItem>
                </FlexContainer>
              </Tab.Panel>
            )}
          </Tab.Panels>
        </FlexContainer>
      </Tab.Group>
    </div>
  );
};
