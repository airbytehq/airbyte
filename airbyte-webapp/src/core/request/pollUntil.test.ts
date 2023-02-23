import { pollUntil } from "./pollUntil";

// a toy promise that can be polled for a specific response
const fourZerosAndThenSeven = () => {
  let _callCount = 0;
  return () => Promise.resolve([0, 0, 0, 0, 7][_callCount++]);
};
// eslint-disable-next-line
const truthyResponse = (x: any) => !!x;

describe("pollUntil", () => {
  describe("when maxTimeoutMs is not provided", () => {
    it("calls the provided apiFn until condition returns true and resolves to its final return value", () => {
      const pollableFn = fourZerosAndThenSeven();

      return expect(pollUntil(pollableFn, truthyResponse, { intervalMs: 1 })).resolves.toBe(7);
    });
  });

  describe("when condition returns true before maxTimeoutMs is reached", () => {
    it("calls the provided apiFn until condition returns true and resolves to its final return value", () => {
      const pollableFn = fourZerosAndThenSeven();

      return expect(pollUntil(pollableFn, truthyResponse, { intervalMs: 1, maxTimeoutMs: 100 })).resolves.toBe(7);
    });
  });

  describe("when maxTimeoutMs is reached before condition returns true", () => {
    it("resolves to false", () => {
      const pollableFn = fourZerosAndThenSeven();

      return expect(pollUntil(pollableFn, truthyResponse, { intervalMs: 100, maxTimeoutMs: 1 })).resolves.toBe(false);
    });

    // Because the timing of the polling depends on both the provided `intervalMs` and the
    // execution time of `apiFn`, the timing of polling iterations isn't entirely
    // deterministic; it's precise enough for its job, but it's difficult to make precise
    // test assertions about polling behavior without long intervalMs/maxTimeoutMs bogging
    // down the test suite.
    it("calls its apiFn arg no more than (maxTimeoutMs / intervalMs) times", async () => {
      let _callCount = 0;
      let lastCalledValue = 999;
      const pollableFn = () =>
        Promise.resolve([1, 2, 3, 4, 5][_callCount++]).then((val) => {
          lastCalledValue = val;
          return val;
        });

      await pollUntil(pollableFn, (_) => false, { intervalMs: 20, maxTimeoutMs: 78 });

      // In theory, this is what just happened:
      // | time elapsed | value (source)  |
      // |--------------+-----------------|
      // |          0ms | 1 (poll)        |
      // |         20ms | 2 (poll)        |
      // |         40ms | 3 (poll)        |
      // |         60ms | 4 (poll)        |
      // |         78ms | false (timeout) |
      //
      // In practice, since the polling intervalMs isn't started until after `apiFn`
      // resolves to a value, the actual call counts are slightly nondeterministic. We
      // could ignore that fact with a slow enough intervalMs, but who wants slow tests?
      expect(lastCalledValue > 2).toBe(true);
      expect(lastCalledValue <= 4).toBe(true);
    });
  });
});
