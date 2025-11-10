import React, { useState } from "react";
import { useAuth } from "../AuthContext";
import { Link, useNavigate } from "react-router-dom";

const Register = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    first_name: "",
    last_name: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.username.trim()) {
      setError("Username is required");
      return false;
    }
    if (!formData.email.trim()) {
      setError("Email is required");
      return false;
    }
    if (!formData.password) {
      setError("Password is required");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    if (!formData.first_name.trim()) {
      setError("First name is required");
      return false;
    }
    if (!formData.last_name.trim()) {
      setError("Last name is required");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    const { confirmPassword, first_name, last_name, ...userData } = formData;
    // Combine first_name and last_name into full_name for backend
    const registrationData = {
      ...userData,
      full_name: `${first_name} ${last_name}`.trim(),
    };
    const result = await register(registrationData);

    if (result.success) {
      setSuccess("Account created successfully! Please log in.");
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  return (
    <div
      className="min-vh-100 d-flex align-items-center justify-content-center py-4"
      style={{
        background: "linear-gradient(135deg, #20c997 0%, #0dcaf0 100%)",
      }}
    >
      <div className="container-fluid px-4">
        <div className="row justify-content-center">
          <div className="col-12 col-sm-10 col-md-8 col-lg-7 col-xl-6 col-xxl-5">
            <div
              className="card border-0 shadow-lg"
              style={{
                borderRadius: "24px",
                maxWidth: "600px",
                margin: "0 auto",
              }}
            >
              <div
                className="card-body p-5"
                style={{ padding: "3rem !important" }}
              >
                <div className="text-center mb-5">
                  <div
                    className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center mb-4"
                    style={{ width: "120px", height: "120px" }}
                  >
                    <i
                      className="fas fa-user-plus text-white"
                      style={{ fontSize: "4rem" }}
                    ></i>
                  </div>
                  <h1
                    className="fw-bold text-dark mb-3"
                    style={{ fontSize: "2.8rem", letterSpacing: "-0.5px" }}
                  >
                    🚀 Create Account
                  </h1>
                  <p
                    className="text-muted"
                    style={{ fontSize: "1.15rem", lineHeight: "1.6" }}
                  >
                    Join IntelliResume and take your career to the next level
                  </p>
                </div>

                {error && (
                  <div className="alert alert-danger" role="alert">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="alert alert-success" role="alert">
                    {success}
                  </div>
                )}

                <form onSubmit={handleSubmit}>
                  <div className="row">
                    <div className="col-md-6 mb-4">
                      <label
                        htmlFor="first_name"
                        className="form-label fw-medium text-dark"
                      >
                        First Name *
                      </label>
                      <input
                        type="text"
                        className="form-control form-control-lg border-0 bg-light"
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        required
                        placeholder="John"
                        style={{ borderRadius: "12px", padding: "12px 16px" }}
                      />
                    </div>
                    <div className="col-md-6 mb-4">
                      <label
                        htmlFor="last_name"
                        className="form-label fw-medium text-dark"
                      >
                        Last Name *
                      </label>
                      <input
                        type="text"
                        className="form-control form-control-lg border-0 bg-light"
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        required
                        placeholder="Doe"
                        style={{ borderRadius: "12px", padding: "12px 16px" }}
                      />
                    </div>
                  </div>

                  <div className="mb-4">
                    <label
                      htmlFor="username"
                      className="form-label fw-medium text-dark"
                    >
                      Username *
                    </label>
                    <input
                      type="text"
                      className="form-control form-control-lg border-0 bg-light"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      required
                      placeholder="johndoe"
                      style={{ borderRadius: "12px", padding: "12px 16px" }}
                    />
                  </div>

                  <div className="mb-4">
                    <label
                      htmlFor="email"
                      className="form-label fw-medium text-dark"
                    >
                      Email Address *
                    </label>
                    <input
                      type="email"
                      className="form-control form-control-lg border-0 bg-light"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="john@example.com"
                      style={{ borderRadius: "12px", padding: "12px 16px" }}
                    />
                  </div>

                  <div className="mb-4">
                    <label
                      htmlFor="password"
                      className="form-label fw-medium text-dark"
                    >
                      Password *
                    </label>
                    <input
                      type="password"
                      className="form-control form-control-lg border-0 bg-light"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      placeholder="Create a strong password"
                      style={{ borderRadius: "12px", padding: "12px 16px" }}
                    />
                    <div className="form-text text-muted mt-2">
                      <i className="fas fa-info-circle me-1"></i>
                      Password must be at least 8 characters with uppercase,
                      lowercase, and number.
                    </div>
                  </div>

                  <div className="mb-4">
                    <label
                      htmlFor="confirmPassword"
                      className="form-label fw-medium text-dark"
                    >
                      Confirm Password *
                    </label>
                    <input
                      type="password"
                      className="form-control form-control-lg border-0 bg-light"
                      id="confirmPassword"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      placeholder="Confirm your password"
                      style={{ borderRadius: "12px", padding: "12px 16px" }}
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-lg w-100 mb-4 border-0 shadow-sm text-white fw-medium"
                    disabled={loading}
                    style={{
                      background:
                        "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
                      borderRadius: "12px",
                      padding: "12px",
                    }}
                  >
                    {loading ? (
                      <>
                        <span
                          className="spinner-border spinner-border-sm me-2"
                          role="status"
                        ></span>
                        Creating Account...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-user-plus me-2"></i>
                        Create Account
                      </>
                    )}
                  </button>
                </form>

                <div className="text-center">
                  <p className="mb-0 text-muted">
                    Already have an account?{" "}
                    <Link
                      to="/login"
                      className="text-decoration-none fw-medium"
                      style={{ color: "#667eea" }}
                    >
                      Sign in here
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
