#!/usr/bin/env python3
"""Test Groq API connection for text and audio"""

# Import the Groq client class
from groq import Client
from src.config import GROQ_API_KEY, GROQ_MODEL  # Your config file with keys/models
from pathlib import Path  # Correct import for Path objects

def test_groq_connection():
    """
    Test the Groq API with a simple chat request.
    
    Pattern:
    1. Create a Client instance with API key.
    2. Send a chat completion request to a model.
    3. Print and return the result.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("ERROR: GROQ_API_KEY not set in config or .env file")
        return False

    try:
        # Create the client using your API key
        client = Client(api_key=GROQ_API_KEY)

        # Send a simple chat request
        response = client.chat.completions.create(
            model=GROQ_MODEL,  # The model you want to test
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Reply briefly."},
                {"role": "user", "content": "Say 'Connection successful!' if you can read this."},
            ],
            max_tokens=50,      # Limit response length
            temperature=0,      # Deterministic output for testing
        )

        # Extract the text from the response
        result = response.choices[0].message.content
        print(f"SUCCESS: Groq API connection working!")
        print(f"Model: {GROQ_MODEL}")
        print(f"Response: {result}")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False


def test_groq_connection2():
    """
    Another example of testing Groq chat with a different model.
    
    Demonstrates pattern reuse:
    - Initialize client
    - Send a message
    - Print the output
    """
    client = Client(api_key=GROQ_API_KEY)  # Always pass API key if required

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",  # Example different model
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
    )

    print("Groq response:")
    print(response.choices[0].message.content)


def test_ad():
    """
    Test Groq TTS with Orpheus English model.
    Requires terms acceptance at:
    https://console.groq.com/playground?model=canopylabs%2Forpheus-v1-english
    """
    from pathlib import Path  # local import avoids any config shadowing
    from groq import Client

    client = Client(api_key=GROQ_API_KEY)
    speech_file_path = Path("speech.wav")

    # Orpheus supports vocal directions in brackets!
    text = "[cheerful] Hello! This is a test of the Groq Orpheus text to speech system."

    response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",  # HARDCODE — never use GROQ_MODEL here
        voice="troy",        # Options: troy, thalia, stella, scarlett, leah, dan
        response_format="wav",
        input=text,
    )

    response.stream_to_file(speech_file_path)
    print(f"✅ Audio saved to {speech_file_path}")


if __name__ == "__main__":
    # Test text chat API
    # test_groq_connection()
    # test_groq_connection2()

    # Test audio API
    test_ad()