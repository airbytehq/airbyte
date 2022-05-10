import type { Location } from "react-router-dom";

export function hasFromState(state: unknown): state is { from: Location } {
  return typeof state === "object" && state !== null && "from" in state;
}
