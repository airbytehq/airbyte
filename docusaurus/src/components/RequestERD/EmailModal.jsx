import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import cn from "classnames";
import React, { useState } from "react";
import styles from "./EmailModal.module.css";

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
  const [showEmailError, setShowEmailError] = useState(false);


  const emailValidation = (value) => {
    console.log("value", value);
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
    emailValidation(emailValue)

  };
  
  const handleBlur = () => {
    if(email && emailError) {
      setShowEmailError(true);
    }
  };
  const handleFocus = () => {
    setShowEmailError(false);
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
        <p> Error submitting your request. Please try again later.</p>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      onSubmit(email);
    }} >
      <p>
        We ask for your email so we can notify you when the ERD is ready.
      </p>
      <div className={styles.modalContentForm}>

      <div className={styles.modalContentInputContainer}>
        <input
          className={cn(styles.modalContentInput, {
            [styles.modalContentInputError]: showEmailError && emailError,
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
        {showEmailError && emailError && <p className={styles.inputErrorMessage}>{emailError}</p>}
      </div>
      <button
        type="submit"
        className={styles.modalContentButton}
        disabled={status === "loading" || Boolean(emailError)}
      >
        {status === "loading" ? "Submitting..." : "Submit"}
      </button>
      </div>
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
            <CloseButton onClose={()=> {
              setStatus("");
              onClose();
            }} />
          </div>
          <ModalBody onSubmit={handleSubmit} status={status}/>
        </>
      </div>
    </div>
  );
};
