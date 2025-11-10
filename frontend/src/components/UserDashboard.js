import React, { useState, useEffect } from "react";
import { useAuth } from "../AuthContext";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  FileText,
  TrendingUp,
  Award,
  Target,
  Calendar,
  Star,
  Brain,
  CheckCircle,
} from "lucide-react";
import axios from "axios";
import { Link } from "react-router-dom";

// Navigation Component with improved styling
const Navigation = () => {
  const { user, isAdmin, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <nav
      className="navbar navbar-expand-lg navbar-dark shadow-sm"
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        padding: "1rem 0",
      }}
    >
      <div className="container-fluid px-4">
        <Link
          className="navbar-brand fw-bold fs-3"
          to="/"
          style={{
            fontFamily: "system-ui, -apple-system, sans-serif",
            letterSpacing: "-0.5px",
          }}
        >
          <i className="fas fa-file-alt me-2"></i>
          IntelliResume
        </Link>

        <button
          className="navbar-toggler border-0"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarNav">
          <div className="navbar-nav ms-auto d-flex align-items-center">
            {user && (
              <>
                <Link
                  className="nav-link px-3 py-2 rounded-pill me-2 position-relative"
                  to="/dashboard"
                  style={{
                    transition: "all 0.3s ease",
                    fontWeight: "500",
                  }}
                  onMouseEnter={(e) =>
                    (e.target.style.backgroundColor = "rgba(255,255,255,0.1)")
                  }
                  onMouseLeave={(e) =>
                    (e.target.style.backgroundColor = "transparent")
                  }
                >
                  <i className="fas fa-tachometer-alt me-2"></i>
                  Dashboard
                </Link>

                {!isAdmin && (
                  <>
                    <Link
                      className="nav-link px-3 py-2 rounded-pill me-2"
                      to="/analyze"
                      style={{
                        transition: "all 0.3s ease",
                        fontWeight: "500",
                      }}
                      onMouseEnter={(e) =>
                        (e.target.style.backgroundColor =
                          "rgba(255,255,255,0.1)")
                      }
                      onMouseLeave={(e) =>
                        (e.target.style.backgroundColor = "transparent")
                      }
                    >
                      <i className="fas fa-upload me-2"></i>
                      Analyze Resume
                    </Link>
                    <Link
                      className="nav-link px-3 py-2 rounded-pill me-2"
                      to="/history"
                      style={{
                        transition: "all 0.3s ease",
                        fontWeight: "500",
                      }}
                      onMouseEnter={(e) =>
                        (e.target.style.backgroundColor =
                          "rgba(255,255,255,0.1)")
                      }
                      onMouseLeave={(e) =>
                        (e.target.style.backgroundColor = "transparent")
                      }
                    >
                      <i className="fas fa-history me-2"></i>
                      My Analyses
                    </Link>
                  </>
                )}

                {isAdmin && (
                  <Link
                    className="nav-link px-3 py-2 rounded-pill me-2"
                    to="/admin"
                    style={{
                      transition: "all 0.3s ease",
                      fontWeight: "500",
                    }}
                    onMouseEnter={(e) =>
                      (e.target.style.backgroundColor = "rgba(255,255,255,0.1)")
                    }
                    onMouseLeave={(e) =>
                      (e.target.style.backgroundColor = "transparent")
                    }
                  >
                    <i className="fas fa-users-cog me-2"></i>
                    Admin Panel
                  </Link>
                )}

                <div className="dropdown me-3">
                  <button
                    className="btn btn-link text-white dropdown-toggle d-flex align-items-center text-decoration-none border-0 bg-transparent"
                    type="button"
                    data-bs-toggle="dropdown"
                    style={{ fontWeight: "500" }}
                  >
                    <div
                      className="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center me-2"
                      style={{
                        width: "32px",
                        height: "32px",
                        fontSize: "14px",
                        fontWeight: "bold",
                      }}
                    >
                      {user.full_name?.charAt(0).toUpperCase()}
                    </div>
                    {user.full_name}
                  </button>
                  <ul
                    className="dropdown-menu dropdown-menu-end shadow border-0"
                    style={{
                      borderRadius: "12px",
                      padding: "0.5rem 0",
                    }}
                  >
                    <li>
                      <Link className="dropdown-item py-2" to="/profile">
                        <i className="fas fa-user me-2"></i>
                        Profile
                      </Link>
                    </li>
                    <li>
                      <Link className="dropdown-item py-2" to="/settings">
                        <i className="fas fa-cog me-2"></i>
                        Settings
                      </Link>
                    </li>
                    <li>
                      <hr className="dropdown-divider" />
                    </li>
                    <li>
                      <button
                        className="dropdown-item py-2 text-danger"
                        onClick={handleLogout}
                      >
                        <i className="fas fa-sign-out-alt me-2"></i>
                        Logout
                      </button>
                    </li>
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
const UserDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, insightsResponse] = await Promise.all([
        axios.get("/api/dashboard/user/stats"),
        axios.get("/api/dashboard/user/insights"),
      ]);

      setStats(statsResponse.data);
      setInsights(insightsResponse.data);

      // Debug: Log the score progression data
      console.log(
        "Score progression data:",
        statsResponse.data.score_progression
      );
      console.log(
        "Recommended skills data:",
        statsResponse.data.recommended_skills
      );
    } catch (error) {
      setError("Failed to load dashboard data");
      console.error("Dashboard error:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ minHeight: "400px" }}
      >
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <>
      <Navigation />
      <div
        className="container-fluid py-4"
        style={{ backgroundColor: "#f8f9fa", minHeight: "100vh" }}
      >
        {/* Welcome Header */}
        <div className="row mb-4">
          <div className="col-12">
            <div
              className="card border-0 shadow-lg"
              style={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                borderRadius: "20px",
              }}
            >
              <div className="card-body p-4">
                <h2
                  className="text-white mb-3 fw-bold"
                  style={{ fontSize: "1.8rem" }}
                >
                  <i className="fas fa-chart-line me-3"></i>
                  Welcome back, {user?.full_name}!
                </h2>
                <p
                  className="text-white mb-0"
                  style={{ opacity: 0.9, fontSize: "1rem" }}
                >
                  Here's your resume analysis dashboard with personalized
                  insights and recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="row mb-4">
          <div className="col-md-3 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{
                borderRadius: "15px",
                background:
                  "linear-gradient(135deg, #667eea20 0%, #764ba220 100%)",
              }}
            >
              <div className="card-body text-center p-4">
                <div
                  className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "50px", height: "50px" }}
                >
                  <FileText className="text-white" size={24} />
                </div>
                <h3
                  className="text-primary mb-2 fw-bold"
                  style={{ fontSize: "1.8rem" }}
                >
                  {stats?.total_resumes || 0}
                </h3>
                <p
                  className="text-muted mb-0 fw-medium"
                  style={{ fontSize: "0.9rem" }}
                >
                  Total Resumes
                </p>
              </div>
            </div>
          </div>

          <div className="col-md-3 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{
                borderRadius: "15px",
                background:
                  "linear-gradient(135deg, #28a74520 0%, #20c99720 100%)",
              }}
            >
              <div className="card-body text-center p-4">
                <div
                  className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "50px", height: "50px" }}
                >
                  <Award className="text-white" size={24} />
                </div>
                <h3
                  className="text-success mb-2 fw-bold"
                  style={{ fontSize: "1.8rem" }}
                >
                  {stats?.overall_score || 0}
                </h3>
                <p
                  className="text-muted mb-0 fw-medium"
                  style={{ fontSize: "0.9rem" }}
                >
                  Overall Score
                </p>
              </div>
            </div>
          </div>

          <div className="col-md-3 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{
                borderRadius: "15px",
                background:
                  "linear-gradient(135deg, #ffc10720 0%, #fb8c0020 100%)",
              }}
            >
              <div className="card-body text-center p-4">
                <div
                  className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "50px", height: "50px" }}
                >
                  <TrendingUp className="text-white" size={24} />
                </div>
                <h3
                  className="text-warning mb-2 fw-bold"
                  style={{ fontSize: "1.8rem" }}
                >
                  {stats?.resumes_improved || 0}
                </h3>
                <p
                  className="text-muted mb-0 fw-medium"
                  style={{ fontSize: "0.9rem" }}
                >
                  Improved Resumes
                </p>
              </div>
            </div>
          </div>

          <div className="col-md-3 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{
                borderRadius: "15px",
                background:
                  "linear-gradient(135deg, #17a2b820 0%, #0dcaf020 100%)",
              }}
            >
              <div className="card-body text-center p-4">
                <div
                  className="bg-info rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "50px", height: "50px" }}
                >
                  <Calendar className="text-white" size={24} />
                </div>
                <h4
                  className="text-info mb-2 fw-bold"
                  style={{ fontSize: "1.1rem" }}
                >
                  {stats?.last_analyzed
                    ? new Date(stats.last_analyzed).toLocaleDateString()
                    : "N/A"}
                </h4>
                <p
                  className="text-muted mb-0 fw-medium"
                  style={{ fontSize: "0.9rem" }}
                >
                  Last Analyzed
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="row mb-4">
          {/* Score Progression Chart */}
          <div className="col-lg-8 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h5
                  className="card-title mb-0 fw-bold text-dark"
                  style={{ fontSize: "1.1rem" }}
                >
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "36px", height: "36px" }}
                    >
                      <TrendingUp className="text-white" size={18} />
                    </div>
                    Resume Score Progression
                  </div>
                </h5>
              </div>
              <div className="card-body px-4 pb-4">
                {stats?.score_progression &&
                stats.score_progression.length > 0 ? (
                  <>
                    {console.log("=== CHART DATA DETAILED DEBUG ===")}
                    {console.log("Full stats object:", stats)}
                    {console.log(
                      "Score progression array:",
                      stats.score_progression
                    )}
                    {stats.score_progression.map((item, index) => {
                      console.log(`Point ${index}:`, {
                        date: item.date,
                        score: item.score,
                        scoreType: typeof item.score,
                        rawItem: item,
                      });
                      return null;
                    })}
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart
                        key={JSON.stringify(stats.score_progression)}
                        data={stats.score_progression}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="date" fontSize={12} tickLine={false} />
                        <YAxis
                          domain={[0, 100]}
                          fontSize={12}
                          tickLine={false}
                          axisLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#fff",
                            border: "1px solid #e0e0e0",
                            borderRadius: "8px",
                            fontSize: "12px",
                          }}
                          formatter={(value, name, props) => {
                            console.log("=== TOOLTIP DEBUG ===");
                            console.log(
                              "Tooltip value:",
                              value,
                              "Type:",
                              typeof value
                            );
                            console.log("Tooltip name:", name);
                            console.log("Tooltip props:", props);
                            console.log("Full payload:", props?.payload);
                            return [`${value}%`, "Score"];
                          }}
                          labelFormatter={(label) => `Date: ${label}`}
                        />
                        <Line
                          type="monotone"
                          dataKey="score"
                          stroke="#0088FE"
                          strokeWidth={2}
                          dot={{ fill: "#0088FE", strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </>
                ) : (
                  <div className="text-center text-muted py-5">
                    <FileText size={48} className="mb-3" />
                    <p>
                      No resume analyses yet. Upload your first resume to see
                      progress!
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ATS Compatibility */}
          <div className="col-lg-4 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h5
                  className="card-title mb-0 fw-bold text-dark"
                  style={{ fontSize: "1.1rem" }}
                >
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "36px", height: "36px" }}
                    >
                      <Target className="text-white" size={18} />
                    </div>
                    ATS Compatibility
                  </div>
                </h5>
              </div>
              <div className="card-body d-flex align-items-center justify-content-center px-4 pb-4">
                <div className="text-center">
                  <div className="position-relative d-inline-flex mb-3">
                    <svg
                      width="120"
                      height="120"
                      className="transform-rotate-90"
                      style={{
                        filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.1))",
                      }}
                    >
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        stroke="#e9ecef"
                        strokeWidth="10"
                        fill="transparent"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        stroke="url(#gradient1)"
                        strokeWidth="10"
                        fill="transparent"
                        strokeDasharray={`${2 * Math.PI * 50}`}
                        strokeDashoffset={`${
                          2 *
                          Math.PI *
                          50 *
                          (1 - (stats?.ats_compatibility || 75) / 100)
                        }`}
                        strokeLinecap="round"
                      />
                      <defs>
                        <linearGradient
                          id="gradient1"
                          gradientUnits="userSpaceOnUse"
                        >
                          <stop offset="0%" stopColor="#28a745" />
                          <stop offset="100%" stopColor="#20c997" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="position-absolute top-50 start-50 translate-middle">
                      <h4
                        className="text-success mb-0 fw-bold"
                        style={{ fontSize: "1.6rem" }}
                      >
                        {stats?.ats_compatibility || 75}%
                      </h4>
                    </div>
                  </div>
                  <p
                    className="text-muted mt-2 mb-0 fw-medium"
                    style={{ fontSize: "0.85rem" }}
                  >
                    Compatibility Score
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="row mb-4">
          {/* Top Recommended Skills */}
          <div className="col-lg-6 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h5
                  className="card-title mb-0 fw-bold text-dark"
                  style={{ fontSize: "1.1rem" }}
                >
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "36px", height: "36px" }}
                    >
                      <Star className="text-white" size={18} />
                    </div>
                    Top Recommended Skills
                  </div>
                </h5>
              </div>
              <div className="card-body px-4 pb-4">
                {stats?.recommended_skills &&
                stats.recommended_skills.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart
                      data={stats.recommended_skills}
                      margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis
                        dataKey="skill"
                        fontSize={11}
                        tickLine={false}
                        axisLine={false}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis
                        domain={[0, 100]}
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#fff",
                          border: "1px solid #e0e0e0",
                          borderRadius: "8px",
                          fontSize: "12px",
                        }}
                        formatter={(value) => [`${value}%`, "Relevance"]}
                      />
                      <Bar
                        dataKey="relevance"
                        fill="#667eea"
                        stroke="#4c63d2"
                        strokeWidth={1}
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center text-muted py-5">
                    <Star size={48} className="mb-3" />
                    <p>Upload a resume to get skill recommendations!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="col-lg-6 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{
                borderRadius: "15px",
                background:
                  stats?.bert_available !== false
                    ? "linear-gradient(135deg, #667eea10 0%, #764ba210 100%)"
                    : "transparent",
              }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h4 className="card-title mb-0 fw-bold text-dark">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-info rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "40px", height: "40px" }}
                    >
                      <Brain className="text-white" size={20} />
                    </div>
                    AI-Generated Insights
                    {stats?.bert_available !== false && (
                      <span
                        className="badge bg-primary ms-2"
                        style={{ fontSize: "0.6rem" }}
                      >
                        BERT
                      </span>
                    )}
                  </div>
                </h4>
              </div>
              <div className="card-body px-4 pb-4">
                {insights ? (
                  <div>
                    <p className="mb-3">{insights.summary}</p>

                    {/* BERT Status Indicator */}
                    {stats?.bert_available !== false && (
                      <div className="mb-3 p-2 bg-primary bg-opacity-10 rounded">
                        <div className="d-flex align-items-center">
                          <i className="fas fa-robot text-primary me-2"></i>
                          <small className="text-primary fw-bold">
                            Enhanced with BERT AI • More accurate insights
                          </small>
                        </div>
                      </div>
                    )}

                    <div className="mb-3">
                      <h6 className="text-success">
                        <CheckCircle size={16} className="me-1" />
                        Strengths
                      </h6>
                      <ul className="list-unstyled ms-3">
                        {insights.strengths?.map((strength, index) => (
                          <li key={index} className="mb-1">
                            <small className="text-muted">• {strength}</small>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h6 className="text-warning">
                        <TrendingUp size={16} className="me-1" />
                        Improvements
                      </h6>
                      <ul className="list-unstyled ms-3">
                        {insights.improvements
                          ?.slice(0, 3)
                          .map((improvement, index) => (
                            <li key={index} className="mb-1">
                              <small className="text-muted">
                                • {improvement}
                              </small>
                            </li>
                          ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted py-5">
                    <Brain size={48} className="mb-3" />
                    <p>Analyze your resume to get AI insights!</p>
                    {stats?.bert_available === false && (
                      <div className="mt-2">
                        <small className="text-info">
                          <i className="fas fa-info-circle me-1"></i>
                          BERT AI analysis available after first upload
                        </small>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Recommended Job Roles */}
        {insights?.recommended_jobs && insights.recommended_jobs.length > 0 && (
          <div className="row mb-4">
            <div className="col-12">
              <div
                className="card border-0 shadow-sm"
                style={{ borderRadius: "15px" }}
              >
                <div className="card-header border-0 bg-transparent pt-4 px-4">
                  <h4 className="card-title mb-0 fw-bold text-dark">
                    <div className="d-flex align-items-center">
                      <div
                        className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                        style={{ width: "40px", height: "40px" }}
                      >
                        <Target className="text-white" size={20} />
                      </div>
                      Recommended Job Roles
                    </div>
                  </h4>
                </div>
                <div className="card-body px-4 pb-4">
                  <div className="row">
                    {insights.recommended_jobs.map((job, index) => (
                      <div key={index} className="col-md-3 mb-3">
                        <div
                          className="badge text-white fs-6 p-3 w-100 shadow-sm"
                          style={{
                            background:
                              "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            borderRadius: "10px",
                          }}
                        >
                          <i className="fas fa-briefcase me-2"></i>
                          {job}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default UserDashboard;
