import {
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
} from "@headlessui/react";
import styles from "./index.module.css";
import apiEndpointsDataRaw from "@site/src/data/api-endpoints-dereferenced.json";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { SourceConfiguration } from "../SourceConfiguration";
import { ApiEndpointsData, RequestBodyProperty } from "../SourceConfiguration/types";

const apiEndpointsData = apiEndpointsDataRaw as ApiEndpointsData;

interface SourceRequestSchemaProps {
  pageId: string;
}

export const SourceRequestSchema = ({ pageId }: SourceRequestSchemaProps) => {
  // Get endpoint data from the dereferenced API endpoints
  const endpointData = pageId ? apiEndpointsData[pageId] : null;
  const requestBodyProperties: RequestBodyProperty[] = endpointData?.requestBodyProperties || [];

  // Sort properties: required first, then optional
  const sortedProperties = [...requestBodyProperties].sort((a: RequestBodyProperty, b: RequestBodyProperty) => {
    if (a.required === b.required) return 0;
    return a.required ? -1 : 1;
  });

  return (
    <TabGroup>
      <TabList>
        <Tab className={`${styles.mimeTypeTab} ${styles.mimeTypeTab_active}`}>
          {" "}
          application/json
        </Tab>
      </TabList>
      <TabPanels>
        <TabPanel>
          <Disclosure defaultOpen={true}>
            <DisclosureButton className={styles.disclosureButton}>
              <FontAwesomeIcon icon={faChevronRight} />
              <h3 className={styles.summaryHeader}>
                Body
                <strong className={styles.required}>required</strong>
              </h3>
            </DisclosureButton>
            <DisclosurePanel className={styles.disclosurePanel}>
              <ul style={{ marginLeft: "1rem", listStyle: "none", padding: 0 }}>
                {sortedProperties &&
                  sortedProperties.length > 0 &&
                  sortedProperties.map((param: RequestBodyProperty) => {
                    return (
                      <div
                        key={param.name}
                        className="openapi-schema__list-item"
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                          }}
                        >
                          <span className="openapi-schema__container">
                            <strong className="openapi-schema__property">
                              {param.name}
                            </strong>
                            <span className="openapi-schema__name">
                             {param.type}
                            </span>
                          </span>
                          {param.required && (
                            <span className="openapi-schema__required">
                              required
                            </span>
                          )}
                        </div>
                        {param.description && (
                          <p
                            style={{
                              fontSize: "0.9rem",
                              color: "var(--ifm-color-emphasis-700)",
                              lineHeight: 1.4,
                              margin: "0.25rem 0",
                            }}
                          >
                            {param.description}
                          </p>
                        )}
                        {param.name === "configuration" && (
                          <SourceConfiguration endpointData={endpointData} />
                        )}
                      </div>
                    );
                  })}
              </ul>
            </DisclosurePanel>
          </Disclosure>
        </TabPanel>
      </TabPanels>
    </TabGroup>
  );
};

export default SourceRequestSchema;
