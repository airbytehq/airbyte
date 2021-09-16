import { useState } from "react";

import { useGetUserService } from "packages/cloud/services/users/UserService";

type UseUserHook = () => {
  onDelete: (id: string) => void;
  isDeleting: boolean;
  deletingError?: Error;
};

const useUser: UseUserHook = () => {
  const userService = useGetUserService();
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [deletingError, setDeletingError] = useState<Error>();

  const onDelete = (id: string) => {
    if (!isDeleting) {
      setIsDeleting(true);

      userService
        .remove(id)
        .then(() => setIsDeleting(false))
        .catch((err) => setDeletingError(err));
    }
  };

  return { onDelete, isDeleting, deletingError };
};

export default useUser;
