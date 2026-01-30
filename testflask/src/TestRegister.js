import React from "react";

const TestRegister = () => {
  const registerUser = async () => {
    console.log("Registering user");
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "http://localhost:5050/register";
    form.target = "_blank"; // optional: open in new tab
    form.rel = "noopener noreferrer";
    form.enctype = "multipart/form-data";

    const emailInput = document.createElement("input");
    emailInput.type = "hidden";
    emailInput.name = "email";
    emailInput.value = "tokentestuser1@test";

    const tokenInput = document.createElement("input");
    tokenInput.type = "hidden";
    tokenInput.name = "token";
    tokenInput.value =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRva2VudGVzdHVzZXIxQHRlc3QiLCJpYXQiOjE3Njg4MjM3OTEsImV4cCI6MTc2ODg1OTc5MX0.6JmThiq_BpTN4WPrjdE-XTJ_zQKJpOISK7IQZu8_k18";

    form.appendChild(emailInput);
    form.appendChild(tokenInput);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
  };
  return (
    <div>
      <h1>Test Register</h1>
      <p>this page is to test the /register running on flask</p>
      <button
        onClick={() => {
          registerUser();
        }}
      >
        Register
      </button>
    </div>
  );
};

export default TestRegister;
