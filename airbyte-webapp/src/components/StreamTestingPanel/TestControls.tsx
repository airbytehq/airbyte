interface TestControlsProps {
  onClickTest: () => void;
  className?: string;
}

export const TestControls: React.FC<TestControlsProps> = ({}) => {
  return <></>;
  // const { selectedStream, yamlIsValid } = useConnectorBuilderState();
  // const testButton = (
  //   <Button
  //     className={styles.testButton}
  //     size="sm"
  //     onClick={onClickTest}
  //     disabled={!yamlIsValid}
  //     icon={
  //       yamlIsValid ? (
  //         <div>
  //           <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
  //         </div>
  //       ) : (
  //         <FontAwesomeIcon icon={faWarning} />
  //       )
  //     }
  //   >
  //     <Text className={styles.testButtonText} size="sm" bold>
  //       <FormattedMessage id="connectorBuilder.testButton" />
  //     </Text>
  //   </Button>
  // );
  // return (
  //   <div className={classNames(className, styles.container)}>
  //     <ConfigMenu />
  //     <div className={styles.urlDisplay}>
  //       <Tooltip control={<Text size="lg">{selectedStream.url}</Text>}>{selectedStream.url}</Tooltip>
  //     </div>
  //     {yamlIsValid ? (
  //       testButton
  //     ) : (
  //       <Tooltip control={testButton}>
  //         <FormattedMessage id="connectorBuilder.invalidYamlTest" />
  //       </Tooltip>
  //     )}
  //   </div>
  // );
};
