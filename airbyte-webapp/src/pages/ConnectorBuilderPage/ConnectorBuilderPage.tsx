import classnames from "classnames";
import { Formik } from "formik";
import React, { useCallback } from "react";
import { useIntl } from "react-intl";

import { Builder } from "components/connectorBuilder/Builder/Builder";
import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import { builderFormValidationSchema, BuilderFormValues } from "components/connectorBuilder/types";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import {
  ConnectorBuilderAPIProvider,
  ConnectorBuilderStateProvider,
  useConnectorBuilderState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

const ConnectorBuilderPageInner: React.FC = React.memo(() => {
  const { builderFormValues, editorView, setEditorView } = useConnectorBuilderState();

  const switchToUI = useCallback(() => setEditorView("ui"), [setEditorView]);
  const switchToYaml = useCallback(() => setEditorView("yaml"), [setEditorView]);

  return (
    <Formik initialValues={builderFormValues} onSubmit={() => undefined} validationSchema={builderFormValidationSchema}>
      {({ values }) => (
        <Panels editorView={editorView} switchToUI={switchToUI} values={values} switchToYaml={switchToYaml} />
      )}
    </Formik>
  );
});

export const ConnectorBuilderPage: React.FC = () => (
  <ConnectorBuilderStateProvider>
    <ConnectorBuilderAPIProvider>
      <ConnectorBuilderPageInner />
    </ConnectorBuilderAPIProvider>
  </ConnectorBuilderStateProvider>
);

const Panels = React.memo(
  ({
    editorView,
    switchToUI,
    switchToYaml,
    values,
  }: {
    editorView: string;
    switchToUI: () => void;
    values: BuilderFormValues;
    switchToYaml: () => void;
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
                <Builder values={values} toggleYamlEditor={switchToYaml} />
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
