import { useEffect, useRef } from "react";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useInitService<T extends new (...args: unknown[]) => any>(
  f: () => InstanceType<T>,
  deps: ConstructorParameters<T>
): InstanceType<T> {
  const service = useRef<InstanceType<T>>(f());

  useEffect(() => {
    service.current = f();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return service.current;
}
