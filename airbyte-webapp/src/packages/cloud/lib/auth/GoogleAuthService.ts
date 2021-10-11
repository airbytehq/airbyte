import {
  Auth,
  User,
  UserCredential,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  confirmPasswordReset,
  applyActionCode,
  sendEmailVerification,
  EmailAuthProvider,
  reauthenticateWithCredential,
  updatePassword,
  updateEmail,
} from "firebase/auth";

import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { ErrorCodes } from "packages/cloud/services/auth/types";
import { Provider } from "config";

interface AuthService {
  login(email: string, password: string): Promise<UserCredential>;

  signOut(): Promise<any>;

  signUp(email: string, password: string): Promise<UserCredential>;

  reauthenticate(
    email: string,
    passwordPassword: string
  ): Promise<UserCredential>;

  updatePassword(newPassword: string): Promise<void>;

  resetPassword(email: string): Promise<void>;

  finishResetPassword(code: string, newPassword: string): Promise<void>;

  sendEmailVerifiedLink(): Promise<void>;

  updateEmail(email: string, password: string): Promise<void>;
}

export class GoogleAuthService implements AuthService {
  constructor(private firebaseAuthProvider: Provider<Auth>) {}

  get auth(): Auth {
    return this.firebaseAuthProvider();
  }

  getCurrentUser(): User | null {
    return this.auth.currentUser;
  }

  async login(email: string, password: string): Promise<UserCredential> {
    return signInWithEmailAndPassword(this.auth, email, password).catch(
      (err) => {
        switch (err.code) {
          case "auth/invalid-email":
            throw new FieldError("email", ErrorCodes.Invalid);
          case "auth/user-disabled":
            throw new FieldError("email", "disabled");
          case "auth/user-not-found":
            throw new FieldError("email", "notfound");
          case "auth/wrong-password":
            throw new FieldError("password", ErrorCodes.Invalid);
        }

        throw err;
      }
    );
  }

  async signUp(email: string, password: string): Promise<UserCredential> {
    return createUserWithEmailAndPassword(this.auth, email, password).catch(
      (err) => {
        switch (err.code) {
          case "auth/email-already-in-use":
            throw new FieldError("email", ErrorCodes.Duplicate);
          case "auth/invalid-email":
            throw new FieldError("email", ErrorCodes.Invalid);
          case "auth/weak-password":
            throw new FieldError("password", ErrorCodes.Invalid);
        }

        throw err;
      }
    );
  }

  async reauthenticate(
    email: string,
    password: string
  ): Promise<UserCredential> {
    if (this.auth.currentUser === null) {
      throw new Error("You must log in first to reauthenticate!");
    }
    const credential = EmailAuthProvider.credential(email, password);
    return reauthenticateWithCredential(this.auth.currentUser, credential);
  }

  async updatePassword(newPassword: string): Promise<void> {
    if (this.auth.currentUser === null) {
      throw new Error("You must log in first to update password!");
    }
    return updatePassword(this.auth.currentUser, newPassword).catch((err) => {
      throw err;
    });
  }

  async updateEmail(email: string, password: string): Promise<void> {
    const user = await this.getCurrentUser();

    if (user) {
      await this.reauthenticate(email, password);

      return updateEmail(user, email);
    }

    return Promise.resolve();
  }

  async resetPassword(email: string): Promise<void> {
    return sendPasswordResetEmail(this.auth, email).catch((err) => {
      // switch (err.code) {
      //   case "auth/email-already-in-use":
      //     throw new FieldError("email", ErrorCodes.Duplicate);
      //   case "auth/invalid-email":
      //     throw new FieldError("email", ErrorCodes.Invalid);
      //   case "auth/weak-password":
      //     throw new FieldError("password", ErrorCodes.Invalid);
      // }

      throw err;
    });
  }

  async finishResetPassword(code: string, newPassword: string): Promise<void> {
    return confirmPasswordReset(this.auth, code, newPassword).catch((err) => {
      // switch (err.code) {
      //   case "auth/email-already-in-use":
      //     throw new FieldError("email", ErrorCodes.Duplicate);
      //   case "auth/invalid-email":
      //     throw new FieldError("email", ErrorCodes.Invalid);
      //   case "auth/weak-password":
      //     throw new FieldError("password", ErrorCodes.Invalid);
      // }

      throw err;
    });
  }

  async sendEmailVerifiedLink(): Promise<void> {
    return sendEmailVerification(this.getCurrentUser()!).catch((err) => {
      // switch (err.code) {
      //   case "auth/email-already-in-use":
      //     throw new FieldError("email", ErrorCodes.Duplicate);
      //   case "auth/invalid-email":
      //     throw new FieldError("email", ErrorCodes.Invalid);
      //   case "auth/weak-password":
      //     throw new FieldError("password", ErrorCodes.Invalid);
      // }

      throw err;
    });
  }

  async confirmEmailVerify(code: string): Promise<void> {
    return applyActionCode(this.auth, code);
  }

  signOut(): Promise<void> {
    return this.auth.signOut();
  }
}
