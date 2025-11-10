@echo off
REM BERT Dependencies Installation Script for Windows
REM This script installs the required dependencies for BERT-based resume analysis

echo 🤖 Installing BERT dependencies for IntelliResume...
echo ⚠️  Warning: This will download ~2-3GB of data
echo.

set /p continue="Do you want to continue? (y/N): "
if /i not "%continue%"=="y" (
    echo Installation cancelled.
    pause
    exit /b 1
)

echo 📦 Installing Python packages...
echo.

REM Install core dependencies
pip install transformers>=4.30.0
if errorlevel 1 goto error

pip install torch>=2.0.0
if errorlevel 1 goto error

pip install sentence-transformers>=2.2.0
if errorlevel 1 goto error

pip install scikit-learn>=1.3.0
if errorlevel 1 goto error

pip install tokenizers>=0.13.0
if errorlevel 1 goto error

pip install accelerate>=0.20.0
if errorlevel 1 goto error

echo.
echo ✅ BERT dependencies installed successfully!
echo 🧠 The system will now download pre-trained models on first use
echo 📋 You can test the installation by running: python bert_analyzer.py
echo.

REM Test the installation
echo 🔬 Testing BERT analyzer...
python -c "try: from bert_analyzer import test_bert_analyzer; result = test_bert_analyzer(); print('✅ BERT analyzer is working correctly!' if result['status'] == 'success' else '❌ BERT analyzer test failed: ' + result.get('message', 'Unknown error')); except Exception as e: print('❌ Test failed:', str(e))"

echo.
echo 🎉 Installation complete!
echo 💡 Restart your Flask server to enable BERT features
pause
exit /b 0

:error
echo.
echo ❌ Installation failed! Please check your Python environment and try again.
pause
exit /b 1