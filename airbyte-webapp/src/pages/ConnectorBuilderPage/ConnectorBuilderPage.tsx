import classnames from "classnames";
import { Formik } from "formik";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { useIntl } from "react-intl";

import { Builder } from "components/connectorBuilder/Builder/Builder";
import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import { builderFormValidationSchema, BuilderFormValues } from "components/connectorBuilder/types";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import { Action, Namespace } from "core/analytics";
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

  const initialFormValues = useRef(builderFormValues);
  return useMemo(
    () => (
      <Formik
        initialValues={initialFormValues.current}
        validateOnBlur
        validateOnChange={false}
        validateOnMount={false}
        onSubmit={noop}
        validationSchema={builderFormValidationSchema}
      >
        {(props) => {
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
    ),
    [editorView, switchToUI, switchToYaml]
  );
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
