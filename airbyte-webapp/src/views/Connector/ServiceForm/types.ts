import { ConnectionConfiguration } from "core/domain/connection";

type ServiceFormValues = {
  name: string;
  serviceType: string;
  connectionConfiguration: ConnectionConfiguration;
};

export type { ServiceFormValues };
