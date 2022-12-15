import { render, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffectOnce } from "react-use";
import { useMockIntersectionObserver } from "test-utils/testutils";

import { ModalServiceProvider, useModalService } from "./ModalService";
import { ModalResult } from "./types";

const TestComponent: React.FC<{ onModalResult?: (result: ModalResult<unknown>) => void }> = ({ onModalResult }) => {
  const { openModal } = useModalService();
  useEffectOnce(() => {
    openModal({
      title: "Test Modal Title",
      content: ({ onCancel, onClose }) => (
        <div data-testid="testModalContent">
          <button onClick={onCancel} data-testid="cancel">
            Cancel
          </button>
          <button onClick={() => onClose("reason1")} data-testid="close-reason1">
            Close Reason 1
          </button>
          <button onClick={() => onClose("reason2")} data-testid="close-reason2">
            Close Reason 2
          </button>
        </div>
      ),
    }).then(onModalResult);
  });
  return null;
};

const renderModal = (resultCallback?: (reason: unknown) => void) => {
  return render(
    <ModalServiceProvider>
      <TestComponent onModalResult={resultCallback} />
    </ModalServiceProvider>
  );
};

describe("ModalService", () => {
  beforeEach(() => {
    // IntersectionObserver isn't available in test environment but is used by headless-ui dialog
    useMockIntersectionObserver();
  });
  it("should open a modal on openModal", () => {
    const rendered = renderModal();

    expect(rendered.getByText("Test Modal Title")).toBeTruthy();
    expect(rendered.getByTestId("testModalContent")).toBeTruthy();
  });

  it("should close the modal with escape and emit a cancel result", async () => {
    const resultCallback = jest.fn();

    const rendered = renderModal(resultCallback);

    await waitFor(() => userEvent.keyboard("{Escape}"));

    expect(rendered.queryByTestId("testModalContent")).toBeFalsy();
    expect(resultCallback).toHaveBeenCalledWith({ type: "canceled" });
  });

  it("should allow cancelling the modal from inside", async () => {
    const resultCallback = jest.fn();

    const rendered = renderModal(resultCallback);

    await waitFor(() => userEvent.click(rendered.getByTestId("cancel")));

    expect(rendered.queryByTestId("testModalContent")).toBeFalsy();
    expect(resultCallback).toHaveBeenCalledWith({ type: "canceled" });
  });

  it("should allow closing the button with a reason and return that reason", async () => {
    const resultCallback = jest.fn();

    let rendered = renderModal(resultCallback);

    await waitFor(() => userEvent.click(rendered.getByTestId("close-reason1")));

    expect(rendered.queryByTestId("testModalContent")).toBeFalsy();
    expect(resultCallback).toHaveBeenCalledWith({ type: "closed", reason: "reason1" });

    resultCallback.mockReset();
    rendered = renderModal(resultCallback);

    await waitFor(() => userEvent.click(rendered.getByTestId("close-reason2")));

    expect(rendered.queryByTestId("testModalContent")).toBeFalsy();
    expect(resultCallback).toHaveBeenCalledWith({ type: "closed", reason: "reason2" });
  });
});
