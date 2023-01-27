import classnames from "classnames";
import { Formik, useFormikContext } from "formik";
import { load, YAMLException } from "js-yaml";
import isEqual from "lodash/isEqual";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useIntl } from "react-intl";

import { Builder } from "components/connectorBuilder/Builder/Builder";
import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import {
  builderFormValidationSchema,
  BuilderFormValues,
  DEFAULT_BUILDER_FORM_VALUES,
} from "components/connectorBuilder/types";
import { useManifestToBuilderForm } from "components/connectorBuilder/useManifestToBuilderForm";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { Button } from "components/ui/Button";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useAnalyticsService } from "hooks/services/Analytics";
import {
  ConnectorBuilderTestStateProvider,
  ConnectorBuilderFormStateProvider,
  useConnectorBuilderFormState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const noop = function () {};

const ConnectorBuilderPageInner: React.FC = React.memo(() => {
  const { builderFormValues, editorView, setEditorView } = useConnectorBuilderFormState();
  const analyticsService = useAnalyticsService();

  useEffect(() => {
    analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.CONNECTOR_BUILDER_START, {
      actionDescription: "Connector Builder UI Opened",
    });
  }, [analyticsService]);

  const switchToUI = useCallback(() => setEditorView("ui"), [setEditorView]);
  const switchToYaml = useCallback(() => setEditorView("yaml"), [setEditorView]);

  const [showLandingPage, setShowLandingPage] = useState(isEqual(builderFormValues, DEFAULT_BUILDER_FORM_VALUES));

  const initialFormValues = useRef(builderFormValues);
  return useMemo(() => {
    return (
      <Formik
        initialValues={initialFormValues.current}
        validateOnBlur
        validateOnChange={false}
        validateOnMount={false}
        onSubmit={noop}
        validationSchema={builderFormValidationSchema}
      >
        {(props) => {
          if (showLandingPage) {
            return (
              <LandingPage
                setShowLandingPage={setShowLandingPage}
                switchToUI={switchToUI}
                switchToYaml={switchToYaml}
              />
            );
          }
          return (
            <Panels
              editorView={editorView}
              validateForm={props.validateForm}
              switchToUI={switchToUI}
              values={props.values}
              switchToYaml={switchToYaml}
            />
          );
        }}
      </Formik>
    );
  }, [editorView, showLandingPage, switchToUI, switchToYaml]);
});

export const ConnectorBuilderPage: React.FC = () => (
  <ConnectorBuilderFormStateProvider>
    <ConnectorBuilderTestStateProvider>
      <ConnectorBuilderPageInner />
    </ConnectorBuilderTestStateProvider>
  </ConnectorBuilderFormStateProvider>
);

const Panels = React.memo(
  ({
    editorView,
    switchToUI,
    switchToYaml,
    values,
    validateForm,
  }: {
    editorView: string;
    switchToUI: () => void;
    values: BuilderFormValues;
    switchToYaml: () => void;
    validateForm: () => void;
  }) => {
    const { formatMessage } = useIntl();
    return (
      <ResizablePanels
        className={classnames({ [styles.gradientBg]: editorView === "yaml", [styles.solidBg]: editorView === "ui" })}
        firstPanel={{
          children: (
            <>
              {editorView === "yaml" ? (
                <YamlEditor toggleYamlEditor={switchToUI} />
              ) : (
                <Builder values={values} validateForm={validateForm} toggleYamlEditor={switchToYaml} />
              )}
            </>
          ),
          className: styles.leftPanel,
          minWidth: 100,
        }}
        secondPanel={{
          children: <StreamTestingPanel />,
          className: styles.rightPanel,
          flex: 0.33,
          minWidth: 60,
          overlay: {
            displayThreshold: 325,
            header: formatMessage({ id: "connectorBuilder.testConnector" }),
            rotation: "counter-clockwise",
          },
        }}
      />
    );
  }
);

const LandingPage = React.memo(
  ({
    setShowLandingPage,
    switchToUI,
    switchToYaml,
  }: {
    setShowLandingPage: (value: boolean) => void;
    switchToUI: () => void;
    switchToYaml: () => void;
  }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { setJsonManifest, setYamlIsValid } = useConnectorBuilderFormState();
    const { convertToBuilderFormValues } = useManifestToBuilderForm();
    const { setValues } = useFormikContext<BuilderFormValues>();
    const [importLoading, setImportLoading] = useState(false);

    const handleYamlUpload = useCallback(
      async (yaml: string) => {
        try {
          let json;
          try {
            json = load(yaml) as ConnectorManifest;
          } catch (e) {
            if (e instanceof YAMLException) {
              console.log(`The YAML you provided is invalid! \nError: ${e.reason}\nLine number: ${e.mark.line}`);
            }
            return;
          }
          setYamlIsValid(true);

          let convertedFormValues;
          try {
            convertedFormValues = await convertToBuilderFormValues(json, DEFAULT_BUILDER_FORM_VALUES);
          } catch (e) {
            switchToYaml();
            setJsonManifest(json);
            setShowLandingPage(false);
            return;
          }

          switchToUI();
          setValues(convertedFormValues);
          setShowLandingPage(false);
        } finally {
          setImportLoading(false);
        }
      },
      [
        convertToBuilderFormValues,
        setJsonManifest,
        setShowLandingPage,
        setValues,
        setYamlIsValid,
        switchToUI,
        switchToYaml,
      ]
    );

    return (
      <div>
        <Text>Landing Page</Text>
        <input
          type="file"
          accept=".yml,.yaml"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={(uploadEvent) => {
            setImportLoading(true);
            const file = uploadEvent.target.files?.[0];
            const reader = new FileReader();
            reader.onload = (readerEvent) => {
              handleYamlUpload(readerEvent.target?.result as string);
            };
            if (file) {
              reader.readAsText(file);
            }
          }}
        />
        <Button onClick={() => fileInputRef.current?.click()} isLoading={importLoading}>
          Import YAML
        </Button>
        <Button
          onClick={() => {
            switchToUI();
            setShowLandingPage(false);
          }}
        >
          Start from scratch
        </Button>
      </div>
    );
  }
);

export default ConnectorBuilderPage;
