export enum StepType {
  INSTRUCTION = "instruction",
  CREATE_SOURCE = "create-source",
  CREATE_DESTINATION = "create-destination",
  SET_UP_CONNECTION = "set-up-connection",
  FINAL = "final",
}

// exp-speedy-connection
export interface ILocationState<Type> extends Omit<Location, "state"> {
  state: Type;
}
