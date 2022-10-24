// import { FormattedMessage } from "react-intl";

// import { YamlEditor } from "components/YamlEditor";

// import styles from "./ConnectorBuilderPage.module.scss";

// import { ReflexSplitter } from "react-reflex";

import { ResizablePanels, Panel, Splitter } from "components/ui/ResizablePanels";

export const ConnectorBuilderPage: React.FC = () => {
  return (
    <ResizablePanels>
      <Panel flex={0.75} minWidth={500}>
        <div>👈 Left panel</div>
      </Panel>
      <Splitter />
      <Panel flex={0.25} minWidth={200}>
        <div>Right panel 👉</div>
      </Panel>
    </ResizablePanels>
  );
};
