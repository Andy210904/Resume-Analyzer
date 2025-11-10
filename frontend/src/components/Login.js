import React, { useState } from "react";
import { useAuth } from "../AuthContext";
import { Link, useNavigate, useLocation } from "react-router-dom";

const Login = () => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    remember: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isAdminLogin, setIsAdminLogin] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/";

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await login(formData, isAdminLogin);

    if (result.success) {
      navigate(isAdminLogin ? "/admin/dashboard" : from, { replace: true });
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  return (
    <div
      className="min-vh-100 d-flex align-items-center justify-content-center"
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <div className="container-fluid px-4">
        <div className="row justify-content-center">
          <div className="col-12 col-sm-8 col-md-6 col-lg-5 col-xl-4">
            <div
              className="card border-0 shadow-lg"
              style={{
                borderRadius: "16px",
                maxWidth: "400px",
                margin: "0 auto",
              }}
            >
              <div className="card-body p-4">
                <div className="text-center mb-4">
                  <div
                    className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                    style={{ width: "80px", height: "80px" }}
                  >
                    <i
                      className="fas fa-user-circle text-white"
                      style={{ fontSize: "2.5rem" }}
                    ></i>
                  </div>
                  <h1
                    className="fw-bold text-dark mb-2"
                    style={{ fontSize: "1.8rem", letterSpacing: "-0.5px" }}
                  >
                    {isAdminLogin ? "🔐 Admin Login" : "👋 Welcome Back"}
                  </h1>
                  <p
                    className="text-muted"
                    style={{ fontSize: "0.9rem", lineHeight: "1.4" }}
                  >
                    {isAdminLogin
                      ? "Access the admin dashboard and manage your system"
                      : "Sign in to your IntelliResume account and continue improving your career"}
                  </p>
                </div>

                {error && (
                  <div className="alert alert-danger" role="alert">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label
                      htmlFor="username"
                      className="form-label fw-medium text-dark mb-2"
                      style={{ fontSize: "0.95rem" }}
                    >
                      Username or Email
                    </label>
                    <input
                      type="text"
                      className="form-control border-0 bg-light"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      required
                      placeholder="Enter your username or email"
                      style={{
                        borderRadius: "12px",
                        padding: "12px 16px",
                        fontSize: "0.95rem",
                        minHeight: "45px",
                      }}
                    />
                  </div>

                  <div className="mb-3">
                    <label
                      htmlFor="password"
                      className="form-label fw-medium text-dark mb-2"
                      style={{ fontSize: "0.95rem" }}
                    >
                      Password
                    </label>
                    <input
                      type="password"
                      className="form-control border-0 bg-light"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      placeholder="Enter your password"
                      style={{
                        borderRadius: "12px",
                        padding: "12px 16px",
                        fontSize: "0.95rem",
                        minHeight: "45px",
                      }}
                    />
                  </div>

                  <div className="mb-4 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="remember"
                      name="remember"
                      checked={formData.remember}
                      onChange={handleChange}
                      style={{ transform: "scale(1.1)" }}
                    />
                    <label
                      className="form-check-label text-muted ms-2"
                      htmlFor="remember"
                      style={{ fontSize: "0.9rem" }}
                    >
                      Remember me
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="btn w-100 mb-3 border-0 shadow-sm text-white fw-medium"
                    disabled={loading}
                    style={{
                      background:
                        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      borderRadius: "12px",
                      padding: "12px 16px",
                      fontSize: "1rem",
                      minHeight: "45px",
                    }}
                  >
                    {loading ? (
                      <>
                        <span
                          className="spinner-border spinner-border-sm me-2"
                          role="status"
                        ></span>
                        Signing in...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-sign-in-alt me-2"></i>
                        Sign In
                      </>
                    )}
                  </button>
                </form>

                <div className="text-center mb-3">
                  <button
                    type="button"
                    className="btn btn-link text-decoration-none fw-medium p-1"
                    onClick={() => setIsAdminLogin(!isAdminLogin)}
                    style={{ color: "#667eea", fontSize: "0.9rem" }}
                  >
                    <i className="fas fa-exchange-alt me-1"></i>
                    {isAdminLogin ? "Login as Regular User" : "Login as Admin"}
                  </button>
                </div>

                {!isAdminLogin && (
                  <div className="text-center">
                    <p
                      className="mb-0 text-muted"
                      style={{ fontSize: "0.9rem" }}
                    >
                      Don't have an account?{" "}
                      <Link
                        to="/register"
                        className="text-decoration-none fw-medium"
                        style={{ color: "#667eea", fontSize: "0.9rem" }}
                      >
                        Sign up here
                      </Link>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
