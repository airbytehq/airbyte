import React from "react";
import {
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
} from "@headlessui/react";
import styles from "./index.module.css";
import apiEndpointsDataRaw from "@site/src/data/api-endpoints-dereferenced.json";
import { ApiEndpointsData, ResponseBodyProperty } from "../SourceConfiguration/types";
import { SourceConfiguration } from "../SourceConfiguration";
import Markdown from "@theme/Markdown";
import Details from "@theme/Details";

const apiEndpointsData = apiEndpointsDataRaw as ApiEndpointsData;

interface SourceResponseSchemaProps {
  pageId: string;
}

// Helper to determine status code category (2xx, 4xx, etc.) for ordering
const getStatusCodeCategory = (code: string): number => {
  const num = parseInt(code, 10);
  return Math.floor(num / 100);
};

// Sort status codes: 2xx first, then 4xx, 5xx, etc.
const sortStatusCodes = (codes: string[]): string[] => {
  return codes.sort((a, b) => {
    const catA = getStatusCodeCategory(a);
    const catB = getStatusCodeCategory(b);
    if (catA !== catB) return catA - catB;
    return parseInt(a, 10) - parseInt(b, 10);
  });
};

// Get human-readable status code text
function getStatusCodeText(code: string): string {
  const statusTexts: Record<string, string> = {
    "200": "OK",
    "201": "Created",
    "204": "No Content",
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "409": "Conflict",
    "422": "Unprocessable Entity",
    "500": "Internal Server Error",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
  };
  return statusTexts[code] || "Response";
}

// Helper to get status code color class
function getStatusCodeColorClass(code: string): string {
  const num = parseInt(code, 10);
  if (num >= 200 && num < 300) return "openapi-badge__success"; // 2xx - green
  if (num >= 300 && num < 400) return "openapi-badge__redirect"; // 3xx - blue
  if (num >= 400 && num < 500) return "openapi-badge__error"; // 4xx - red
  if (num >= 500) return "openapi-badge__error"; // 5xx - red
  return "openapi-badge__info"; // fallback
}

const renderBodyProperties = (properties: ResponseBodyProperty[], endpointData: any) => (
  <ul style={{ marginLeft: "1rem", listStyle: "none", padding: 0 }}>
    {properties &&
      properties.length > 0 &&
      properties.map((param: ResponseBodyProperty) => {
        return (
          <div key={param.name} className="openapi-schema__list-item">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span className="openapi-schema__container">
                <strong className="openapi-schema__property">{param.name}</strong>
                <span className="openapi-schema__name">{param.type}</span>
              </span>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                {param.required && <span className="openapi-schema__required">required</span>}
                {param.readOnly && <span className={styles.propertyBadge_readonly}>read-only</span>}
              </div>
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
);

export const SourceResponseSchema = ({ pageId }: SourceResponseSchemaProps) => {
  // Get endpoint data from the dereferenced API endpoints
  const endpointData = pageId ? apiEndpointsData[pageId] : null;
  const responsesByStatus = endpointData?.responsesByStatus || {};

  // Get sorted status codes
  const statusCodes = sortStatusCodes(Object.keys(responsesByStatus));

  if (statusCodes.length === 0) {
    return null;
  }

  // State to track selected status code
  const [selectedStatusIndex, setSelectedStatusIndex] = React.useState(0);

  return (
    <div className={styles.responseSchema}>
      {/* Responses Header and Status Code Tabs */}
      <div className={styles.responsesHeaderContainer}>
        <h2>Responses</h2>
        <div className={styles.statusCodePills}>
          {statusCodes.map((code: string, index: number) => {
            const isSuccess = parseInt(code) >= 200 && parseInt(code) < 300;
            return (
              <button
                key={code}
                onClick={() => setSelectedStatusIndex(index)}
                className={`${styles.statusCodeBadge} ${
                  selectedStatusIndex === index ? styles.statusCodeBadge_active : ""
                } ${isSuccess ? styles.statusCodeBadge_success : styles.statusCodeBadge_error}`}
              >
                {code}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tabbed Content for MIME Type and Status Codes */}
      <div className={styles.statusCodePanels}>
        {statusCodes.map((code: string, index: number) => {
          if (index !== selectedStatusIndex) return null;

          const response = responsesByStatus[code];
          const statusProperties: ResponseBodyProperty[] = response?.properties || [];

          // Sort properties: required first, then optional
          const sortedProperties = [...statusProperties].sort((a: ResponseBodyProperty, b: ResponseBodyProperty) => {
            if (a.required === b.required) return 0;
            return a.required ? -1 : 1;
          });

          return (
            <div key={code}>
              {/* Response Description */}
              {response.description && (
                <div className={styles.responseDescription}>
                  <Markdown>{response.description}</Markdown>
                </div>
              )}

              {/* MIME Type and Content Tabs */}
              {(response.examples?.length > 0 || statusProperties.length > 0) && (
                <TabGroup>
                  <TabList>
                    <Tab className={`${styles.mimeTypeTab} ${styles.mimeTypeTab_active}`}>
                      application/json
                    </Tab>
                  </TabList>
                  <TabPanels>
                    <TabPanel>
                      {/* Schema and Examples Tabs */}
                      <TabGroup>
                        <TabList>
                          {statusProperties.length > 0 && (
                            <Tab className={styles.contentTypeTab}>Schema</Tab>
                          )}
                          {response.examples && response.examples.length > 0 && (
                            response.examples.map((example: any) => (
                              <Tab key={example.name} className={styles.contentTypeTab}>
                                {example.name}
                              </Tab>
                            ))
                          )}
                        </TabList>
                        <TabPanels>
                          {/* Schema Panel */}
                          {statusProperties.length > 0 && (
                            <TabPanel>
                              <Details
                                className="openapi-markdown__details response"
                                data-collapsed={false}
                                open={true}
                                style={{
                                  textAlign: "left",
                                }}
                                summary={
                                  <summary
                                    style={{
                                      cursor: "pointer",
                                      userSelect: "none",
                                      marginBottom: "0",
                                    }}
                                  >
                                    <strong style={{ color: "var(--ifm-color-content)" }}>
                                      Schema
                                    </strong>
                                  </summary>
                                }
                              >
                                <div style={{ marginLeft: "1rem", textAlign: "left" }}>
                                  {renderBodyProperties(sortedProperties, endpointData)}
                                </div>
                              </Details>
                            </TabPanel>
                          )}

                          {/* Example Panels */}
                          {response.examples && response.examples.length > 0 && (
                            response.examples.map((example: any) => (
                              <TabPanel key={example.name}>
                                <pre style={{ marginLeft: "1rem", textAlign: "left" }}>
                                  <code>{JSON.stringify(example.value, null, 2)}</code>
                                </pre>
                              </TabPanel>
                            ))
                          )}
                        </TabPanels>
                      </TabGroup>
                    </TabPanel>
                  </TabPanels>
                </TabGroup>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SourceResponseSchema;
