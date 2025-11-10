import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

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

const PastAnalyses = () => {
  const [analyses, setAnalyses] = useState([]);
  const [filteredAnalyses, setFilteredAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [deleteLoading, setDeleteLoading] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [downloadingId, setDownloadingId] = useState(null);

  // Filter states
  const [sortBy, setSortBy] = useState("date"); // 'date', 'score', 'jobRole'
  const [sortOrder, setSortOrder] = useState("desc"); // 'asc', 'desc'
  const [filterJobRole, setFilterJobRole] = useState(""); // filter by job role
  const [filterScore, setFilterScore] = useState(""); // 'high', 'medium', 'low', ''

  const fetchAnalyses = async (p = 1) => {
    try {
      setLoading(true);
      const res = await axios.get(
        `/api/dashboard/user/analyses?page=${p}&per_page=50`,
        { withCredentials: true }
      );
      const analysesData = res.data.analyses || [];
      setAnalyses(analysesData);
      setFilteredAnalyses(analysesData);
      setPage(res.data.current_page || 1);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load analyses");
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort analyses
  const applyFiltersAndSort = useCallback(() => {
    let filtered = [...analyses];

    // Apply job role filter
    if (filterJobRole) {
      filtered = filtered.filter((analysis) =>
        analysis.job_role.toLowerCase().includes(filterJobRole.toLowerCase())
      );
    }

    // Apply score filter
    if (filterScore) {
      filtered = filtered.filter((analysis) => {
        const score = analysis.overall_score || 0;
        switch (filterScore) {
          case "high":
            return score >= 80;
          case "medium":
            return score >= 60 && score < 80;
          case "low":
            return score < 60;
          default:
            return true;
        }
      });
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let compareValue = 0;

      switch (sortBy) {
        case "score":
          compareValue = (a.overall_score || 0) - (b.overall_score || 0);
          break;
        case "jobRole":
          compareValue = a.job_role.localeCompare(b.job_role);
          break;
        case "filename":
          compareValue = a.filename.localeCompare(b.filename);
          break;
        case "date":
        default:
          compareValue = new Date(a.created_at) - new Date(b.created_at);
          break;
      }

      return sortOrder === "desc" ? -compareValue : compareValue;
    });

    setFilteredAnalyses(filtered);
  }, [analyses, sortBy, sortOrder, filterJobRole, filterScore]);

  // Get unique job roles for filter dropdown
  const getUniqueJobRoles = () => {
    const roles = analyses.map((a) => a.job_role).filter(Boolean);
    return [...new Set(roles)].sort();
  };

  // Get job role match from BERT analysis
  const getJobRoleMatch = (analysis) => {
    try {
      // Check for BERT analysis results
      if (
        analysis.analysis_results &&
        analysis.analysis_results.bert_analysis
      ) {
        const bertAnalysis = analysis.analysis_results.bert_analysis;

        // Check for job role matching in BERT analysis
        if (
          bertAnalysis.job_role_matching &&
          bertAnalysis.job_role_matching.predicted_roles &&
          bertAnalysis.job_role_matching.predicted_roles.length > 0
        ) {
          const topMatch = bertAnalysis.job_role_matching.predicted_roles[0];
          return {
            role: topMatch.role,
            score: Math.round(topMatch.match_score * 100),
          };
        }

        // Fallback to career analysis if available
        if (
          bertAnalysis.career_analysis &&
          bertAnalysis.career_analysis.career_recommendations &&
          bertAnalysis.career_analysis.career_recommendations.length > 0
        ) {
          const topCareer =
            bertAnalysis.career_analysis.career_recommendations[0];
          return {
            role: topCareer.role,
            score: Math.round(topCareer.match_score * 100),
          };
        }
      }

      // Check for legacy career analysis in main results
      if (
        analysis.analysis_results &&
        analysis.analysis_results.career_path_analysis
      ) {
        const careerAnalysis = analysis.analysis_results.career_path_analysis;
        if (
          careerAnalysis.career_recommendations &&
          careerAnalysis.career_recommendations.length > 0
        ) {
          const topCareer = careerAnalysis.career_recommendations[0];
          return {
            role: topCareer.role,
            score: Math.round(topCareer.match_score * 100),
          };
        }
      }

      return { role: "N/A", score: 0 };
    } catch (e) {
      console.error("Error extracting job role match:", e);
      return { role: "N/A", score: 0 };
    }
  };

  const handleDelete = async (analysisId, filename) => {
    if (
      !window.confirm(
        `Are you sure you want to delete the analysis for "${filename}"?\n\nThis action cannot be undone.`
      )
    ) {
      return;
    }

    try {
      setDeleteLoading(analysisId);
      await axios.delete(`/api/dashboard/user/analyses/${analysisId}`, {
        withCredentials: true,
      });

      // Remove the deleted analysis from the current list
      setAnalyses((prev) => prev.filter((a) => a.id !== analysisId));

      // Show success message
      setSuccessMessage(`Analysis for "${filename}" deleted successfully!`);
      setTimeout(() => setSuccessMessage(""), 5000);

      // If this was the last item on the page and we're not on page 1, go to previous page
      if (analyses.length === 1 && page > 1) {
        fetchAnalyses(page - 1);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Failed to delete analysis");
      setTimeout(() => setError(""), 5000);
    } finally {
      setDeleteLoading(null);
    }
  };

  const handleDownload = async (analysisId, filename) => {
    try {
      setDownloadingId(analysisId);
      const response = await axios.get(`/api/analysis/download/${analysisId}`, {
        withCredentials: true,
        responseType: "blob", // Important for file downloads
      });

      // Determine the correct filename and extension based on content type
      const contentType = response.headers["content-type"];
      let downloadFilename = `resume_analysis_report_${analysisId}.pdf`; // Default to PDF

      // Extract filename from response headers if available
      const contentDisposition = response.headers["content-disposition"];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
        );
        if (filenameMatch && filenameMatch[1]) {
          downloadFilename = filenameMatch[1].replace(/['"]/g, "");
        }
      }

      // Ensure correct extension based on content type
      if (
        contentType &&
        contentType.includes("pdf") &&
        !downloadFilename.endsWith(".pdf")
      ) {
        downloadFilename = downloadFilename.replace(/\.[^/.]+$/, ".pdf");
      } else if (
        contentType &&
        contentType.includes("json") &&
        !downloadFilename.endsWith(".json")
      ) {
        downloadFilename = downloadFilename.replace(/\.[^/.]+$/, ".json");
      }

      // Create blob with correct MIME type
      const blob = new Blob([response.data], {
        type: contentType || "application/pdf",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", downloadFilename);

      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      setError(
        `Failed to download analysis for "${filename}". Please try again.`
      );
      setTimeout(() => setError(""), 5000);
    } finally {
      setDownloadingId(null);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  useEffect(() => {
    applyFiltersAndSort();
  }, [applyFiltersAndSort]);

  if (loading)
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ minHeight: "300px" }}
      >
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );

  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <>
      <Navigation />
      <div
        className="container-fluid py-4"
        style={{ backgroundColor: "#f8f9fa", minHeight: "100vh" }}
      >
        {/* Success Message */}
        {successMessage && (
          <div className="row mb-3">
            <div className="col-12">
              <div
                className="alert alert-success alert-dismissible fade show"
                role="alert"
              >
                <i className="fas fa-check-circle me-2"></i>
                {successMessage}
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSuccessMessage("")}
                ></button>
              </div>
            </div>
          </div>
        )}
        <div className="row mb-4">
          <div className="col-12">
            <div
              className="card border-0 shadow-lg"
              style={{
                background: "linear-gradient(135deg, #6c757d 0%, #495057 100%)",
                borderRadius: "20px",
              }}
            >
              <div className="card-body p-4">
                <h1
                  className="text-white mb-3 fw-bold"
                  style={{ fontSize: "1.8rem" }}
                >
                  <i className="fas fa-history me-3"></i>
                  Your Past Analyses
                </h1>
                <p
                  className="text-white mb-0"
                  style={{ opacity: 0.9, fontSize: "1rem" }}
                >
                  Review previous resume analyses, download reports or re-run
                  analysis to track your progress.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Sort Controls */}
        {analyses.length > 0 && (
          <div
            className="card border-0 shadow-sm mb-4"
            style={{ borderRadius: "15px" }}
          >
            <div className="card-body p-4">
              <div className="row align-items-end">
                <div className="col-md-3 mb-3">
                  <label
                    className="form-label fw-bold text-muted"
                    style={{ fontSize: "0.85rem" }}
                  >
                    <i className="fas fa-sort me-1"></i>
                    Sort By
                  </label>
                  <select
                    className="form-select"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    style={{ borderRadius: "8px" }}
                  >
                    <option value="date">Date</option>
                    <option value="score">Score</option>
                    <option value="jobRole">Job Role</option>
                    <option value="filename">Filename</option>
                  </select>
                </div>

                <div className="col-md-2 mb-3">
                  <label
                    className="form-label fw-bold text-muted"
                    style={{ fontSize: "0.85rem" }}
                  >
                    <i className="fas fa-arrow-up-down me-1"></i>
                    Order
                  </label>
                  <select
                    className="form-select"
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    style={{ borderRadius: "8px" }}
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                  </select>
                </div>

                <div className="col-md-3 mb-3">
                  <label
                    className="form-label fw-bold text-muted"
                    style={{ fontSize: "0.85rem" }}
                  >
                    <i className="fas fa-briefcase me-1"></i>
                    Filter by Job Role
                  </label>
                  <select
                    className="form-select"
                    value={filterJobRole}
                    onChange={(e) => setFilterJobRole(e.target.value)}
                    style={{ borderRadius: "8px" }}
                  >
                    <option value="">All Job Roles</option>
                    {getUniqueJobRoles().map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-2 mb-3">
                  <label
                    className="form-label fw-bold text-muted"
                    style={{ fontSize: "0.85rem" }}
                  >
                    <i className="fas fa-star me-1"></i>
                    Filter by Score
                  </label>
                  <select
                    className="form-select"
                    value={filterScore}
                    onChange={(e) => setFilterScore(e.target.value)}
                    style={{ borderRadius: "8px" }}
                  >
                    <option value="">All Scores</option>
                    <option value="high">High (80-100)</option>
                    <option value="medium">Medium (60-79)</option>
                    <option value="low">Low (0-59)</option>
                  </select>
                </div>

                <div className="col-md-2 mb-3">
                  <button
                    className="btn btn-outline-secondary w-100"
                    onClick={() => {
                      setSortBy("date");
                      setSortOrder("desc");
                      setFilterJobRole("");
                      setFilterScore("");
                    }}
                    style={{ borderRadius: "8px" }}
                  >
                    <i className="fas fa-undo me-1"></i>
                    Reset
                  </button>
                </div>
              </div>

              {/* Results Summary */}
              <div className="mt-3 pt-3 border-top">
                <small className="text-muted">
                  <i className="fas fa-info-circle me-1"></i>
                  Showing {filteredAnalyses.length} of {analyses.length}{" "}
                  analyses
                  {filterJobRole && ` • Job Role: ${filterJobRole}`}
                  {filterScore &&
                    ` • Score: ${
                      filterScore === "high"
                        ? "High (80-100)"
                        : filterScore === "medium"
                        ? "Medium (60-79)"
                        : "Low (0-59)"
                    }`}
                </small>
              </div>
            </div>
          </div>
        )}

        {filteredAnalyses.length === 0 && analyses.length > 0 ? (
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "15px" }}
          >
            <div className="card-body text-center p-5">
              <div
                className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center mb-4"
                style={{ width: "80px", height: "80px" }}
              >
                <i
                  className="fas fa-filter text-white"
                  style={{ fontSize: "2rem" }}
                ></i>
              </div>
              <h4 className="text-dark mb-3" style={{ fontSize: "1.3rem" }}>
                No Results Found
              </h4>
              <p className="text-muted mb-4" style={{ fontSize: "0.95rem" }}>
                No analyses match your current filter criteria. Try adjusting
                your filters or reset them to see all analyses.
              </p>
              <button
                className="btn btn-outline-primary px-4 py-2"
                onClick={() => {
                  setSortBy("date");
                  setSortOrder("desc");
                  setFilterJobRole("");
                  setFilterScore("");
                }}
                style={{ borderRadius: "8px" }}
              >
                <i className="fas fa-undo me-2"></i>
                Reset Filters
              </button>
            </div>
          </div>
        ) : analyses.length === 0 ? (
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "15px" }}
          >
            <div className="card-body text-center p-5">
              <div
                className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-4"
                style={{ width: "80px", height: "80px" }}
              >
                <i
                  className="fas fa-file-upload text-white"
                  style={{ fontSize: "2rem" }}
                ></i>
              </div>
              <h4 className="text-dark mb-3" style={{ fontSize: "1.3rem" }}>
                No Analyses Yet
              </h4>
              <p className="text-muted mb-4" style={{ fontSize: "0.95rem" }}>
                You haven't uploaded any resumes for analysis yet. Get started
                by uploading your first resume!
              </p>
              <Link
                to="/analyze"
                className="btn btn-lg px-4 py-3 border-0 shadow-sm text-white fw-medium"
                style={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  borderRadius: "12px",
                }}
              >
                <i className="fas fa-upload me-2"></i>
                Upload Your First Resume
              </Link>
            </div>
          </div>
        ) : (
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "15px" }}
          >
            <div className="card-header border-0 bg-transparent pt-4 px-4">
              <h4
                className="card-title mb-0 fw-bold text-dark"
                style={{ fontSize: "1.2rem" }}
              >
                <div className="d-flex align-items-center justify-content-between">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-info rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "36px", height: "36px" }}
                    >
                      <i
                        className="fas fa-table text-white"
                        style={{ fontSize: "14px" }}
                      ></i>
                    </div>
                    Analysis History
                  </div>
                  <span
                    className="badge bg-primary-subtle text-primary px-3 py-2 rounded-pill"
                    style={{ fontSize: "0.8rem" }}
                  >
                    {analyses.length}{" "}
                    {analyses.length === 1 ? "Analysis" : "Analyses"}
                  </span>
                </div>
              </h4>
            </div>
            <div className="card-body px-4 pb-4">
              <div className="table-responsive">
                <table
                  className="table table-hover"
                  style={{ fontSize: "0.9rem" }}
                >
                  <thead>
                    <tr>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-calendar me-1"></i>Date
                      </th>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-file me-1"></i>File
                      </th>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-briefcase me-1"></i>Target Role
                      </th>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-star me-1"></i>Overall Score
                      </th>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-bullseye me-1"></i>Best Role Match
                      </th>
                      <th style={{ fontSize: "0.85rem" }}>
                        <i className="fas fa-cogs me-1"></i>Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAnalyses.map((a) => {
                      const roleMatch = getJobRoleMatch(a);
                      return (
                        <tr key={a.id}>
                          <td style={{ fontSize: "0.85rem" }}>
                            {new Date(a.created_at).toLocaleString("en-IN", {
                              timeZone: "Asia/Kolkata",
                              year: "numeric",
                              month: "2-digit",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                              second: "2-digit",
                              hour12: true,
                            })}{" "}
                            IST
                          </td>
                          <td
                            style={{ fontSize: "0.85rem", maxWidth: "200px" }}
                          >
                            <div className="text-truncate" title={a.filename}>
                              {a.filename}
                            </div>
                          </td>
                          <td style={{ fontSize: "0.85rem" }}>
                            <span className="badge bg-info-subtle text-info px-2 py-1">
                              {a.job_role}
                            </span>
                          </td>
                          <td style={{ fontSize: "0.85rem" }}>
                            <span
                              className={`badge ${
                                a.overall_score >= 80
                                  ? "bg-success"
                                  : a.overall_score >= 60
                                  ? "bg-warning"
                                  : "bg-danger"
                              } px-2 py-1`}
                            >
                              {a.overall_score ?? "N/A"}
                            </span>
                          </td>
                          <td style={{ fontSize: "0.85rem" }}>
                            {roleMatch.role !== "N/A" ? (
                              <div>
                                <div
                                  className="fw-bold text-primary"
                                  style={{ fontSize: "0.8rem" }}
                                >
                                  {roleMatch.role}
                                </div>
                                <div
                                  className="text-muted"
                                  style={{ fontSize: "0.75rem" }}
                                >
                                  {roleMatch.score}% match
                                </div>
                              </div>
                            ) : (
                              <span className="text-muted">
                                <i className="fas fa-robot me-1"></i>
                                BERT N/A
                              </span>
                            )}
                          </td>
                          <td>
                            <div className="btn-group btn-group-sm">
                              <Link
                                to={`/analysis/${a.id}`}
                                className="btn btn-outline-primary"
                                style={{ borderRadius: "8px 0 0 8px" }}
                              >
                                <i className="fas fa-eye me-1"></i>
                                View
                              </Link>
                              <button
                                onClick={() => handleDownload(a.id, a.filename)}
                                className="btn btn-outline-secondary"
                                style={{ borderRadius: "0" }}
                                disabled={downloadingId === a.id}
                              >
                                <i
                                  className={`fas ${
                                    downloadingId === a.id
                                      ? "fa-spinner fa-spin"
                                      : "fa-download"
                                  } me-1`}
                                ></i>
                                {downloadingId === a.id
                                  ? "Downloading..."
                                  : "Download"}
                              </button>
                              <button
                                onClick={() => handleDelete(a.id, a.filename)}
                                className="btn btn-outline-danger"
                                style={{ borderRadius: "0 8px 8px 0" }}
                                title="Delete Analysis"
                                disabled={deleteLoading === a.id}
                              >
                                {deleteLoading === a.id ? (
                                  <span
                                    className="spinner-border spinner-border-sm"
                                    role="status"
                                  ></span>
                                ) : (
                                  <i className="fas fa-trash"></i>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Results Summary */}
              <div className="mt-3 pt-3 border-top">
                <div className="row align-items-center">
                  <div className="col-md-6">
                    <small className="text-muted">
                      <i className="fas fa-info-circle me-1"></i>
                      Showing {filteredAnalyses.length} of {analyses.length}{" "}
                      total analyses
                    </small>
                  </div>
                  <div className="col-md-6 text-end">
                    {(filterJobRole ||
                      filterScore ||
                      sortBy !== "date" ||
                      sortOrder !== "desc") && (
                      <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => {
                          setSortBy("date");
                          setSortOrder("desc");
                          setFilterJobRole("");
                          setFilterScore("");
                        }}
                        style={{ borderRadius: "6px" }}
                      >
                        <i className="fas fa-undo me-1"></i>
                        Clear All Filters
                      </button>
                    )}
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

export default PastAnalyses;
