import { useState } from "react";
import ReactJson from "react-json-view";
import { match, P } from "ts-pattern";

import { LoadingPage } from "components";
import { DropDown } from "components/ui/DropDown";
import { Text } from "components/ui/Text";

import { SourceDefinitionRead } from "core/request/AirbyteClient";

import styles from "./SchemaViewer.module.scss";
import { useGetSourceSchema } from "./useGetSourceSchema";
import { ResourceNotAvailable } from "../ResourceNotAvailable";
const isString = (x: unknown): x is string => typeof x === "string";
const isArray = (x: unknown): x is unknown[] => Array.isArray(x);

export const SchemaViewer = ({ sourceDefinition }: { sourceDefinition: SourceDefinitionRead }) => {
  const query = useGetSourceSchema({ sourceDefinitionId: sourceDefinition.sourceDefinitionId });
  console.log(query);
  const [isSchemaRequested, setIsSchemaRequested] = useState(false);

  const streams = query.data ? Object.keys(query.data).map((key) => ({ label: key, value: key })) : [];
  const [stream, setStream] = useState(streams[0]?.value ?? "");

  return match(query)
    .with({ status: "loading" }, () => (
      <div className={styles.loadingContainer}>
        <LoadingPage />
      </div>
    ))
    .with({ status: "error" }, () => (
      <ResourceNotAvailable activeTab="schema" setRequested={setIsSchemaRequested} isRequested={isSchemaRequested} />
    ))
    .with({ status: "success", data: P.not(P.nullish) }, ({ data }) => {
      const streamProperties = data[stream] ? data[stream].properties : {};
      return (
        <div style={{ padding: "20px" }}>
          <div className={styles.dropdownContainer}>
            <Text bold>Streams:</Text>

            <DropDown
              className={styles.streamDropdown}
              options={streams}
              value={stream}
              onChange={(option) => setStream(option.value)}
            />
          </div>
          <div style={{ minHeight: "100vh", marginTop: "20px" }}>
            {stream &&
              Object.keys(streamProperties).map((key) => {
                return (
                  <div key={key} className={styles.propertyContainer}>
                    <div className={styles.propertyHeader}>
                      <div className={styles.separator} />
                      <Text className={styles.propertyText} bold>
                        {key}
                      </Text>
                      <code>
                        {match(streamProperties[key].type)
                          .with(P.when(isString), () => streamProperties[key].type)
                          .with(P.when(isArray), () => streamProperties[key].type.join(" | "))
                          .otherwise(() => null)}
                      </code>
                    </div>
                    {streamProperties[key].example && (
                      <div className={styles.exampleContainer}>
                        <Text size="sm">Example: </Text>
                        {match(streamProperties[key].type)
                          .with(
                            P.when((t) => isArray(t) && (t.includes("object") || t.includes("array"))),
                            () => (
                              <ReactJson
                                name={false}
                                src={streamProperties[key].example}
                                enableClipboard={false}
                                displayDataTypes={false}
                                quotesOnKeys={false}
                                theme="grayscale:inverted"
                                style={{ backgroundColor: "#f8f8fa", padding: "3px 5px" }}
                              />
                            )
                          )
                          .otherwise(() => (
                            <code className={styles.propertyExample}>
                              {JSON.stringify(streamProperties[key].example)}
                            </code>
                          ))}
                      </div>
                    )}
                    {!streamProperties[key].example &&
                      match(streamProperties[key].type)
                        .with(
                          P.when((t) => isArray(t) && (t.includes("object") || t.includes("array"))),
                          () => (
                            <div className={styles.exampleContainer}>
                              <ReactJson
                                name={false}
                                src={streamProperties[key].properties}
                                enableClipboard={false}
                                theme="grayscale:inverted"
                                style={{ backgroundColor: "#f8f8fa", padding: "3px 5px" }}
                              />
                            </div>
                          )
                        )
                        .otherwise(() => null)}
                  </div>
                );
              })}
          </div>
        </div>
      );
    })
    .otherwise(() => null);
};
