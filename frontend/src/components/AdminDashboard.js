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
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Users,
  FileText,
  TrendingUp,
  Activity,
  Award,
  Download,
  Filter,
  Eye,
  Edit,
  Trash2,
  Search,
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

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usersLoading, setUsersLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

  useEffect(() => {
    fetchDashboardStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/dashboard/admin/stats");
      setStats(response.data);
    } catch (error) {
      setError("Failed to load dashboard statistics");
      console.error("Dashboard stats error:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setUsersLoading(true);
      const response = await axios.get(
        `/api/dashboard/admin/users?page=${currentPage}&per_page=10`
      );
      setUsers(response.data.users);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error("Users fetch error:", error);
    } finally {
      setUsersLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const filteredUsers = users.filter(
    (user) =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
                background: "linear-gradient(135deg, #343a40 0%, #495057 100%)",
                borderRadius: "20px",
              }}
            >
              <div className="card-body p-4">
                <h1
                  className="text-white mb-3 fw-bold"
                  style={{ fontSize: "2.5rem" }}
                >
                  <i className="fas fa-users-cog me-3"></i>
                  Admin Dashboard
                </h1>
                <p className="text-white mb-0 fs-5" style={{ opacity: 0.9 }}>
                  Welcome {user?.full_name}! Monitor system-wide analytics and
                  manage users.
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
                  style={{ width: "60px", height: "60px" }}
                >
                  <Users className="text-white" size={28} />
                </div>
                <h2
                  className="text-primary mb-2 fw-bold"
                  style={{ fontSize: "2.5rem" }}
                >
                  {stats?.total_users || 0}
                </h2>
                <p className="text-muted mb-0 fw-medium">Total Users</p>
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
                  style={{ width: "60px", height: "60px" }}
                >
                  <FileText className="text-white" size={28} />
                </div>
                <h2
                  className="text-success mb-2 fw-bold"
                  style={{ fontSize: "2.5rem" }}
                >
                  {stats?.total_analyses || 0}
                </h2>
                <p className="text-muted mb-0 fw-medium">Total Analyses</p>
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
                  style={{ width: "60px", height: "60px" }}
                >
                  <Award className="text-white" size={28} />
                </div>
                <h2
                  className="text-warning mb-2 fw-bold"
                  style={{ fontSize: "2.5rem" }}
                >
                  {stats?.avg_score || 0}
                </h2>
                <p className="text-muted mb-0 fw-medium">Average Score</p>
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
                  style={{ width: "60px", height: "60px" }}
                >
                  <Activity className="text-white" size={28} />
                </div>
                <h2
                  className="text-info mb-2 fw-bold"
                  style={{ fontSize: "2.5rem" }}
                >
                  {stats?.active_today || 0}
                </h2>
                <p className="text-muted mb-0 fw-medium">Active Today</p>
              </div>
            </div>
          </div>
        </div>

        <div className="row mb-4">
          {/* Upload Trend Chart */}
          <div className="col-lg-8 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h4 className="card-title mb-0 fw-bold text-dark">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "40px", height: "40px" }}
                    >
                      <TrendingUp className="text-white" size={20} />
                    </div>
                    Upload Trend (Last 7 Days)
                  </div>
                </h4>
              </div>
              <div className="card-body px-4 pb-4">
                {stats?.upload_trend && stats.upload_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={stats.upload_trend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="count"
                        stroke="#0088FE"
                        strokeWidth={3}
                        dot={{ fill: "#0088FE", strokeWidth: 2, r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center text-muted py-5">
                    <TrendingUp size={48} className="mb-3" />
                    <p>No data available for upload trends</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Score Distribution */}
          <div className="col-lg-4 mb-3">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="card-title mb-0">
                  <Award className="me-2" size={20} />
                  Score Distribution
                </h5>
              </div>
              <div className="card-body">
                {stats?.score_distribution && (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={stats.score_distribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ range, count }) =>
                          count > 0 ? `${range}: ${count}` : ""
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {stats.score_distribution.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="row mb-4">
          {/* Top Skills */}
          <div className="col-lg-6 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h4 className="card-title mb-0 fw-bold text-dark">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "40px", height: "40px" }}
                    >
                      <TrendingUp className="text-white" size={20} />
                    </div>
                    Top 10 Skills
                  </div>
                </h4>
              </div>
              <div className="card-body px-4 pb-4">
                {stats?.top_skills && (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={stats.top_skills} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="skill" type="category" width={100} />
                      <Tooltip />
                      <Bar
                        dataKey="count"
                        fill="#00C49F"
                        radius={[0, 4, 4, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* Domain Distribution */}
          <div className="col-lg-6 mb-3">
            <div
              className="card h-100 border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4">
                <h4 className="card-title mb-0 fw-bold text-dark">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "40px", height: "40px" }}
                    >
                      <FileText className="text-white" size={20} />
                    </div>
                    Domain Distribution
                  </div>
                </h4>
              </div>
              <div className="card-body px-4 pb-4">
                {stats?.domain_distribution && (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={stats.domain_distribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="domain" />
                      <YAxis />
                      <Tooltip />
                      <Bar
                        dataKey="count"
                        fill="#FFBB28"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* User Management Table */}
        <div className="row mb-4">
          <div className="col-12">
            <div
              className="card border-0 shadow-sm"
              style={{ borderRadius: "15px" }}
            >
              <div className="card-header border-0 bg-transparent pt-4 px-4 d-flex justify-content-between align-items-center">
                <h4 className="card-title mb-0 fw-bold text-dark">
                  <div className="d-flex align-items-center">
                    <div
                      className="bg-info rounded-circle d-inline-flex align-items-center justify-content-center me-3"
                      style={{ width: "40px", height: "40px" }}
                    >
                      <Users className="text-white" size={20} />
                    </div>
                    User Management
                  </div>
                </h4>
                <div className="d-flex gap-3">
                  <div className="input-group" style={{ width: "300px" }}>
                    <span className="input-group-text border-0 bg-light">
                      <Search size={16} />
                    </span>
                    <input
                      type="text"
                      className="form-control border-0 bg-light"
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      style={{ borderRadius: "0 8px 8px 0" }}
                    />
                  </div>
                  <button
                    className="btn btn-outline-primary border-2 px-3"
                    style={{ borderRadius: "8px" }}
                  >
                    <Filter className="me-1" size={16} />
                    Filter
                  </button>
                  <button
                    className="btn btn-success px-3"
                    style={{ borderRadius: "8px" }}
                  >
                    <Download className="me-1" size={16} />
                    Export
                  </button>
                </div>
              </div>
              <div className="card-body">
                {usersLoading ? (
                  <div className="text-center py-4">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="table-responsive">
                      <table className="table table-hover">
                        <thead>
                          <tr>
                            <th>User</th>
                            <th>Email</th>
                            <th>Joined</th>
                            <th>Last Active</th>
                            <th>Resumes</th>
                            <th>Avg Score</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredUsers.map((user) => (
                            <tr key={user.id}>
                              <td>
                                <div>
                                  <div className="fw-bold">
                                    {user.full_name}
                                  </div>
                                  <small className="text-muted">
                                    @{user.username}
                                  </small>
                                </div>
                              </td>
                              <td>{user.email}</td>
                              <td>
                                {new Date(user.created_at).toLocaleDateString()}
                              </td>
                              <td>
                                {user.last_login
                                  ? new Date(
                                      user.last_login
                                    ).toLocaleDateString()
                                  : "Never"}
                              </td>
                              <td>
                                <span className="badge bg-primary">
                                  {user.resume_count}
                                </span>
                              </td>
                              <td>
                                <span
                                  className={`badge ${
                                    user.avg_score >= 80
                                      ? "bg-success"
                                      : user.avg_score >= 60
                                      ? "bg-warning"
                                      : "bg-danger"
                                  }`}
                                >
                                  {user.avg_score || 0}
                                </span>
                              </td>
                              <td>
                                <span
                                  className={`badge ${
                                    user.is_active
                                      ? "bg-success"
                                      : "bg-secondary"
                                  }`}
                                >
                                  {user.is_active ? "Active" : "Inactive"}
                                </span>
                              </td>
                              <td>
                                <div className="btn-group btn-group-sm">
                                  <button
                                    className="btn btn-outline-primary"
                                    title="View"
                                  >
                                    <Eye size={14} />
                                  </button>
                                  <button
                                    className="btn btn-outline-secondary"
                                    title="Edit"
                                  >
                                    <Edit size={14} />
                                  </button>
                                  <button
                                    className="btn btn-outline-danger"
                                    title="Delete"
                                  >
                                    <Trash2 size={14} />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                      <nav className="mt-3">
                        <ul className="pagination justify-content-center">
                          <li
                            className={`page-item ${
                              currentPage === 1 ? "disabled" : ""
                            }`}
                          >
                            <button
                              className="page-link"
                              onClick={() => handlePageChange(currentPage - 1)}
                              disabled={currentPage === 1}
                            >
                              Previous
                            </button>
                          </li>
                          {[...Array(totalPages)].map((_, index) => (
                            <li
                              key={index + 1}
                              className={`page-item ${
                                currentPage === index + 1 ? "active" : ""
                              }`}
                            >
                              <button
                                className="page-link"
                                onClick={() => handlePageChange(index + 1)}
                              >
                                {index + 1}
                              </button>
                            </li>
                          ))}
                          <li
                            className={`page-item ${
                              currentPage === totalPages ? "disabled" : ""
                            }`}
                          >
                            <button
                              className="page-link"
                              onClick={() => handlePageChange(currentPage + 1)}
                              disabled={currentPage === totalPages}
                            >
                              Next
                            </button>
                          </li>
                        </ul>
                      </nav>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
