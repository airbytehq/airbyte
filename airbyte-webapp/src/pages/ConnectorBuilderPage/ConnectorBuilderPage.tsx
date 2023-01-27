import classnames from "classnames";
import { Formik } from "formik";
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
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import {
  ConnectorBuilderTestStateProvider,
  ConnectorBuilderFormStateProvider,
  useConnectorBuilderFormState,
  DEFAULT_JSON_MANIFEST_VALUES,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";
import { LandingPage } from "./LandingPage";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const noop = function () {};

const ConnectorBuilderPageInner: React.FC = React.memo(() => {
  const { builderFormValues, jsonManifest, editorView, setEditorView } = useConnectorBuilderFormState();
  const analyticsService = useAnalyticsService();

  useEffect(() => {
    analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.CONNECTOR_BUILDER_START, {
      actionDescription: "Connector Builder UI Opened",
    });
  }, [analyticsService]);

  const switchToUI = useCallback(() => setEditorView("ui"), [setEditorView]);
  const switchToYaml = useCallback(() => setEditorView("yaml"), [setEditorView]);

  const [showLandingPage, setShowLandingPage] = useState(
    isEqual(builderFormValues, DEFAULT_BUILDER_FORM_VALUES) && isEqual(jsonManifest, DEFAULT_JSON_MANIFEST_VALUES)
  );

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

export default ConnectorBuilderPage;
