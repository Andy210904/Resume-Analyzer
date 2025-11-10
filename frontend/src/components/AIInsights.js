import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";

const AIInsights = ({ resumeText = "", jobRole = "software_engineer" }) => {
  const [loading, setLoading] = useState(false);
  const [bulletAnalyses, setBulletAnalyses] = useState([]);
  const [aiAvailable, setAiAvailable] = useState(false);

  // Check AI availability on component mount
  useEffect(() => {
    checkAIStatus();
  }, []);

  const analyzeBulletPoints = async () => {
    if (!resumeText) return;

    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:5000/api/ai-insights/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            resume_text: resumeText,
            job_role: jobRole,
          }),
        }
      );

      const data = await response.json();

      if (data.available) {
        setBulletAnalyses(data.bullet_analyses || []);
        setAiAvailable(true);
      } else {
        setAiAvailable(false);
        setBulletAnalyses([]);
      }
    } catch (error) {
      console.error("Error analyzing bullet points:", error);
      setAiAvailable(false);
    } finally {
      setLoading(false);
    }
  };

  const checkAIStatus = async () => {
    try {
      const response = await fetch(
        "http://localhost:5000/api/ai-insights/status"
      );
      const data = await response.json();
      setAiAvailable(data.available);
    } catch (error) {
      console.error("Error checking AI status:", error);
      setAiAvailable(false);
    }
  };

  // Auto-analyze when resume text is provided
  useEffect(() => {
    if (resumeText && resumeText.length > 50) {
      analyzeBulletPoints();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resumeText]);

  const getClassificationBadge = (classification) => {
    const badges = {
      "responsibility-driven": "badge bg-warning text-dark",
      "achievement-driven": "badge bg-success",
      mixed: "badge bg-info",
    };
    return badges[classification] || "badge bg-secondary";
  };

  const getImpactScoreColor = (score) => {
    if (score >= 0.7) return "text-success";
    if (score >= 0.5) return "text-warning";
    return "text-danger";
  };

  const InstallationGuide = () => (
    <div className="card border-warning">
      <div className="card-header bg-warning text-dark">
        <h5 className="card-title mb-0">
          <i className="fas fa-robot me-2"></i>
          AI Insights Feature
        </h5>
      </div>
      <div className="card-body">
        <p className="mb-3">
          <strong>Generative AI features are not available.</strong> Install the
          required packages to enable:
        </p>
        <ul className="list-unstyled">
          <li>• AI-powered bullet point rewriting</li>
          <li>• Personalized improvement suggestions</li>
          <li>• Impact-focused content enhancement</li>
        </ul>

        <div className="alert alert-info">
          <h6>Installation Instructions:</h6>
          <code>pip install transformers torch sentence-transformers</code>
          <p className="mt-2 mb-0 small">
            <strong>Note:</strong> This will download ~2GB of AI models for
            optimal performance.
          </p>
        </div>

        <button className="btn btn-primary" onClick={checkAIStatus}>
          <i className="fas fa-sync-alt me-2"></i>
          Check Again
        </button>
      </div>
    </div>
  );

  const BulletPointCard = ({ analysis, index }) => (
    <div className="card mb-3 border-start border-primary border-3">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start mb-3">
          <h6 className="card-subtitle text-muted">
            Bullet Point #{index + 1}
          </h6>
          <div className="d-flex gap-2">
            <span className={getClassificationBadge(analysis.classification)}>
              {analysis.classification.replace("-", " ").toUpperCase()}
            </span>
            <span
              className={`badge ${
                analysis.impact_score >= 0.7
                  ? "bg-success"
                  : analysis.impact_score >= 0.5
                  ? "bg-warning text-dark"
                  : "bg-danger"
              }`}
            >
              Impact: {(analysis.impact_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="mb-3">
          <h6>Original:</h6>
          <p className="text-muted border-start border-3 border-secondary ps-3 mb-0">
            {analysis.original_text}
          </p>
        </div>

        {analysis.weakness_reasons.length > 0 && (
          <div className="mb-3">
            <h6 className="text-warning">
              <i className="fas fa-exclamation-triangle me-2"></i>
              Issues Identified:
            </h6>
            <ul className="list-unstyled">
              {analysis.weakness_reasons.map((reason, idx) => (
                <li key={idx} className="small text-muted">
                  • {reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mb-3">
          <h6 className="text-success">
            <i className="fas fa-magic me-2"></i>
            AI Rewrite:
          </h6>
          <div className="p-3 bg-light border-start border-3 border-success rounded">
            <p className="mb-0 text-dark">{analysis.ai_rewrite}</p>
          </div>
        </div>

        {analysis.suggested_improvements.length > 0 && (
          <div className="mb-3">
            <h6 className="text-primary">
              <i className="fas fa-lightbulb me-2"></i>
              Improvement Tips:
            </h6>
            <ul className="list-unstyled">
              {analysis.suggested_improvements.map((suggestion, idx) => (
                <li key={idx} className="small text-muted mb-1">
                  <i className="fas fa-arrow-right text-primary me-2"></i>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="d-flex justify-content-between align-items-center">
          <small className="text-muted">
            Confidence: {(analysis.confidence * 100).toFixed(0)}%
          </small>
          <button
            className="btn btn-sm btn-outline-primary"
            onClick={() => navigator.clipboard.writeText(analysis.ai_rewrite)}
          >
            <i className="fas fa-copy me-1"></i>
            Copy Rewrite
          </button>
        </div>
      </div>
    </div>
  );

  const SummaryStats = () => {
    const responsibilityDriven = bulletAnalyses.filter(
      (b) => b.classification === "responsibility-driven"
    ).length;
    const achievementDriven = bulletAnalyses.filter(
      (b) => b.classification === "achievement-driven"
    ).length;
    const averageImpact =
      bulletAnalyses.reduce((acc, b) => acc + b.impact_score, 0) /
      bulletAnalyses.length;

    return (
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card text-center border-warning">
            <div className="card-body">
              <h3 className="text-warning">{responsibilityDriven}</h3>
              <small className="text-muted">Responsibility-Driven</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center border-success">
            <div className="card-body">
              <h3 className="text-success">{achievementDriven}</h3>
              <small className="text-muted">Achievement-Driven</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center border-info">
            <div className="card-body">
              <h3 className="text-info">{bulletAnalyses.length}</h3>
              <small className="text-muted">Total Analyzed</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center border-primary">
            <div className="card-body">
              <h3 className={`${getImpactScoreColor(averageImpact)}`}>
                {(averageImpact * 100).toFixed(0)}%
              </h3>
              <small className="text-muted">Avg Impact Score</small>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (!aiAvailable) {
    return <InstallationGuide />;
  }

  return (
    <div className="ai-insights-container">
      <div className="card">
        <div className="card-header">
          <div className="d-flex justify-content-between align-items-center">
            <h4 className="mb-0">
              <i className="fas fa-robot text-primary me-2"></i>
              AI Insights - Bullet Point Re-writer
            </h4>
            <button
              className="btn btn-outline-primary btn-sm"
              onClick={analyzeBulletPoints}
              disabled={loading || !resumeText}
            >
              {loading ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                  ></span>
                  Analyzing...
                </>
              ) : (
                <>
                  <i className="fas fa-sync-alt me-2"></i>
                  Re-analyze
                </>
              )}
            </button>
          </div>
        </div>

        <div className="card-body">
          {loading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-3 text-muted">
                Analyzing your resume bullet points with AI...
              </p>
            </div>
          ) : bulletAnalyses.length > 0 ? (
            <>
              <SummaryStats />

              <div className="mb-3">
                <p className="text-muted">
                  <i className="fas fa-info-circle me-2"></i>
                  AI has analyzed your resume and identified{" "}
                  <strong>
                    {
                      bulletAnalyses.filter(
                        (b) => b.classification === "responsibility-driven"
                      ).length
                    }
                  </strong>{" "}
                  bullet points that could be more impactful. Below are
                  personalized suggestions to transform them into
                  achievement-focused statements.
                </p>
              </div>

              <div className="bullet-analyses">
                {bulletAnalyses.map((analysis, index) => (
                  <BulletPointCard
                    key={index}
                    analysis={analysis}
                    index={index}
                  />
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-5">
              <i className="fas fa-file-text fa-3x text-muted mb-3"></i>
              <h5 className="text-muted">No Resume Text Provided</h5>
              <p className="text-muted">
                Upload a resume or paste resume text to get AI-powered bullet
                point improvements.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIInsights;
