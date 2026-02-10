#!/usr/bin/env python3
"""
Diagnostic script for Resume Tailor Application
Tests imports and basic functionality without running the full app
"""

import sys
import os

print("=" * 60)
print("📄 Resume Tailor - Diagnostic Tool")
print("=" * 60)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

errors = []
warnings = []

# Test 1: Basic imports
print("\n1️⃣ Testing basic imports...")
try:
    import streamlit
    print("   ✅ Streamlit available")
except ImportError as e:
    errors.append(f"Streamlit: {e}")
    print("   ❌ Streamlit not installed")

# Test 2: Config module
print("\n2️⃣ Testing config module...")
try:
    from config import GROQ_MODEL, GROQ_API_KEY
    print(f"   ✅ Config loaded")
    print(f"   📍 Model: {GROQ_MODEL}")
    print(f"   🔑 API Key: {'✅ Set' if GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here' else '❌ Not set'}")
except ImportError as e:
    errors.append(f"Config: {e}")
    print(f"   ❌ Config error: {e}")

# Test 3: Resume Parser
print("\n3️⃣ Testing resume parser...")
try:
    from resume_parser import ResumeParser
    print("   ✅ ResumeParser imported")
except ImportError as e:
    errors.append(f"ResumeParser: {e}")
    print(f"   ❌ ResumeParser error: {e}")

# Test 4: Job Scraper
print("\n4️⃣ Testing job scraper...")
try:
    from job_scraper import JobScraper
    print("   ✅ JobScraper imported")
except ImportError as e:
    errors.append(f"JobScraper: {e}")
    print(f"   ❌ JobScraper error: {e}")

# Test 5: Tailor Engine
print("\n5️⃣ Testing tailor engine...")
try:
    from tailor_engine import ResumeTailor
    print("   ✅ ResumeTailor imported")
except ImportError as e:
    errors.append(f"ResumeTailor: {e}")
    print(f"   ❌ ResumeTailor error: {e}")

# Test 6: Output Generator
print("\n6️⃣ Testing output generator...")
try:
    from output_generator import ResumeGenerator
    print("   ✅ ResumeGenerator imported")
except ImportError as e:
    errors.append(f"ResumeGenerator: {e}")
    print(f"   ❌ ResumeGenerator error: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 60)

if not errors and not warnings:
    print("✅ All systems operational! Ready to run:")
    print("   streamlit run app.py")
elif not errors:
    print("⚠️  Warnings found (non-critical):")
    for w in warnings:
        print(f"   - {w}")
    print("\n✅ App should still work. Run: streamlit run app.py")
else:
    print("❌ ERRORS FOUND - App won't work yet:")
    print("\n   Missing dependencies. Install with:")
    print("   pip3 install -r requirements.txt")
    print("   playwright install chromium")
    print("\n   Or if pip3 not available, use your system's package manager.")
    print("\n   Details:")
    for e in errors:
        print(f"   • {e}")

print("\n" + "=" * 60)

# Check .env file
print("\n🔍 Checking .env configuration...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"   ✅ .env file found at {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'GROQ_API_KEY=' in content and 'your_groq_api_key_here' not in content:
            print("   ✅ API key appears to be configured")
        else:
            print("   ⚠️  API key not configured (still has placeholder)")
            print("   Get free key: https://console.groq.com/keys")
else:
    print(f"   ❌ No .env file found")
    print("   Create one from .env.example:")
    print("   cp .env.example .env")
    print("   Then edit and add your GROQ_API_KEY")

print("\n" + "=" * 60)