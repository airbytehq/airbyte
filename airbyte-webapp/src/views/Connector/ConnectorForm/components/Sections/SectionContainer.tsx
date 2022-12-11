import styles from "./SectionContainer.module.scss";

export const SectionContainer: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return <div className={styles.container}>{children}</div>;
};
