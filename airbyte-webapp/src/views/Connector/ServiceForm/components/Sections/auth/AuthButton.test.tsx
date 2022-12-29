import { screen, render } from "@testing-library/react";
import { TestWrapper } from "test-utils/testutils";

import { useFormikOauthAdapter } from "views/Connector/ServiceForm/components/Sections/auth/useOauthFlowAdapter";
import { useServiceForm } from "views/Connector/ServiceForm/serviceFormContext";
import { useAuthentication } from "views/Connector/ServiceForm/useAuthentication";

import { AuthButton } from "./AuthButton";
jest.setTimeout(10000);

jest.mock("formik", () => {
  const useFormikContext = () => {
    const values = {};
    const submitCount = 0;
    return { values, submitCount };
  };

  return { useFormikContext };
});

/**
 * Mock services to reuse multiple times with different values:
 * 1. mock the service
 * 2. cast the type as shown below.  `as unknown` is required to get the typing to play nice as there isn't crossover
 *    Partial is optional, but required if you do not want to mock the entire object
 *
 * Then, can implement in tests using useWhateverServiceYouMocked.mockImplementationOnce or useWhateverServiceYouMocked.mockImplementation
 */

jest.mock("views/Connector/ServiceForm/components/Sections/auth/useOauthFlowAdapter");
const mockUseFormikOauthAdapter = useFormikOauthAdapter as unknown as jest.Mock<Partial<typeof useFormikOauthAdapter>>;
const baseUseFormikOauthAdapterValues = {
  run: jest.fn(),
  loading: false,
};

jest.mock("views/Connector/ServiceForm/serviceFormContext");
const mockUseServiceForm = useServiceForm as unknown as jest.Mock<Partial<typeof useServiceForm>>;
const baseUseServiceFormValues = {
  selectedConnector: "abcde",
  allowOAuthConnector: true,
  selectedService: undefined,
};

jest.mock("views/Connector/ServiceForm/useAuthentication");
const mockUseAuthentication = useAuthentication as unknown as jest.Mock<Partial<typeof useAuthentication>>;

describe("auth button", () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockUseAuthentication.mockReturnValue({ hiddenAuthFieldErrors: {} });
  });

  it("initially renders with correct message and no status message", () => {
    // no auth errors
    mockUseServiceForm.mockImplementationOnce(() => {
      const { selectedConnector, selectedService } = baseUseServiceFormValues;

      return { selectedConnector, selectedService };
    });

    // not done
    mockUseFormikOauthAdapter.mockImplementationOnce(() => {
      const done = false;
      const { run, loading } = baseUseFormikOauthAdapterValues;

      return { done, run, loading };
    });

    render(
      <TestWrapper>
        <AuthButton />
      </TestWrapper>
    );

    // correct button text
    const button = screen.getByRole("button", { name: "Authenticate your account" });
    expect(button).toBeInTheDocument();

    // no error message
    const errorMessage = screen.queryByText(/Authentication required/i);
    expect(errorMessage).not.toBeInTheDocument();

    // no success message
    const successMessage = screen.queryByText(/Authentication succeeded/i);
    expect(successMessage).not.toBeInTheDocument();
  });

  it("after successful authentication, it renders with correct message and success message", () => {
    // no auth errors
    mockUseServiceForm.mockImplementationOnce(() => {
      const { selectedConnector, selectedService } = baseUseServiceFormValues;

      return { selectedConnector, selectedService };
    });

    // done
    mockUseFormikOauthAdapter.mockImplementationOnce(() => {
      const done = true;
      const { run, loading } = baseUseFormikOauthAdapterValues;

      return { done, run, loading, hasRun: done };
    });

    render(
      <TestWrapper>
        <AuthButton />
      </TestWrapper>
    );

    // correct button text
    const button = screen.getByRole("button", { name: "Re-authenticate" });
    expect(button).toBeInTheDocument();

    // success message
    const successMessage = screen.getByText(/Authentication succeeded/i);
    expect(successMessage).toBeInTheDocument();
  });

  it("renders an error if there are any auth fields with empty values", () => {
    // auth errors
    mockUseAuthentication.mockReturnValue({ hiddenAuthFieldErrors: { field: "form.empty.error" } });

    mockUseServiceForm.mockImplementationOnce(() => {
      const { selectedConnector, selectedService } = baseUseServiceFormValues;

      return { selectedConnector, selectedService };
    });

    // not done
    mockUseFormikOauthAdapter.mockImplementationOnce(() => {
      const done = false;
      const { run, loading } = baseUseFormikOauthAdapterValues;

      return { done, run, loading };
    });

    render(
      <TestWrapper>
        <AuthButton />
      </TestWrapper>
    );

    // correct button
    const button = screen.getByRole("button", { name: "Authenticate your account" });
    expect(button).toBeInTheDocument();

    // error message
    const errorMessage = screen.getByText(/Authentication required/i);
    expect(errorMessage).toBeInTheDocument();
  });
});
