import { AirbyteJSONSchema } from "core/jsonSchema";

type ConnectionConfiguration = unknown;

type ConnectionSpecification = AirbyteJSONSchema;

export type { ConnectionConfiguration, ConnectionSpecification };

export enum ConnectionNamespaceDefinition {
  Source = "source",
  Destination = "destination",
  CustomFormat = "customformat",
}

export enum ConnectionSchedule {
  Minutes = "minutes",
  Hours = "hours",
  Days = "days",
  Weeks = "weeks",
  Months = "months",
}

export type ScheduleProperties = {
  units: number;
  timeUnit: ConnectionSchedule;
};
