import firebase from "firebase";

import { FieldError } from "packages/cloud/lib/errors/FieldError";
import { ErrorCodes } from "packages/cloud/services/auth/types";
import firebaseApp from "packages/cloud/config/firebase";

type UserCredential = any;

interface AuthService {
  login(email: string, password: string): Promise<any>;

  signOut(): Promise<any>;

  signUp(email: string, password: string): Promise<any>;
}

export class GoogleAuthService implements AuthService {
  getCurrentUser(): firebase.User | null {
    return firebaseApp.auth().currentUser;
  }
  async login(email: string, password: string): Promise<UserCredential> {
    return firebaseApp
      .auth()
      .signInWithEmailAndPassword(email, password)
      .catch((err) => {
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
      });
  }

  async signUp(email: string, password: string): Promise<UserCredential> {
    return firebaseApp
      .auth()
      .createUserWithEmailAndPassword(email, password)
      .catch((err) => {
        switch (err.code) {
          case "auth/email-already-in-use":
            throw new FieldError("email", ErrorCodes.Duplicate);
          case "auth/invalid-email":
            throw new FieldError("email", ErrorCodes.Invalid);
          case "auth/weak-password":
            throw new FieldError("password", ErrorCodes.Invalid);
        }

        throw err;
      });
  }

  async resetPassword(email: string): Promise<UserCredential> {
    return firebaseApp
      .auth()
      .sendPasswordResetEmail(email)
      .catch((err) => {
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

  signOut(): Promise<void> {
    return firebaseApp.auth().signOut();
  }
}
