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
  AuthErrorCodes,
} from "firebase/auth";

import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { ErrorCodes } from "packages/cloud/services/auth/types";
import { Provider } from "config";

interface AuthService {
  login(email: string, password: string): Promise<UserCredential>;

  signOut(): Promise<void>;

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
          case AuthErrorCodes.INVALID_EMAIL:
            throw new FieldError("email", ErrorCodes.Invalid);
          case AuthErrorCodes.USER_CANCELLED:
            throw new FieldError("email", "disabled");
          case AuthErrorCodes.USER_DELETED:
            throw new FieldError("email", "notfound");
          case AuthErrorCodes.INVALID_PASSWORD:
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
          case AuthErrorCodes.EMAIL_EXISTS:
            throw new FieldError("email", ErrorCodes.Duplicate);
          case AuthErrorCodes.INVALID_EMAIL:
            throw new FieldError("email", ErrorCodes.Invalid);
          case AuthErrorCodes.WEAK_PASSWORD:
            throw new FieldError("password", ErrorCodes.Validation);
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
    return updatePassword(this.auth.currentUser, newPassword);
  }

  async updateEmail(email: string, password: string): Promise<void> {
    const user = await this.getCurrentUser();

    if (user) {
      await this.reauthenticate(email, password);

      try {
        await updateEmail(user, email);
      } catch (e) {
        switch (e.code) {
          case "auth/invalid-email":
            throw new FieldError("email", ErrorCodes.Invalid);
          case "auth/email-already-in-use":
            throw new FieldError("email", ErrorCodes.Duplicate);
          case "auth/requires-recent-login":
            throw new Error("auth/requires-recent-login");
        }
      }
    }
  }

  async resetPassword(email: string): Promise<void> {
    return sendPasswordResetEmail(this.auth, email);
  }

  async finishResetPassword(code: string, newPassword: string): Promise<void> {
    return confirmPasswordReset(this.auth, code, newPassword);
  }

  async sendEmailVerifiedLink(): Promise<void> {
    const currentUser = this.getCurrentUser();

    if (!currentUser) {
      console.error("sendEmailVerifiedLink should be used within auth flow");
      throw new Error("user is not authorised");
    }

    return sendEmailVerification(currentUser);
  }

  async confirmEmailVerify(code: string): Promise<void> {
    return applyActionCode(this.auth, code);
  }

  signOut(): Promise<void> {
    return this.auth.signOut();
  }
}
