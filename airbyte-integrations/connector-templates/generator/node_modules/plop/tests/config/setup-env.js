beforeAll(() => {
  const originalWarn = console.warn;
  jest.spyOn(console, "warn").mockImplementation((...args) => {
    if (args[0] && args[0].includes && args[0].includes("deprecated")) {
      return;
    }
    originalWarn(...args);
  });
});

afterEach(() => {
  if (jest.isMockFunction(global.setTimeout)) {
    jest.useRealTimers();
  }
});

afterAll(() => {
  jest.restoreAllMocks();
});

jest.setTimeout(5000);
