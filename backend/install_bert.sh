#!/bin/bash
# BERT Dependencies Installation Script
# This script installs the required dependencies for BERT-based resume analysis

echo "🤖 Installing BERT dependencies for IntelliResume..."
echo "⚠️  Warning: This will download ~2-3GB of data"

# Check if user wants to continue
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

echo "📦 Installing Python packages..."

# Install core dependencies
pip install transformers>=4.30.0
pip install torch>=2.0.0 
pip install sentence-transformers>=2.2.0
pip install scikit-learn>=1.3.0
pip install tokenizers>=0.13.0
pip install accelerate>=0.20.0

echo "✅ BERT dependencies installed successfully!"
echo "🧠 The system will now download pre-trained models on first use"
echo "📋 You can test the installation by running: python bert_analyzer.py"

# Test the installation
echo "🔬 Testing BERT analyzer..."
cd "$(dirname "$0")"
python -c "
try:
    from bert_analyzer import test_bert_analyzer
    result = test_bert_analyzer()
    if result['status'] == 'success':
        print('✅ BERT analyzer is working correctly!')
    else:
        print('❌ BERT analyzer test failed:', result.get('message', 'Unknown error'))
except Exception as e:
    print('❌ Test failed:', str(e))
"

echo "🎉 Installation complete!"
echo "💡 Restart your Flask server to enable BERT features"