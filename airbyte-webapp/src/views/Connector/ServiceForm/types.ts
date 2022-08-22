// TODO: This needs to be converted to interface, but has int he current state a problem with index signatures
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
export type ServiceFormValues<T = unknown> = {
  name: string;
  serviceType: string;
  connectionConfiguration: T;
};
