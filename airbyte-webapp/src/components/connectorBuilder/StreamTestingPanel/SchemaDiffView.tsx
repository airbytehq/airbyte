import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { diffJson, Change } from "diff";
import { useField } from "formik";
import merge from "lodash/merge";
import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useDebounce } from "react-use";

import { Button } from "components/ui/Button";
import { Callout } from "components/ui/Callout";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Tooltip } from "components/ui/Tooltip";

import { Action, Namespace } from "core/analytics";
import { StreamReadInferredSchema } from "core/request/ConnectorBuilderClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import {
  useConnectorBuilderFormState,
  useConnectorBuilderTestState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./SchemaDiffView.module.scss";
import { formatJson } from "../utils";

interface SchemaDiffViewProps {
  inferredSchema: StreamReadInferredSchema;
}

interface Diff {
  /**
   * List of changes from current schema to detected schema
   */
  changes: Change[];
  /**
   * Formatted merged schema if merging in the detected schema changes the existing schema
   */
  mergedSchema?: string;
  /**
   * Flag if overriding the existing schema with the new schema would lose information
   */
  lossyOverride: boolean;
}

function getDiff(existingSchema: string | undefined, detectedSchema: object): Diff {
  if (!existingSchema) {
    return { changes: [], lossyOverride: false };
  }
  try {
    const existingObject = existingSchema ? JSON.parse(existingSchema) : undefined;
    const mergedSchemaPreferExisting = formatJson(merge({}, detectedSchema, existingObject), true);
    const changes = diffJson(existingObject, detectedSchema);
    // The override would be lossy if lines are removed in the diff
    const lossyOverride = changes.some((change) => change.removed);
    return {
      changes,
      mergedSchema: mergedSchemaPreferExisting !== existingSchema ? mergedSchemaPreferExisting : undefined,
      lossyOverride,
    };
  } catch {
    return { changes: [], lossyOverride: true };
  }
}

export const SchemaDiffView: React.FC<SchemaDiffViewProps> = ({ inferredSchema }) => {
  const analyticsService = useAnalyticsService();
  const { streams, testStreamIndex } = useConnectorBuilderTestState();
  const { editorView } = useConnectorBuilderFormState();
  const [field, , helpers] = useField(`streams[${testStreamIndex}].schema`);
  const formattedSchema = useMemo(() => inferredSchema && formatJson(inferredSchema, true), [inferredSchema]);

  const [schemaDiff, setSchemaDiff] = useState<Diff>(() =>
    editorView === "ui" ? getDiff(field.value, inferredSchema) : { changes: [], lossyOverride: false }
  );

  useDebounce(
    () => {
      if (editorView === "ui") {
        setSchemaDiff(getDiff(field.value, inferredSchema));
      }
    },
    250,
    [field.value, inferredSchema, editorView]
  );

  return (
    <FlexContainer direction="column">
      {editorView === "ui" && field.value && field.value !== formattedSchema && (
        <Callout className={styles.infoBox}>
          <FontAwesomeIcon icon={faWarning} size="lg" />
          <FlexItem grow>
            <FlexContainer direction="column">
              <FormattedMessage id="connectorBuilder.differentSchemaDescription" />
              <FlexContainer>
                <FlexItem grow>
                  <Button
                    full
                    variant="dark"
                    disabled={field.value === formattedSchema}
                    onClick={() => {
                      helpers.setValue(formattedSchema);
                      analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.OVERWRITE_SCHEMA, {
                        actionDescription: "Declared schema overwritten by detected schema",
                        stream_name: streams[testStreamIndex]?.name,
                      });
                    }}
                  >
                    <FormattedMessage
                      id={
                        schemaDiff.lossyOverride
                          ? "connectorBuilder.overwriteSchemaButton"
                          : "connectorBuilder.useSchemaButton"
                      }
                    />
                  </Button>
                </FlexItem>
                {schemaDiff.mergedSchema && schemaDiff.lossyOverride && (
                  <FlexItem grow>
                    <Tooltip
                      control={
                        <Button
                          full
                          variant="dark"
                          onClick={() => {
                            helpers.setValue(schemaDiff.mergedSchema);
                            analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.MERGE_SCHEMA, {
                              actionDescription: "Detected and Declared schemas merged to update declared schema",
                              stream_name: streams[testStreamIndex]?.name,
                            });
                          }}
                        >
                          <FormattedMessage id="connectorBuilder.mergeSchemaButton" />
                        </Button>
                      }
                    >
                      <FormattedMessage id="connectorBuilder.mergeSchemaTooltip" />
                    </Tooltip>
                  </FlexItem>
                )}
              </FlexContainer>
            </FlexContainer>
          </FlexItem>
        </Callout>
      )}
      {editorView === "ui" && !field.value && (
        <Button
          full
          variant="secondary"
          onClick={() => {
            helpers.setValue(formattedSchema);
            analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.OVERWRITE_SCHEMA, {
              actionDescription: "Declared schema overwritten by detected schema",
              stream_name: streams[testStreamIndex]?.name,
            });
          }}
        >
          <FormattedMessage id="connectorBuilder.useSchemaButton" />
        </Button>
      )}
      <FlexItem>
        {editorView === "yaml" || !schemaDiff.changes.length ? (
          <pre className={styles.diffLine}>
            {formattedSchema
              .split("\n")
              .map((line) => ` ${line}`)
              .join("\n")}
          </pre>
        ) : (
          schemaDiff.changes.map((change, changeIndex) => (
            <pre
              className={classNames(
                {
                  [styles.added]: change.added,
                  [styles.removed]: change.removed,
                },
                styles.diffLine
              )}
              key={changeIndex}
            >
              {change.value
                .split("\n")
                .map((line) => (line === "" ? undefined : `${change.added ? "+" : change.removed ? "-" : " "}${line}`))
                .filter(Boolean)
                .join("\n")}
            </pre>
          ))
        )}
      </FlexItem>
    </FlexContainer>
  );
};
