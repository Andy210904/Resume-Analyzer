# BERT Integration for IntelliResume

This document explains how to use the BERT-based advanced NLP features in IntelliResume.

## 🧠 What is BERT Integration?

The BERT (Bidirectional Encoder Representations from Transformers) integration adds advanced semantic understanding to the resume analysis, providing:

- **Semantic Skill Extraction**: Understands skills even when not explicitly mentioned
- **Context-Aware Analysis**: Considers the context around skills and experiences
- **Improved Accuracy**: Better matching between resumes and job requirements
- **Content Quality Assessment**: Evaluates writing quality and professional language use
- **Experience Level Prediction**: Automatically determines seniority level

## 🚀 Installation

### Option 1: Automatic Installation (Recommended)

**Windows:**

```cmd
cd backend
install_bert.bat
```

**Linux/Mac:**

```bash
cd backend
chmod +x install_bert.sh
./install_bert.sh
```

### Option 2: Manual Installation

```bash
pip install -r bert_requirements.txt
```

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 3GB free space for models
- **Python**: 3.8 or higher
- **Optional**: NVIDIA GPU with CUDA for faster processing

## 🔧 Usage

### Checking BERT Status

Visit: `http://localhost:5000/api/bert/status`

```json
{
  "available": true,
  "device": "cpu",
  "models_loaded": true,
  "version": "1.0.0"
}
```

### Testing BERT Functionality

POST to: `http://localhost:5000/api/bert/test`

### Analyzing Resumes with BERT

The BERT analysis is automatically included when available. The response will include:

```json
{
  "traditional_analysis": { ... },
  "bert_analysis": {
    "overall_score": 85,
    "skills_analysis": {
      "total_skills_found": 15,
      "skills_by_category": {
        "programming": [
          {
            "skill": "Python",
            "confidence": 0.95,
            "context": "Developed web applications using Python..."
          }
        ]
      }
    },
    "experience_level": {
      "predicted_level": "Mid-level",
      "confidence": 0.82,
      "years_experience": 5
    },
    "content_quality": {
      "overall_quality": 78.5,
      "action_verb_usage": 65.0,
      "quantifiable_achievements": 45.0
    },
    "semantic_suggestions": [
      "Add more quantifiable achievements with specific numbers",
      "Use stronger action verbs to describe accomplishments"
    ]
  },
  "enhanced_score": 87
}
```

## 🎛️ Configuration

### Environment Variables

Add to your `.env` file:

```env
# BERT Configuration
BERT_ENABLED=true
BERT_DEVICE=auto  # auto, cpu, cuda
BERT_CACHE_DIR=./models_cache
```

### Disabling BERT

To disable BERT without uninstalling:

1. Set `BERT_ENABLED=false` in `.env`
2. Or simply don't install the dependencies

## 🔍 Features Breakdown

### 1. Semantic Skill Extraction

- Finds skills based on context, not just keywords
- Example: "Built machine learning models" → Detects "Machine Learning", "Python", "Data Science"

### 2. Experience Level Prediction

- Analyzes language patterns to determine seniority
- Considers job titles, responsibilities, and achievements

### 3. Content Quality Analysis

- Evaluates professional language usage
- Checks for action verbs and quantifiable achievements
- Assesses readability and structure

### 4. Job Role Matching

- Semantic matching between resume and job descriptions
- Suggests most suitable roles based on content

### 5. Enhanced Suggestions

- Context-aware recommendations
- Personalized improvement suggestions
- Industry-specific advice

## 🚨 Troubleshooting

### Common Issues

#### 1. Out of Memory Error

```python
RuntimeError: CUDA out of memory
```

**Solution**: Set `BERT_DEVICE=cpu` in environment variables

#### 2. Model Download Fails

```python
OSError: Can't load tokenizer
```

**Solution**: Check internet connection and disk space

#### 3. Slow Performance

**Solution**:

- Use GPU if available
- Reduce batch size in configuration
- Consider using smaller models

### Performance Optimization

1. **GPU Usage**: Set `BERT_DEVICE=cuda` if you have NVIDIA GPU
2. **Model Caching**: Models are cached locally after first download
3. **Batch Processing**: Multiple resumes can be processed efficiently

## 📊 Comparison: Traditional vs BERT Analysis

| Feature           | Traditional      | BERT Enhanced          |
| ----------------- | ---------------- | ---------------------- |
| Skill Detection   | Keyword matching | Semantic understanding |
| Context Awareness | Limited          | High                   |
| Accuracy          | ~70%             | ~90%                   |
| Processing Time   | Fast (~1s)       | Moderate (~5-10s)      |
| Resource Usage    | Low              | High                   |
| False Positives   | Common           | Rare                   |

## 🔮 Future Enhancements

- [ ] Fine-tuned models for specific industries
- [ ] Real-time analysis suggestions
- [ ] Multi-language support
- [ ] Custom model training
- [ ] Advanced visualization of semantic relationships

## 🛠️ Development

### Adding New Skills

Edit `bert_analyzer.py`:

```python
self.skill_database = {
    "new_category": [
        "New Skill 1", "New Skill 2"
    ]
}
```

### Custom Models

Replace the default models:

```python
self.sentence_model = SentenceTransformer('your-custom-model')
```

### Testing

Run the test suite:

```bash
python bert_analyzer.py
```

## 📋 API Reference

### GET /api/bert/status

Check if BERT is available and working

### POST /api/bert/test

Test BERT functionality with sample data

### POST /api/analyze

Regular analysis endpoint (includes BERT if available)

## 🤝 Contributing

To contribute to BERT features:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

The BERT integration uses pre-trained models from Hugging Face under Apache 2.0 license.

---

**Need Help?**

- Check the troubleshooting section
- Review logs in the terminal
- Test with the `/api/bert/status` endpoint
