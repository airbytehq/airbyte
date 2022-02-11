import { useEffect, useRef } from "react";

export function useInitService<T extends new (...args: any) => any>(
  f: () => InstanceType<T>,
  deps: ConstructorParameters<T>
): InstanceType<T> {
  const service = useRef<InstanceType<T>>(f());

  useEffect(() => {
    service.current = f();
  }, deps);

  return service.current;
}
