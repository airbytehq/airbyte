import firebase from "firebase";

const config = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
};

const firebaseApp = !firebase.apps.length
  ? firebase.initializeApp(config)
  : firebase.app();

export { firebaseApp };
export default firebaseApp;
