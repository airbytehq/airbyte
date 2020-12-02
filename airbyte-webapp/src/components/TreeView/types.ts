export type INode = {
  value: string;
  label: string;
  hideCheckbox?: boolean;
  children?: Array<INode>;
};
