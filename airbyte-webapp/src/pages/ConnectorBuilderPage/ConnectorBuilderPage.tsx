import classnames from "classnames";
import { Formik } from "formik";
import { useIntl } from "react-intl";

import { Builder } from "components/connectorBuilder/Builder/Builder";
import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import { builderFormValidationSchema } from "components/connectorBuilder/types";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import {
  ConnectorBuilderStateProvider,
  useConnectorBuilderState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

const ConnectorBuilderPageInner: React.FC = () => {
  const { formatMessage } = useIntl();
  const { builderFormValues, editorView, setEditorView } = useConnectorBuilderState();

  return (
    <Formik initialValues={builderFormValues} onSubmit={() => undefined} validationSchema={builderFormValidationSchema}>
      {({ values }) => (
        <ResizablePanels
          className={classnames({ [styles.gradientBg]: editorView === "yaml", [styles.solidBg]: editorView === "ui" })}
          firstPanel={{
            children: (
              <>
                {editorView === "yaml" ? (
                  <YamlEditor toggleYamlEditor={() => setEditorView("ui")} />
                ) : (
                  <Builder values={values} toggleYamlEditor={() => setEditorView("yaml")} />
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
      )}
    </Formik>
  );
};

export const ConnectorBuilderPage: React.FC = () => (
  <ConnectorBuilderStateProvider>
    <ConnectorBuilderPageInner />
  </ConnectorBuilderStateProvider>
);
