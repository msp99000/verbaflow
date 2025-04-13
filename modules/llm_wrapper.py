import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

def customLLMBot(prompt, session_id=None, purpose="general", system_message=None):
    """
    Generic LLM interface that can be used for multiple purposes using Groq
    """
    try:
        if not groq_api_key:
            return "Error: Groq API key not found in environment variables."

        # Set default system message based on purpose if none provided
        if not system_message:
            if purpose == "chat":
                system_message = "You are a helpful and friendly conversational AI. Respond naturally to the user."
            elif purpose == "assessment":
                system_message = "You are an assessment AI that provides structured feedback on presentations."
            elif purpose == "training":
                system_message = "You are a communication skills training assistant."
            else:
                system_message = "You are a helpful AI assistant."

        # Models to try in order of preference
        models_to_try = [
            "llama3-8b-8192",  # Smaller, faster model
        ]

        # Try each model until one succeeds
        last_error = None
        for model in models_to_try:
            try:
                # Call the Groq API
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=800
                )

                # Return the response
                return chat_completion.choices[0].message.content.strip()

            except Exception as e:
                last_error = e
                print(f"Error with model {model}: {str(e)}")
                continue  # Try the next model

        # If all models failed, return the error
        return f"Error: Failed to generate response with any available model. Last error: {str(last_error)}"

    except Exception as e:
        return f"Error: {str(e)}"

def chatVoiceBot(transcript, scenario="casual"):
    """
    Process voice chat inputs and return hardcoded conversation responses
    to completely avoid assessment-style responses
    """
    # Convert input to lowercase for easier matching
    transcript_lower = transcript.lower().strip()

    # HARDCODED RESPONSES - complete bypass of the LLM for voice chat

    # ---- CASUAL CONVERSATION RESPONSES ----
    if scenario == "casual":
        # Greeting responses
        if "how are you" in transcript_lower:
            return "I'm doing well, thanks for asking! How about you?"

        if any(word in transcript_lower for word in ["hi", "hello", "hey"]):
            return "Hi there! It's nice to chat with you today. What's on your mind?"

        if "what's up" in transcript_lower:
            return "Not much! Just here chatting with you. How's your day going?"

        if any(phrase in transcript_lower for phrase in ["good morning", "morning"]):
            return "Good morning! I hope you're having a great start to your day."

        if any(phrase in transcript_lower for phrase in ["good afternoon", "afternoon"]):
            return "Good afternoon! How has your day been so far?"

        if any(phrase in transcript_lower for phrase in ["good evening", "evening"]):
            return "Good evening! I hope you had a nice day."

        # Weather responses
        if any(word in transcript_lower for word in ["weather", "raining", "sunny", "cold", "hot"]):
            return "Weather can really affect our mood, can't it? What's your favorite kind of weather?"

        # Generic responses for casual chat
        return "That's interesting! I'd love to hear more about that. What else would you like to talk about today?"

    # ---- INTERVIEW RESPONSES ----
    elif scenario == "interview":
        if any(word in transcript_lower for word in ["experience", "work", "job", "career"]):
            return "That's good background information. Can you tell me more about a specific challenge you faced in your previous role and how you overcame it?"

        if any(word in transcript_lower for word in ["skill", "strength", "good at"]):
            return "Those are valuable skills. Could you share a specific example of how you've applied these skills in a professional setting?"

        if any(word in transcript_lower for word in ["weakness", "improve", "learning"]):
            return "Self-awareness is important. How are you actively working to improve in these areas?"

        # Generic interview response
        return "Thank you for sharing that. Now, could you tell me about a time when you had to adapt quickly to an unexpected change in the workplace?"

    # ---- DEBATE RESPONSES ----
    elif scenario == "debate":
        if any(word in transcript_lower for word in ["technology", "ai", "digital", "internet"]):
            return "That's one perspective on technology. However, some would argue that rapid technological advancement also brings significant ethical challenges and potential social disruption. How would you address those concerns?"

        if any(word in transcript_lower for word in ["climate", "environment", "green", "sustainable"]):
            return "Environmental issues are certainly important. However, some would argue that aggressive climate policies can negatively impact economic growth and jobs in the short term. How would you balance these competing priorities?"

        if any(word in transcript_lower for word in ["education", "school", "learn", "student"]):
            return "Education is crucial, but there are different philosophies about the best approaches. Some advocate for more standardized testing to ensure quality, while others argue for more creative and flexible learning environments. What specific evidence supports your position?"

        # Generic debate response
        return "You've made some interesting points. However, I'd like to challenge that perspective. Have you considered the potential counterarguments based on [economic impact/social consequences/practical implementation challenges]?"

    # ---- STORYTELLING RESPONSES ----
    elif scenario == "storytelling":
        if any(word in transcript_lower for word in ["character", "protagonist", "hero", "villain"]):
            return "Character development is crucial for engaging stories. How might this character's background influence their decisions throughout the narrative?"

        if any(word in transcript_lower for word in ["plot", "story", "narrative", "tale"]):
            return "That's an interesting plot direction. Consider how you might build tension throughout the middle of the story before reaching that resolution."

        if any(word in transcript_lower for word in ["setting", "world", "place", "location"]):
            return "Settings can almost become characters themselves. How might this environment actively shape the events of your story rather than just serving as a backdrop?"

        # Generic storytelling response
        return "That's a creative idea with a lot of potential. Consider what emotional journey you want your audience to experience as they engage with this story."

    # Default response if no scenario matches
    return "I'm here to chat! What would you like to talk about today?"
