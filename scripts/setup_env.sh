#!/bin/bash
# Setup script for Resume Tailor
# This activates the virtual environment and provides helpful commands

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating it now..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "✅ Virtual environment activated!"
echo ""
echo "Available commands:"
echo "  python3 parse_resume.py <resume.pdf|docx>"
echo "  python3 scrape_jobs.py <job_url>"
echo "  python3 scrape_jobs.py --file urls.txt"
echo "  python3 tailor_resume.py <resume.json> <jobs.json>"
echo "  streamlit run app.py"
echo ""
echo "To deactivate: type 'deactivate'"
echo ""

# Start a new shell with venv activated
exec bash