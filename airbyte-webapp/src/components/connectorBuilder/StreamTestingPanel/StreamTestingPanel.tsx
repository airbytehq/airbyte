import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import { ValidationError } from "yup";

import { Heading } from "components/ui/Heading";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { jsonSchemaToFormBlock } from "core/form/schemaToFormBlock";
import { buildYupFormForJsonSchema } from "core/form/schemaToYup";
import { StreamReadRequestBodyConfig } from "core/request/ConnectorBuilderClient";
import { Spec } from "core/request/ConnectorManifest";
import {
  useConnectorBuilderTestState,
  useConnectorBuilderFormState,
} from "services/connectorBuilder/ConnectorBuilderStateService";
import { links } from "utils/links";

import { ConfigMenu } from "./ConfigMenu";
import { StreamSelector } from "./StreamSelector";
import { StreamTester } from "./StreamTester";
import styles from "./StreamTestingPanel.module.scss";

const EMPTY_SCHEMA = {};

function useTestInputJsonErrors(testInputJson: StreamReadRequestBodyConfig, spec?: Spec): number {
  return useMemo(() => {
    try {
      const jsonSchema = spec && spec.connection_specification ? spec.connection_specification : EMPTY_SCHEMA;
      const formFields = jsonSchemaToFormBlock(jsonSchema);
      const validationSchema = buildYupFormForJsonSchema(jsonSchema, formFields);
      validationSchema.validateSync(testInputJson, { abortEarly: false });
      return 0;
    } catch (e) {
      if (ValidationError.isError(e)) {
        return e.errors.length;
      }
      return 1;
    }
  }, [testInputJson, spec]);
}

export const StreamTestingPanel: React.FC<unknown> = () => {
  const [isTestInputOpen, setTestInputOpen] = useState(false);
  const { jsonManifest, yamlEditorIsMounted } = useConnectorBuilderFormState();
  const { testInputJson, streamListErrorMessage } = useConnectorBuilderTestState();

  const testInputJsonErrors = useTestInputJsonErrors(testInputJson, jsonManifest.spec);

  if (!yamlEditorIsMounted) {
    return (
      <div className={styles.loadingSpinner}>
        <Spinner />
      </div>
    );
  }

  const hasStreams = jsonManifest.streams?.length > 0;

  return (
    <div className={styles.container}>
      <ConfigMenu
        className={styles.configButton}
        testInputJsonErrors={testInputJsonErrors}
        isOpen={isTestInputOpen}
        setIsOpen={setTestInputOpen}
      />
      {!hasStreams && (
        <div className={styles.addStreamMessage}>
          <Heading as="h2" className={styles.addStreamHeading}>
            <FormattedMessage id="connectorBuilder.noStreamsMessage" />
          </Heading>
          <img className={styles.logo} alt="" src="/images/octavia/pointing.svg" width={102} />
        </div>
      )}
      {hasStreams && streamListErrorMessage === undefined && (
        <div className={styles.selectAndTestContainer}>
          <StreamSelector className={styles.streamSelector} />
          <StreamTester hasTestInputJsonErrors={testInputJsonErrors > 0} setTestInputOpen={setTestInputOpen} />
        </div>
      )}
      {hasStreams && streamListErrorMessage !== undefined && (
        <div className={styles.listErrorDisplay}>
          <Text>
            <FormattedMessage id="connectorBuilder.couldNotDetectStreams" />
          </Text>
          <Text bold>{streamListErrorMessage}</Text>
          <Text>
            <FormattedMessage
              id="connectorBuilder.ensureProperYaml"
              values={{
                a: (node: React.ReactNode) => (
                  <a href={links.lowCodeYamlDescription} target="_blank" rel="noreferrer">
                    {node}
                  </a>
                ),
              }}
            />
          </Text>
        </div>
      )}
    </div>
  );
};
