export type INode = {
  value: string;
  label: string;
  hideCheckbox?: boolean;
  dataType?: string;
  cleanedName?: string;
  children?: Array<INode>;
  supportedSyncModes?: string[];
  syncMode?: string;
};
