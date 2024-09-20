import React, { useState } from "react";
import styles from "./EmailModal.module.css";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import cn from "classnames";
import { useDebouncedCallback } from "use-debounce";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

const CloseButton = ({ onClose }) => {
  return (
    <button onClick={onClose} className={styles.modalContentClose}>
      <FontAwesomeIcon icon={faXmark} />
    </button>
  );
};

const ModalBody = ({ status, onSubmit }) => {
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState("");

  const debouncedValidation = useDebouncedCallback((value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(value)) {
      setEmailError("");
    } else {
      setEmailError("Please enter a valid email address");
    }
  }, 800);

  const handleOnChange = (e) => {
    const emailValue = e.target.value;
    setEmail(emailValue);
    debouncedValidation(emailValue);
  };

  if (status === "success") {
    return (
      <div>
        <p> Request submitted successfully!</p>
        <p> We will notify you when the ERD is ready</p>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div>
        <p> Error submitting request. Please try again later.</p>
      </div>
    );
  }

  return (
    <form onSubmit={() => onSubmit(email)} className={styles.modalContentForm}>
      <div className={styles.modalContentInputContainer}>
        <input
          className={cn(styles.modalContentInput, {
            [styles.modalContentInputError]: emailError,
          })}
          type="email"
          value={email}
          autoComplete="email"
          onChange={handleOnChange}
          placeholder="Enter your email"
          required
          disabled={status === "loading"}
        />
        {emailError && <p className={styles.inputErrorMessage}>{emailError}</p>}
      </div>
      <button
        type="submit"
        onClick={(e) => {
          e.preventDefault();
          onSubmit(email);
        }}
        className={styles.modalContentButton}
        disabled={status === "loading"}
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
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <>
          <div className={styles.modalContentHeader}>
            <h4>Request ERD</h4>
            <CloseButton onClose={onClose} />
          </div>
          <ModalBody onSubmit={handleSubmit} status={status} />
        </>
      </div>
    </div>
  );
};
