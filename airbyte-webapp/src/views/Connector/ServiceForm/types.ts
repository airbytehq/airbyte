export type ServiceFormValues<T = unknown> = {
  name: string;
  serviceType: string;
  connectionConfiguration: T;
};
