import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const AnalysisDetail = () => {
  const { id } = useParams();
  useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  const formatIndustry = (industry) => {
    if (!industry) return "";
    return industry
      .split("_") // Split at underscores
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize
      .join(" "); // Join with space
  };

  const getIndustryAnalysisFeedback = (title, analysis, results) => {
    if (!results?.industry_analysis?.[analysis]) {
      return null;
    }

    const sectionData = results.industry_analysis[analysis];

    return (
      <div className="section-feedback">
        <h4 className="mt-3" style={{ fontSize: "1.1rem" }}>
          {title}
        </h4>

        {/* Progress Bar */}
        <div className="progress mb-2">
          <div
            className={`progress-bar ${
              sectionData.score >= 90
                ? "bg-success"
                : sectionData.score >= 40
                ? "bg-warning"
                : "bg-danger"
            }`}
            role="progressbar"
            style={{ width: `${sectionData.score}%` }}
            aria-valuenow={sectionData.score}
            aria-valuemin="0"
            aria-valuemax="100"
          >
            {sectionData.score}%
          </div>
        </div>

        {/* Feedback Lists */}
        <ul className="section-feedback-list">
          {sectionData.found_skills && (
            <li>
              <strong>Found Skills:</strong>{" "}
              {sectionData.found_skills.join(", ")}
            </li>
          )}
          {sectionData.missing_important_skills && (
            <li>
              <strong>Missing Important Skills:</strong>{" "}
              {sectionData.missing_important_skills.join(", ")}
            </li>
          )}
          {sectionData.found_sections && (
            <li>
              <strong>Found Sections:</strong>{" "}
              {sectionData.found_sections.join(", ")}
            </li>
          )}
          {sectionData.missing_sections && (
            <li>
              <strong>Missing Sections:</strong>{" "}
              {sectionData.missing_sections.join(", ")}
            </li>
          )}
          {sectionData.found_verbs && (
            <li>
              <strong>Found Verbs:</strong> {sectionData.found_verbs.join(", ")}
            </li>
          )}
          {sectionData.recommended_verbs && (
            <li>
              <strong>Recommended Verbs:</strong>{" "}
              {sectionData.recommended_verbs.join(", ")}
            </li>
          )}
          {sectionData.achievement_phrases_found && (
            <li>
              <strong>Achievement Phrases Found:</strong>{" "}
              {sectionData.achievement_phrases_found.join(", ")}
            </li>
          )}
        </ul>
      </div>
    );
  };

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`/api/dashboard/user/analyses/${id}`, {
          withCredentials: true,
        });
        setAnalysis(res.data.analysis);
      } catch (err) {
        setError(err.response?.data?.error || "Failed to load analysis");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [id]);

  const handleDownload = async () => {
    try {
      setDownloading(true);
      const response = await axios.get(`/api/analysis/download/${id}`, {
        withCredentials: true,
        responseType: "blob", // Important for file downloads
      });

      // Determine the correct filename and extension based on content type
      const contentType = response.headers["content-type"];
      let filename = `resume_analysis_report_${id}.pdf`; // Default to PDF

      // Extract filename from response headers if available
      const contentDisposition = response.headers["content-disposition"];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(
          /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
        );
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, "");
        }
      }

      // Ensure correct extension based on content type
      if (
        contentType &&
        contentType.includes("pdf") &&
        !filename.endsWith(".pdf")
      ) {
        filename = filename.replace(/\.[^/.]+$/, ".pdf");
      } else if (
        contentType &&
        contentType.includes("json") &&
        !filename.endsWith(".json")
      ) {
        filename = filename.replace(/\.[^/.]+$/, ".json");
      }

      // Create blob with correct MIME type
      const blob = new Blob([response.data], {
        type: contentType || "application/pdf",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);

      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download analysis. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

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

  if (error)
    return (
      <div className="container py-4">
        <div className="alert alert-danger">{error}</div>
      </div>
    );

  if (!analysis)
    return (
      <div className="container py-4">
        <div className="alert alert-warning">No analysis found.</div>
      </div>
    );

  const results = analysis.analysis_results || {};

  return (
    <div
      className="container-fluid py-4"
      style={{ backgroundColor: "#f8f9fa", minHeight: "100vh" }}
    >
      <div className="row mb-3">
        <div className="col-12">
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "12px" }}
          >
            <div className="card-body p-4">
              <h3 className="fw-bold mb-1" style={{ fontSize: "1.4rem" }}>
                Analysis Details
              </h3>
              <p className="text-muted mb-0" style={{ fontSize: "0.9rem" }}>
                File: <strong>{analysis.filename}</strong> — Job Role:{" "}
                <strong>{analysis.job_role}</strong>
              </p>
              <p className="text-muted" style={{ fontSize: "0.85rem" }}>
                Analyzed on: {new Date(analysis.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* BERT Analysis Card */}
        {results.bert_analysis && (
          <div className="col-lg-6 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "12px" }}
            >
              <div className="card-header">
                <h4 className="mb-0" style={{ fontSize: "1.2rem" }}>
                  <i className="fas fa-brain text-primary me-2"></i>
                  AI-Enhanced Analysis
                  <span
                    className="badge bg-primary ms-2"
                    style={{ fontSize: "0.7rem" }}
                  >
                    BERT
                  </span>
                </h4>
              </div>
              <div className="card-body p-4">
                <div className="text-center mb-4">
                  <h3 style={{ fontSize: "1.2rem" }}>BERT Score</h3>
                  <div
                    className="d-inline-flex align-items-center justify-content-center rounded-circle border border-3 p-3"
                    style={{ width: "100px", height: "100px" }}
                  >
                    <span
                      className={`fs-2 fw-bold ${
                        results.bert_analysis.overall_score >= 70
                          ? "text-success"
                          : results.bert_analysis.overall_score >= 50
                          ? "text-warning"
                          : "text-danger"
                      }`}
                    >
                      {results.bert_analysis.overall_score ?? "N/A"}%
                    </span>
                  </div>
                </div>

                {/* Experience Level Prediction */}
                {results.bert_analysis.experience_level && (
                  <div className="mb-3">
                    <h6 className="mb-2" style={{ fontSize: "0.95rem" }}>
                      <i className="fas fa-user-tie me-1"></i>Experience Level
                    </h6>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="badge bg-info px-3 py-2">
                        {results.bert_analysis.experience_level.predicted_level}
                      </span>
                      <small className="text-muted">
                        {
                          results.bert_analysis.experience_level
                            .years_experience
                        }{" "}
                        years
                      </small>
                    </div>
                  </div>
                )}

                <hr className="my-3" />

                {/* Content Quality */}
                {results.bert_analysis.content_quality && (
                  <div className="mb-3">
                    <h6 className="mb-2" style={{ fontSize: "0.95rem" }}>
                      <i className="fas fa-star me-1"></i>Content Quality
                    </h6>
                    <div className="row g-2">
                      <div className="col-6">
                        <div className="text-center p-2 bg-light rounded">
                          <div className="fw-bold text-primary">
                            {Math.round(
                              results.bert_analysis.content_quality
                                .overall_quality
                            )}
                            %
                          </div>
                          <small className="text-muted">Overall</small>
                        </div>
                      </div>
                      <div className="col-6">
                        <div className="text-center p-2 bg-light rounded">
                          <div className="fw-bold text-success">
                            {Math.round(
                              results.bert_analysis.content_quality
                                .action_verb_usage
                            )}
                            %
                          </div>
                          <small className="text-muted">Action Verbs</small>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <hr className="my-3" />

                {/* Skills Analysis */}
                {results.bert_analysis.skills_analysis && (
                  <div className="mb-3">
                    <h6 className="mb-2" style={{ fontSize: "0.95rem" }}>
                      <i className="fas fa-code me-1"></i>Semantic Skills Found
                    </h6>
                    <div className="d-flex justify-content-between mb-2">
                      <small>Total Skills:</small>
                      <span className="badge bg-primary">
                        {
                          results.bert_analysis.skills_analysis
                            .total_skills_found
                        }
                      </span>
                    </div>

                    {results.bert_analysis.skills_analysis.top_skills &&
                      results.bert_analysis.skills_analysis.top_skills.length >
                        0 && (
                        <div>
                          <small className="text-muted mb-1 d-block">
                            Top Skills (AI Confidence):
                          </small>
                          {results.bert_analysis.skills_analysis.top_skills
                            .slice(0, 5)
                            .map((skill, i) => (
                              <div
                                key={i}
                                className="d-flex justify-content-between align-items-center mb-1"
                              >
                                <small className="text-primary">
                                  {skill.skill}
                                </small>
                                <div className="d-flex align-items-center">
                                  <div
                                    className="progress me-2"
                                    style={{ width: "40px", height: "4px" }}
                                  >
                                    <div
                                      className="progress-bar bg-primary"
                                      style={{
                                        width: `${skill.confidence * 100}%`,
                                      }}
                                    ></div>
                                  </div>
                                  <small
                                    className="text-muted"
                                    style={{ fontSize: "0.7rem" }}
                                  >
                                    {Math.round(skill.confidence * 100)}%
                                  </small>
                                </div>
                              </div>
                            ))}
                        </div>
                      )}
                  </div>
                )}

                <hr className="my-3" />

                {/* Job Role Matching */}
                {results.bert_analysis.job_role_matching &&
                  results.bert_analysis.job_role_matching.predicted_roles && (
                    <div className="mb-3">
                      <h6 className="mb-2" style={{ fontSize: "0.95rem" }}>
                        <i className="fas fa-bullseye me-1"></i>Job Role Match
                      </h6>
                      {results.bert_analysis.job_role_matching.predicted_roles
                        .slice(0, 3)
                        .map((role, i) => (
                          <div
                            key={i}
                            className="d-flex justify-content-between align-items-center mb-1"
                          >
                            <small className="text-dark">{role.role}</small>
                            <span
                              className={`badge ${
                                role.match_score > 0.5
                                  ? "bg-success"
                                  : role.match_score > 0.3
                                  ? "bg-warning"
                                  : "bg-secondary"
                              }`}
                              style={{ fontSize: "0.7rem" }}
                            >
                              {Math.round(role.match_score * 100)}%
                            </span>
                          </div>
                        ))}
                    </div>
                  )}

                <hr className="my-3" />

                {/* BERT Suggestions */}
                {results.bert_analysis.semantic_suggestions &&
                  results.bert_analysis.semantic_suggestions.length > 0 && (
                    <div className="mb-2">
                      <h6 className="mb-2" style={{ fontSize: "0.95rem" }}>
                        <i className="fas fa-lightbulb me-1"></i>AI Insights
                      </h6>
                      <ul className="list-unstyled">
                        {results.bert_analysis.semantic_suggestions
                          .slice(0, 3)
                          .map((suggestion, i) => (
                            <li key={i} className="mb-1">
                              <small>
                                <i
                                  className="fas fa-arrow-right text-primary me-1"
                                  style={{ fontSize: "0.6rem" }}
                                ></i>
                                {suggestion}
                              </small>
                            </li>
                          ))}
                      </ul>
                    </div>
                  )}

                {/* Enhanced Score Display */}
                {results.enhanced_score &&
                  results.enhanced_score !==
                    results.bert_analysis.overall_score && (
                    <div className="mt-3 p-2 bg-light rounded">
                      <div className="d-flex justify-content-between align-items-center">
                        <small className="fw-bold">Enhanced Score:</small>
                        <span className="badge bg-success">
                          {results.enhanced_score}
                        </span>
                      </div>
                      <small className="text-muted">
                        Combined traditional + AI analysis
                      </small>
                    </div>
                  )}
              </div>
            </div>
          </div>
        )}

        {/* Industry Analysis Card */}
        <div
          className={`${results.bert_analysis ? "col-lg-6" : "col-lg-6"} mb-3`}
        >
          <div
            className="card h-100 border-0 shadow-sm"
            style={{ borderRadius: "12px" }}
          >
            <div className="card-header">
              <h4 className="mb-0" style={{ fontSize: "1.2rem" }}>
                Industry Analysis:{" "}
                {formatIndustry(results.industry_analysis?.industry)}
              </h4>
            </div>
            <div className="card-body p-4">
              <div className="text-center mb-4">
                <h3 style={{ fontSize: "1.2rem" }}>Industry Score</h3>
                <div
                  className="d-inline-flex align-items-center justify-content-center rounded-circle border border-3 p-3"
                  style={{ width: "100px", height: "100px" }}
                >
                  <span
                    className={`fs-2 fw-bold ${
                      results.industry_analysis?.overall_score >= 70
                        ? "text-success"
                        : results.industry_analysis?.overall_score >= 50
                        ? "text-warning"
                        : "text-danger"
                    }`}
                  >
                    {results.industry_analysis?.overall_score}%
                  </span>
                </div>
              </div>

              {getIndustryAnalysisFeedback(
                "Skills Analysis",
                "skills_analysis",
                results
              )}
              {getIndustryAnalysisFeedback(
                "Sections Analysis",
                "sections_analysis",
                results
              )}
              {getIndustryAnalysisFeedback(
                "Verbs Analysis",
                "verbs_analysis",
                results
              )}
              {getIndustryAnalysisFeedback(
                "Achievements",
                "achievements_analysis",
                results
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Skill Gap Analysis & Learning Path Section */}
      {results.industry_analysis?.skill_gap_analysis && (
        <div className="row mb-4">
          <div className="col-12">
            <div
              className="card border-0 shadow-sm"
              style={{ borderRadius: "12px" }}
            >
              <div className="card-body p-4">
                <h4 className="mb-4" style={{ fontSize: "1.2rem" }}>
                  <i className="fas fa-graduation-cap text-primary me-2"></i>
                  Skill Gap Analysis & Learning Path
                  <span
                    className="badge bg-primary ms-2"
                    style={{ fontSize: "0.7rem" }}
                  >
                    NEW
                  </span>
                </h4>

                <div className="row">
                  {/* Gap Overview */}
                  <div className="col-lg-4 mb-3">
                    <div className="p-3 bg-light rounded">
                      <h6 className="mb-2" style={{ fontSize: "0.9rem" }}>
                        Gap Overview
                      </h6>
                      <div className="d-flex justify-content-between mb-1">
                        <small>Skills Present:</small>
                        <small className="text-success">
                          {
                            results.industry_analysis.skill_gap_analysis
                              .skills_present
                          }
                        </small>
                      </div>
                      <div className="d-flex justify-content-between mb-1">
                        <small>Skills Missing:</small>
                        <small className="text-danger">
                          {
                            results.industry_analysis.skill_gap_analysis
                              .skills_missing
                          }
                        </small>
                      </div>
                      <div className="d-flex justify-content-between mb-2">
                        <small>Match Rate:</small>
                        <small className="fw-bold">
                          {
                            results.industry_analysis.skill_gap_analysis
                              .skill_match_percentage
                          }
                          %
                        </small>
                      </div>
                      <div className="progress" style={{ height: "8px" }}>
                        <div
                          className={`progress-bar ${
                            results.industry_analysis.skill_gap_analysis
                              .skill_match_percentage >= 80
                              ? "bg-success"
                              : results.industry_analysis.skill_gap_analysis
                                  .skill_match_percentage >= 60
                              ? "bg-warning"
                              : "bg-danger"
                          }`}
                          style={{
                            width: `${results.industry_analysis.skill_gap_analysis.skill_match_percentage}%`,
                          }}
                        ></div>
                      </div>
                      <small className="text-muted mt-1 d-block">
                        Gap Severity:{" "}
                        <span
                          className={`badge ${
                            results.industry_analysis.skill_gap_analysis
                              .gap_severity === "minimal"
                              ? "bg-success"
                              : results.industry_analysis.skill_gap_analysis
                                  .gap_severity === "moderate"
                              ? "bg-warning"
                              : "bg-danger"
                          }`}
                        >
                          {
                            results.industry_analysis.skill_gap_analysis
                              .gap_severity
                          }
                        </span>
                      </small>
                    </div>
                  </div>

                  {/* Priority Skills */}
                  <div className="col-lg-4 mb-3">
                    <div className="p-3 bg-light rounded">
                      <h6 className="mb-2" style={{ fontSize: "0.9rem" }}>
                        Priority Skills to Learn
                      </h6>
                      {results.industry_analysis.skill_gap_analysis
                        .priority_skills_to_learn?.length > 0 ? (
                        <div>
                          {results.industry_analysis.skill_gap_analysis.priority_skills_to_learn.map(
                            (skill, i) => (
                              <div key={i} className="mb-2">
                                <div className="d-flex justify-content-between align-items-center">
                                  <small className="fw-bold text-primary">
                                    {skill.skill}
                                  </small>
                                  <small className="text-muted">
                                    {skill.estimated_time}
                                  </small>
                                </div>
                                <small className="text-muted d-block">
                                  {skill.reason}
                                </small>
                              </div>
                            )
                          )}
                        </div>
                      ) : (
                        <small className="text-muted">
                          Great! You have most essential skills.
                        </small>
                      )}
                    </div>
                  </div>

                  {/* Learning Time Estimate */}
                  <div className="col-lg-4 mb-3">
                    <div className="p-3 bg-light rounded">
                      <h6 className="mb-2" style={{ fontSize: "0.9rem" }}>
                        Learning Time Estimate
                      </h6>
                      <div className="text-center mb-2">
                        <div className="display-6 text-primary">
                          {results.industry_analysis.skill_gap_analysis
                            .estimated_learning_time?.estimated_months || 0}
                        </div>
                        <small className="text-muted">months</small>
                      </div>
                      <div className="d-flex justify-content-between">
                        <small>Total Hours:</small>
                        <small>
                          {results.industry_analysis.skill_gap_analysis
                            .estimated_learning_time?.total_hours || 0}
                          h
                        </small>
                      </div>
                      <small className="text-muted d-block mt-1">
                        Career Impact:{" "}
                        <span className="badge bg-info">
                          {
                            results.industry_analysis.skill_gap_analysis
                              .career_impact?.career_advancement_potential
                          }
                        </span>
                      </small>
                      <small className="text-success d-block mt-1">
                        {
                          results.industry_analysis.skill_gap_analysis
                            .career_impact?.salary_increase_potential
                        }
                      </small>
                    </div>
                  </div>
                </div>

                {/* Quick Wins */}
                {results.industry_analysis.skill_gap_analysis.quick_wins
                  ?.length > 0 && (
                  <div className="mt-3">
                    <h6 className="mb-2" style={{ fontSize: "0.9rem" }}>
                      <i className="fas fa-bolt text-warning me-1"></i>Quick
                      Wins (Learn These First!)
                    </h6>
                    <div className="row">
                      {results.industry_analysis.skill_gap_analysis.quick_wins.map(
                        (win, i) => (
                          <div key={i} className="col-md-4 mb-2">
                            <div className="p-2 border rounded bg-warning bg-opacity-10">
                              <div className="d-flex justify-content-between">
                                <small className="fw-bold">{win.skill}</small>
                                <small className="text-success">
                                  {win.learning_time}
                                </small>
                              </div>
                              <small className="text-muted d-block">
                                {win.course} ({win.provider})
                              </small>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* Learning Path */}
                {results.industry_analysis.skill_gap_analysis.learning_path
                  ?.length > 0 && (
                  <div className="mt-4">
                    <h6 className="mb-3" style={{ fontSize: "0.9rem" }}>
                      <i className="fas fa-route text-info me-1"></i>
                      Personalized Learning Path
                    </h6>
                    <div className="row">
                      {results.industry_analysis.skill_gap_analysis.learning_path
                        .slice(0, 6)
                        .map((step, i) => (
                          <div key={i} className="col-lg-6 mb-3">
                            <div className="card border-0 bg-light">
                              <div className="card-body p-3">
                                <div className="d-flex align-items-center mb-2">
                                  <div
                                    className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2"
                                    style={{
                                      width: "24px",
                                      height: "24px",
                                      fontSize: "0.7rem",
                                    }}
                                  >
                                    {step.step}
                                  </div>
                                  <h6
                                    className="mb-0 text-capitalize"
                                    style={{ fontSize: "0.85rem" }}
                                  >
                                    {step.skill}
                                  </h6>
                                  <span
                                    className={`badge ms-auto ${
                                      step.priority === "high"
                                        ? "bg-danger"
                                        : step.priority === "medium"
                                        ? "bg-warning"
                                        : "bg-secondary"
                                    }`}
                                    style={{ fontSize: "0.6rem" }}
                                  >
                                    {step.priority}
                                  </span>
                                </div>

                                {step.recommended_courses &&
                                  step.recommended_courses.length > 0 && (
                                    <div className="mb-2">
                                      {step.recommended_courses
                                        .slice(0, 2)
                                        .map((course, courseIndex) => (
                                          <div
                                            key={courseIndex}
                                            className="course-item mb-2 p-2 bg-white rounded border"
                                          >
                                            <div className="d-flex justify-content-between align-items-start mb-1">
                                              <small
                                                className="fw-bold text-primary"
                                                style={{ fontSize: "0.8rem" }}
                                              >
                                                {course.name.length > 25
                                                  ? course.name.substring(
                                                      0,
                                                      25
                                                    ) + "..."
                                                  : course.name}
                                              </small>
                                              <div className="d-flex align-items-center gap-1">
                                                {course.type === "video" && (
                                                  <i
                                                    className="fab fa-youtube text-danger"
                                                    title="YouTube Video"
                                                  ></i>
                                                )}
                                                {course.type === "course" && (
                                                  <i
                                                    className="fas fa-graduation-cap text-primary"
                                                    title="Online Course"
                                                  ></i>
                                                )}
                                                {course.rating && (
                                                  <small
                                                    className="text-warning"
                                                    style={{
                                                      fontSize: "0.7rem",
                                                    }}
                                                  >
                                                    <i className="fas fa-star"></i>{" "}
                                                    {course.rating}
                                                  </small>
                                                )}
                                              </div>
                                            </div>
                                            <div className="d-flex justify-content-between align-items-center mb-1">
                                              <small
                                                className="text-muted"
                                                style={{ fontSize: "0.75rem" }}
                                              >
                                                {course.provider} •{" "}
                                                {course.duration}
                                              </small>
                                            </div>
                                            <div>
                                              <a
                                                href={course.link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn btn-sm btn-outline-primary"
                                                style={{
                                                  fontSize: "0.7rem",
                                                  padding: "2px 8px",
                                                }}
                                              >
                                                {course.type === "video" ? (
                                                  <>
                                                    <i className="fab fa-youtube me-1"></i>
                                                    Watch Video
                                                  </>
                                                ) : (
                                                  <>
                                                    <i className="fas fa-external-link-alt me-1"></i>
                                                    Take Course
                                                  </>
                                                )}
                                              </a>
                                            </div>
                                          </div>
                                        ))}
                                    </div>
                                  )}

                                {step.recommended_course &&
                                  !step.recommended_courses && (
                                    <div className="mb-2">
                                      <small className="fw-bold text-primary d-block">
                                        {step.recommended_course.name}
                                      </small>
                                      <small className="text-muted">
                                        {step.recommended_course.provider} •{" "}
                                        {step.recommended_course.duration}
                                      </small>
                                    </div>
                                  )}

                                <small className="text-muted d-block mb-2">
                                  {step.description}
                                </small>

                                {step.certifications?.length > 0 && (
                                  <div>
                                    <small className="text-success fw-bold">
                                      Certifications:{" "}
                                    </small>
                                    <small className="text-muted">
                                      {step.certifications
                                        .slice(0, 2)
                                        .join(", ")}
                                    </small>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Career Path Recommendations Section */}
      {results &&
        results.career_path_analysis &&
        !results.career_path_analysis.error && (
          <div className="row mb-4">
            <div className="col-12">
              <div
                className="card border-0 shadow-sm"
                style={{ borderRadius: "12px" }}
              >
                <div className="card-header bg-primary text-white">
                  <h4 className="mb-0" style={{ fontSize: "1.2rem" }}>
                    <i className="fas fa-route me-2"></i>
                    Career Path Recommendations
                  </h4>
                </div>
                <div className="card-body p-4">
                  {/* Analysis Summary */}
                  <div className="row mb-4">
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <h5 className="text-primary mb-1">
                          {results.career_path_analysis
                            ?.total_experience_years || 0}
                        </h5>
                        <small className="text-muted">Years Experience</small>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <h5 className="text-success mb-1">
                          {results.career_path_analysis?.career_recommendations
                            ?.length || 0}
                        </h5>
                        <small className="text-muted">Career Matches</small>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <h5 className="text-info mb-1">
                          {results.career_path_analysis
                            ?.total_skills_analyzed || 0}
                        </h5>
                        <small className="text-muted">Skills Analyzed</small>
                      </div>
                    </div>
                  </div>

                  {/* Top Career Recommendation */}
                  {results.career_path_analysis?.analysis_summary && (
                    <div className="alert alert-success border-0 shadow-sm mb-4">
                      <h6 className="mb-2">
                        <i className="fas fa-star text-warning me-2"></i>
                        Top Career Match:{" "}
                        {results.career_path_analysis.analysis_summary
                          ?.top_career_match || "Not available"}
                      </h6>
                      <p className="mb-2">
                        <strong>Recommended Level:</strong>{" "}
                        {results.career_path_analysis.analysis_summary
                          ?.recommended_level || "Entry Level"}
                      </p>
                      {results.career_path_analysis.analysis_summary
                        ?.skill_development_priority?.length > 0 && (
                        <div>
                          <strong>Priority Skills to Develop:</strong>
                          <div className="mt-1">
                            {results.career_path_analysis.analysis_summary?.skill_development_priority?.map(
                              (skill, index) => (
                                <span
                                  key={index}
                                  className="badge bg-warning text-dark me-1 mb-1"
                                >
                                  {skill}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Career Path Cards */}
                  {results.career_path_analysis?.career_recommendations &&
                    results.career_path_analysis.career_recommendations.length >
                      0 && (
                      <div className="row">
                        {results.career_path_analysis.career_recommendations
                          .slice(0, 3)
                          .map((career, index) => (
                            <div key={index} className="col-md-4 mb-3">
                              <div className="card border-0 shadow-sm h-100">
                                <div className="card-body">
                                  <div className="d-flex justify-content-between align-items-start mb-3">
                                    <h6
                                      className="card-title mb-0"
                                      style={{ fontSize: "0.95rem" }}
                                    >
                                      {career.career_path}
                                    </h6>
                                    <span
                                      className={`badge ${
                                        career.overall_score >= 70
                                          ? "bg-success"
                                          : career.overall_score >= 50
                                          ? "bg-warning"
                                          : "bg-secondary"
                                      }`}
                                    >
                                      {career.overall_score}% Match
                                    </span>
                                  </div>

                                  {/* Skill Match Progress */}
                                  <div className="mb-3">
                                    <div className="d-flex justify-content-between mb-1">
                                      <small>Skills Match</small>
                                      <small>
                                        {career.skill_match.match_percentage}%
                                      </small>
                                    </div>
                                    <div
                                      className="progress"
                                      style={{ height: "6px" }}
                                    >
                                      <div
                                        className={`progress-bar ${
                                          career.skill_match.match_percentage >=
                                          70
                                            ? "bg-success"
                                            : career.skill_match
                                                .match_percentage >= 50
                                            ? "bg-warning"
                                            : "bg-danger"
                                        }`}
                                        style={{
                                          width: `${career.skill_match.match_percentage}%`,
                                        }}
                                      ></div>
                                    </div>
                                  </div>

                                  {/* Recommended Level */}
                                  {career.level_recommendations
                                    ?.recommended_level && (
                                    <div className="mb-3">
                                      <small className="text-primary fw-bold">
                                        Recommended Level:
                                      </small>
                                      <div className="mt-1">
                                        <span className="badge bg-primary">
                                          {
                                            career.level_recommendations
                                              .recommended_level.level
                                          }
                                        </span>
                                        <small className="text-muted ms-2">
                                          (
                                          {
                                            career.level_recommendations
                                              .recommended_level.overall_score
                                          }
                                          % fit)
                                        </small>
                                      </div>
                                    </div>
                                  )}

                                  {/* Industries */}
                                  {career.industries &&
                                    career.industries.length > 0 && (
                                      <div className="mb-3">
                                        <small className="text-muted fw-bold">
                                          Industries:
                                        </small>
                                        <div className="mt-1">
                                          {career.industries
                                            .slice(0, 3)
                                            .map((industry, i) => (
                                              <span
                                                key={i}
                                                className="badge bg-light text-dark me-1 mb-1"
                                              >
                                                {industry}
                                              </span>
                                            ))}
                                        </div>
                                      </div>
                                    )}

                                  {/* Missing Skills */}
                                  {career.skill_match.missing_skills?.length >
                                    0 && (
                                    <div className="mb-2">
                                      <small className="text-warning fw-bold">
                                        Skills to Develop:
                                      </small>
                                      <div className="mt-1">
                                        <small className="text-muted">
                                          {career.skill_match.missing_skills
                                            .slice(0, 3)
                                            .join(", ")}
                                          {career.skill_match.missing_skills
                                            .length > 3 && "..."}
                                        </small>
                                      </div>
                                    </div>
                                  )}

                                  {/* Career Progression Preview */}
                                  {career.level_recommendations?.all_levels && (
                                    <div className="mt-3">
                                      <small className="text-success fw-bold">
                                        Career Progression:
                                      </small>
                                      <div className="mt-1">
                                        {career.level_recommendations.all_levels
                                          .filter((level, idx) => idx < 3)
                                          .map((level, i) => (
                                            <div
                                              key={i}
                                              className="d-flex justify-content-between align-items-center py-1"
                                            >
                                              <small
                                                className="text-muted"
                                                style={{ fontSize: "0.75rem" }}
                                              >
                                                {level.level}
                                              </small>
                                              <small
                                                className="text-primary"
                                                style={{ fontSize: "0.7rem" }}
                                              >
                                                {level.overall_score}%
                                              </small>
                                            </div>
                                          ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    )}

                  {/* Additional Career Options */}
                  {results.career_path_analysis.career_recommendations?.length >
                    3 && (
                    <div className="mt-4">
                      <h6 className="mb-3" style={{ fontSize: "0.95rem" }}>
                        Other Career Options
                      </h6>
                      <div className="row">
                        {results.career_path_analysis?.career_recommendations
                          ?.slice(3, 6)
                          .map((career, index) => (
                            <div key={index} className="col-md-6 mb-2">
                              <div className="d-flex justify-content-between align-items-center p-2 bg-light rounded">
                                <div>
                                  <small className="fw-bold">
                                    {career.career_path}
                                  </small>
                                  <br />
                                  <small className="text-muted">
                                    {career.skill_match.match_percentage}%
                                    skills match
                                  </small>
                                </div>
                                <span
                                  className={`badge ${
                                    career.overall_score >= 70
                                      ? "bg-success"
                                      : career.overall_score >= 50
                                      ? "bg-warning"
                                      : "bg-secondary"
                                  }`}
                                >
                                  {career.overall_score}%
                                </span>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

      {/* Suggestions and Strengths Row */}
      <div className="row">
        <div className="col-lg-6 mb-3">
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "12px" }}
          >
            <div className="card-body p-4">
              <h5 className="mb-3" style={{ fontSize: "1.1rem" }}>
                <i className="fas fa-lightbulb text-warning me-2"></i>
                Suggestions
              </h5>
              {results.suggestions && results.suggestions.length > 0 ? (
                <ul className="list-unstyled">
                  {results.suggestions.map((s, i) => (
                    <li key={i} className="mb-2">
                      <i className="fas fa-arrow-right text-primary me-2"></i>
                      {s}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="alert alert-secondary">
                  No suggestions stored.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-lg-6 mb-3">
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "12px" }}
          >
            <div className="card-body p-4">
              <h5 className="mb-3" style={{ fontSize: "1.1rem" }}>
                <i className="fas fa-star text-success me-2"></i>Strengths
              </h5>
              {results.strengths && results.strengths.length > 0 ? (
                <ul className="list-unstyled">
                  {results.strengths.map((s, i) => (
                    <li key={i} className="mb-2">
                      <i className="fas fa-check text-success me-2"></i>
                      {s}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="alert alert-secondary">
                  No strengths stored.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Actions Row */}
      <div className="row">
        <div className="col-12">
          <div
            className="card border-0 shadow-sm"
            style={{ borderRadius: "12px" }}
          >
            <div className="card-body p-4 text-center">
              <Link to="/history" className="btn btn-outline-primary me-3">
                <i className="fas fa-arrow-left me-2"></i>Back to History
              </Link>
              <button
                onClick={handleDownload}
                className="btn btn-primary"
                disabled={downloading}
              >
                <i
                  className={`fas ${
                    downloading ? "fa-spinner fa-spin" : "fa-download"
                  } me-2`}
                ></i>
                {downloading ? "Downloading..." : "Download Report"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDetail;
