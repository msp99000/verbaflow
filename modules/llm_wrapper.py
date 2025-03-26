
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

def customLLMBot(user_input, session_id):
    """Handles AI responses with detailed feedback on verbal clarity, tone, pacing, and engagement."""

    # Enhanced system prompt for structured AI feedback
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert verbal communication coach specializing in speech clarity, tone, and articulation. "
                "Your goal is to provide structured and detailed feedback in proper HTML format.\n\n"

                "<strong>📝 Response Format:</strong><br>"
                "<strong>Summary:</strong> Briefly highlight strengths and weaknesses.<br>"
                "<strong>Strengths:</strong><ul>"
                "<li>List strengths here.</li></ul>"
                "<strong>Areas for Improvement:</strong><ul>"
                "<li>List areas needing improvement.</li></ul>"
                "<strong>Example Fix:</strong> Provide a better alternative phrasing.<br>"
                "<strong>Encouragement:</strong> End on a motivating note.<br>\n\n"

                "💡 Example Response (Follow this HTML Format):\n"
                "<strong>Summary:</strong> The response is clear but could be more structured.<br>"
                "<strong>Strengths:</strong><ul>"
                "<li>Engaging opening.</li>"
                "<li>Good vocabulary usage.</li></ul>"
                "<strong>Areas for Improvement:</strong><ul>"
                "<li><strong>Clarity:</strong> Sentences could be shorter for better readability.</li>"
                "<li><strong>Tone:</strong> A bit too casual for a professional setting.</li></ul>"
                "<strong>Example Fix:</strong> Instead of saying <em>'Hey, what's up?'</em>, say <em>'Good afternoon, how can I assist you today?'</em><br>"
                "<strong>Encouragement:</strong> Keep practicing! Small refinements will make a big difference."
            )
        },
        {"role": "user", "content": user_input}
    ]

    try:
        if groq_client:
            response = groq_client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192"
            )
            return response.choices[0].message.content  # AI response is already in formatted HTML
        else:
            return "<strong>Error:</strong> Groq API key not configured."
    except Exception as e:
        return f"<strong>API Error:</strong> {str(e)}"
