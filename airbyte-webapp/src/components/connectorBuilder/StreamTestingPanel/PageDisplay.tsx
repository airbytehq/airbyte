import { Tab } from "@headlessui/react";
import classNames from "classnames";
import { useMemo } from "react";
import { useIntl } from "react-intl";

import { Text } from "components/ui/Text";

import { StreamReadSlicesItemPagesItem } from "core/request/ConnectorBuilderClient";

import styles from "./PageDisplay.module.scss";
import { formatJson } from "./utils";

interface PageDisplayProps {
  page: StreamReadSlicesItemPagesItem;
  className?: string;
}

interface TabData {
  title: string;
  key: string;
  content: string;
}

export const PageDisplay: React.FC<PageDisplayProps> = ({ page, className }) => {
  const { formatMessage } = useIntl();

  const formattedRecords = useMemo(() => formatJson(page.records), [page.records]);
  const formattedRequest = useMemo(() => formatJson(page.request), [page.request]);
  const formattedResponse = useMemo(() => formatJson(page.response), [page.response]);

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
              <pre>{tab.content}</pre>
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};
