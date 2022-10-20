import styles from "./ConnectorTestingPanel.module.scss";
import { StreamSelector } from "./StreamSelector";
import { TestControls } from "./TestControls";

export const ConnectorTestingPanel: React.FC<unknown> = () => {
  return (
    <div className={styles.container}>
      <StreamSelector />
      <TestControls
        onClickTest={() => {
          console.log("Test!");
        }}
      />
    </div>
  );
};
