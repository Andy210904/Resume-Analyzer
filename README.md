# 🎯 IntelliResume

> An intelligent resume analysis tool that provides comprehensive feedback and industry-specific insights to help job seekers optimize their resumes.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-19.1.0-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)

## 📋 Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔍 **Comprehensive Resume Analysis**

- **Overall scoring** with detailed breakdown
- **Section-wise analysis** (Education, Experience, Skills, Projects)
- **Word count** and resume length optimization
- **Action verb analysis** for impactful descriptions
- **Keyword extraction** for ATS compatibility

### 🏭 **Industry-Specific Insights**

- **Software Engineer** - Tech skills, frameworks, and methodologies
- **Data Scientist** - ML/AI tools, statistical methods, and analytics
- **Marketing** - Digital marketing, campaigns, and growth strategies
- **Finance** - Financial modeling, analysis, and regulatory knowledge

### 📊 **Advanced Analytics**

- **Skills gap analysis** with missing skill recommendations
- **Achievement-focused feedback** with quantifiable metrics
- **Section completeness** evaluation
- **Professional language assessment**

### 🎨 **User-Friendly Interface**

- **Drag-and-drop** file upload (PDF & DOCX support)
- **Real-time analysis** with progress indicators
- **Responsive design** for all devices
- **Interactive results** with detailed breakdowns

## 🚀 Demo

### Live Application

🌐 **Frontend**: [https://your-frontend-url.com](https://your-frontend-url.com)
🔗 **API**: [https://resume-analyzer-lebh.onrender.com](https://resume-analyzer-lebh.onrender.com)

### Screenshots

![Upload Interface](./docs/images/upload-interface.png)
_Upload your resume and select your target industry_

![Analysis Results](./docs/images/analysis-results.png)
_Comprehensive analysis with actionable insights_

## 🛠 Technology Stack

### Backend

- **Framework**: Flask 2.3.3
- **NLP**: spaCy, NLTK, TextBlob
- **Document Processing**: PyPDF2, python-docx
- **CORS**: Flask-CORS
- **Deployment**: Render

### Frontend

- **Framework**: React 19.1.0
- **Styling**: Bootstrap 5.3.6
- **HTTP Client**: Axios 1.9.0
- **Build Tool**: Create React App

### AI/ML Libraries

- **Natural Language Processing**: spaCy (en_core_web_sm)
- **Text Analysis**: NLTK, TextBlob
- **Sentiment Analysis**: TextBlob
- **Data Processing**: NumPy, Pandas

## 📦 Installation

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 14 or higher
- **npm** or **yarn**

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Andy210904/AI-Resume-Analyzer.git
   cd AI-Resume-Analyzer
   ```

2. **Set up virtual environment**

   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy language model**

   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the Flask server**
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

### Build for Production

1. **Build the frontend**

   ```bash
   cd frontend
   npm run build
   ```

2. **The backend serves the built frontend**
   Access the complete application at `http://localhost:5000`

## 📖 Usage

### Basic Usage

1. **Upload Resume**: Select a PDF or DOCX file
2. **Choose Industry**: Select your target job role
3. **Analyze**: Click "Analyze Resume" button
4. **Review Results**: Get detailed feedback and suggestions

### Supported File Types

- **PDF** (.pdf)
- **Microsoft Word** (.docx)

### Supported Industries

- **Software Engineer**: Full-stack, backend, frontend, DevOps
- **Data Scientist**: ML, AI, analytics, research
- **Marketing**: Digital marketing, content, growth
- **Finance**: Investment, banking, accounting, analysis

## 🔗 API Documentation

### Endpoints

#### POST `/api/analyze`

Analyzes an uploaded resume file.

**Request:**

```javascript
// Form Data
{
  file: File,        // PDF or DOCX file
  job_role: String   // 'software_engineer', 'data_scientist', 'marketing', 'finance'
}
```

**Response:**

```javascript
{
  "overall_score": 85,
  "sections": {
    "education": {
      "exists": true,
      "score": 90,
      "feedback": ["Bachelor's degree found", "Clear graduation dates"]
    },
    "experience": {
      "exists": true,
      "score": 80,
      "feedback": ["3+ years of experience", "Missing quantified achievements"]
    },
    // ... other sections
  },
  "industry_analysis": {
    "industry": "software_engineer",
    "overall_score": 78,
    "skills_analysis": {
      "score": 85,
      "found_skills": ["python", "react", "aws"],
      "missing_important_skills": ["docker", "kubernetes"]
    },
    // ... other analyses
  },
  "suggestions": ["Add more technical projects", "Include metrics in experience"],
  "strengths": ["Strong educational background", "Relevant experience"],
  "word_count": 450
}
```

**Error Response:**

```javascript
{
  "error": "File type not allowed"
}
```

## 📁 Project Structure

```
AI-Resume-Analyzer/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── industry_analyzer.py   # Industry-specific analysis logic
│   ├── requirements.txt       # Python dependencies
│   ├── test.py               # Test utilities
│   └── uploads/              # Temporary file storage
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── ...
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Application styles
│   │   ├── index.js          # React entry point
│   │   └── ...
│   ├── package.json          # Node.js dependencies
│   └── build/                # Production build
├── README.md
└── .gitignore
```

## 🎯 Key Features Breakdown

### Resume Analysis Engine

- **Text Extraction**: Handles PDF and DOCX formats
- **Section Detection**: Automatically identifies resume sections
- **Content Analysis**: Evaluates completeness and quality
- **Scoring Algorithm**: Weighted scoring based on industry standards

### Industry Intelligence

- **Skill Matching**: Compares against industry-required skills
- **Section Recommendations**: Suggests relevant resume sections
- **Action Verb Analysis**: Identifies impactful language
- **Achievement Detection**: Recognizes quantifiable accomplishments

### NLP Capabilities

- **Keyword Extraction**: Identifies important terms and phrases
- **Sentiment Analysis**: Evaluates overall tone and positivity
- **Language Quality**: Assesses professionalism and clarity
- **ATS Optimization**: Ensures compatibility with Applicant Tracking Systems

## 🚀 Deployment

### Backend Deployment (Render)

1. Connect your GitHub repository to Render
2. Select "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variables if needed

### Frontend Deployment (Netlify/Vercel)

1. Build the project: `npm run build`
2. Deploy the `build` folder
3. Configure redirects for single-page application

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Add tests for new features
- Update documentation as needed

## 🐛 Issues and Support

If you encounter any issues or have questions:

1. **Check existing issues** in the GitHub Issues tab
2. **Create a new issue** with detailed description
3. **Provide steps to reproduce** the problem
4. **Include error messages** and screenshots if applicable

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Andy210904** - _Initial work_ - [GitHub Profile](https://github.com/Andy210904)

## 🙏 Acknowledgments

- **spaCy** for natural language processing capabilities
- **Flask** for the robust backend framework
- **React** for the interactive frontend
- **Bootstrap** for responsive design components
- **NLTK** for additional text processing tools

## 📊 Project Stats

- **Languages**: Python, JavaScript, HTML, CSS
- **Total Lines of Code**: ~2,000+
- **Dependencies**: 15+ libraries
- **Supported Industries**: 4
- **File Formats**: PDF, DOCX

---

<div align="center">
  <p><strong>Made with ❤️ for job seekers worldwide</strong></p>
  <p>⭐ Star this repository if it helped you!</p>
</div>
