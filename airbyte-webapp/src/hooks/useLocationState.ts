import { useLocation } from "react-router-dom";

interface ILocationState<T> extends Omit<Location, "state"> {
  state: T;
}

export const useLocationState = <T>(): T => {
  const location = useLocation() as unknown as ILocationState<T>;
  return location.state;
};
