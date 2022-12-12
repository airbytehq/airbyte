export const useAppMonitoringService = () => {
  return {
    trackError: jest.fn(),
    trackAction: jest.fn(),
  };
};
