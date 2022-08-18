import { screen, render } from "@testing-library/react";

import { TestWrapper } from "utils/testutils";

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

jest.mock("views/Connector/ServiceForm/components/Sections/auth/useOAuthFlowAdapter", () => {
  const useFormikOauthAdapter = () => {
    const done = false;
    const run = jest.fn();
    const loading = false;

    return { done, run, loading };
  };
  return { useFormikOauthAdapter };
});

//todo: typescript is making it weird to do a mockImplementation or mockReturnValueOnce...
jest.mock("views/Connector/ServiceForm/serviceFormContext", () => {
  const useServiceForm = () => {
    const hasAuthError = false;
    const selectedConnector = "abcde";
    const allowOAuthConnector = true;

    return { hasAuthError, selectedConnector, allowOAuthConnector };
  };
  return { useServiceForm };
});

test("it initially renders with correct message and no status message", () => {
  render(
    <TestWrapper>
      <AuthButton />
    </TestWrapper>
  );
  const button = screen.getByRole("button", { name: "Authenticate your account" });
  expect(button).toBeInTheDocument();

  const errorMessage = screen.queryByText(/Authentication required/i);
  expect(errorMessage).not.toBeInTheDocument();
});

test.todo("after successful authentication, it renders with correct message and success message", () => {
  //todo: typescript is making this hard to do
  mockedUseServiceForm.mockImplementation(() => {
    const useServiceForm = () => {
      const hasAuthError = true;
      const selectedConnector = "abcde";
      const allowOAuthConnector = true;

      return { hasAuthError, selectedConnector, allowOAuthConnector };
    };
    return { useServiceForm };
  });

  // expect();
});

test.todo("attempting to submit form with missing authentication shows error");
