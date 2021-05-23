import { useFetcher } from "rest-hooks";

import OperationsResource, {
  Operation,
  OperationConfiguration,
} from "core/resources/Operations";

type ValuesProps = {
  name: string;
  operatorConfiguration: OperationConfiguration;
};

type OperationService = {
  createOperation: ({
    operation,
  }: {
    operation: ValuesProps;
  }) => Promise<Operation>;
  updateOperation: ({
    operation,
  }: {
    operation: ValuesProps;
  }) => Promise<Operation>;
  deleteOperation: ({ operationId }: { operationId: string }) => Promise<void>;
};

const useOperation = (): OperationService => {
  const operationUpdate = useFetcher(OperationsResource.updateShape());
  const operationCreate = useFetcher(OperationsResource.createShape());
  const operationDelete = useFetcher(OperationsResource.deleteShape());

  const createOperation = async ({ operation }: { operation: ValuesProps }) => {
    try {
      const result = await operationCreate(operation);
      return result;
    } catch (e) {
      throw e;
    }
  };

  const updateOperation = async ({ operation }: { operation: ValuesProps }) => {
    try {
      const result = await operationUpdate(operation);
      return result;
    } catch (e) {
      throw e;
    }
  };

  const deleteOperation = async ({ operationId }: { operationId: string }) => {
    try {
      await operationDelete({ operationId });
    } catch (e) {
      throw e;
    }
  };

  return {
    createOperation,
    updateOperation,
    deleteOperation,
  };
};

export default useOperation;
