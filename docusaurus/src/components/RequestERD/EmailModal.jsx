import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import cn from "classnames";
import React, { useState } from "react";
import styles from "./EmailModal.module.css";

import { Modal } from "../Modal/Modal";

const Form = ({ status, onSubmit }) => {
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [showEmailError, setShowEmailError] = useState(false);

  const emailValidation = (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(value)) {
      setEmailError("");
    } else {
      setEmailError("Please enter a valid email address");
    }
  };

  const handleOnChange = (e) => {
    const emailValue = e.target.value;
    setEmail(emailValue);
    emailValidation(emailValue);
  };

  const handleBlur = () => {
    if (email && emailError) {
      setShowEmailError(true);
    }
  };
  const handleFocus = () => {
    setShowEmailError(false);
  };

  if (status === "success") {
    return (
      <div className={cn(styles.form__status, styles["form__status--success"])}>
        <p> Request submitted successfully!</p>
        <p> We will notify you when the ERD is ready</p>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className={cn(styles.form__status, styles["form__status--error"])}>
        <p> Error submitting your request. Please try again later.</p>
      </div>
    );
  }

  return (
    <form
      className={styles.form}
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(email);
      }}
    >
      <div className={styles.form__inputContainer}>
        <input
          className={cn(styles.form__input, {
            [styles["form__input--error"]]: showEmailError && emailError,
          })}
          type="email"
          value={email}
          autoComplete="email"
          onChange={handleOnChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          placeholder="Enter your email"
          required
          disabled={status === "loading"}
        />
        {showEmailError && emailError && (
          <p className={styles.form__input__errorMessage}>{emailError}</p>
        )}
      </div>
      <button
        type="submit"
        className={styles.form__submitButton}
        disabled={status === "loading" || Boolean(emailError) || !email}
      >
        {status === "loading" ? "Submitting..." : "Submit"}
      </button>
    </form>
  );
};

export const EmailModal = ({ isOpen, onClose, sourceInfo }) => {
  const [status, setStatus] = useState("");
  const {
    siteConfig: {
      customFields: { requestErdApiUrl },
    },
  } = useDocusaurusContext();

  if (!isOpen) return null;

  const handleSubmit = async (email) => {
    setStatus("loading");

    try {
      const response = await fetch(`${requestErdApiUrl}/api/request-erd`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          requester_email: email,
          url: sourceInfo.url,
          source_name: sourceInfo.name,
          source_definition_id: sourceInfo.definitionId,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        console.error("Error requesting ERD:", JSON.parse(error));
        setStatus("error");
      } else {
        setStatus("success");
      }
    } catch (error) {
      console.error("Error requesting ERD:", error);
      setStatus("error");
    }
  };
  return (
    <Modal
      isOpen={isOpen}
      title="Request ERD"
      description="We ask for your email so we can notify you when the ERD is ready."
      onClose={() => {
        setStatus("");
        onClose();
      }}
    >
      <Form onSubmit={handleSubmit} status={status} />
    </Modal>
  );
};
