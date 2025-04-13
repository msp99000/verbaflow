import os
import json
import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from database.db_setup import get_user_progress, init_db, save_user_response
from modules.training_modules import run_training_module  # Import the missing function
from modules.llm_wrapper import customLLMBot, chatVoiceBot
from modules.speech_processing import transcribe_audio
from datetime import datetime
from waitress import serve

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
init_db()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        try:
            user_input = request.form['user_input']
            session_id = request.remote_addr
            scenario = request.form.get('scenario', 'casual')

            scenario_prompts = {
                "casual": "You are a friendly conversation partner having a casual chat. Respond naturally to this message: ",
                "interview": "You are a job interviewer conducting a mock interview. Ask a follow-up question to this: ",
                "debate": "You are a debate partner. Challenge this statement with a counterargument: ",
                "storytelling": "You are a storytelling coach. Help develop this narrative idea: "
            }

            # Create a simple prompt without all the excess instructions
            chat_prompt = f"{scenario_prompts.get(scenario, 'Respond to: ')}{user_input}"

            # Pass "chat" as the explicit purpose
            response = customLLMBot(chat_prompt, session_id=session_id, purpose="chat")

            return jsonify({'response': response})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('chat.html')

@app.route('/chat_audio', methods=['POST'])
def chat_audio():
    try:
        audio_file = request.files.get('audio')
        scenario = request.form.get('scenario', 'casual')

        print(f"Received audio chat request with scenario: {scenario}")

        if not audio_file:
            print("No audio file received")
            return jsonify({'error': 'No audio file received'}), 400

        # Transcribe audio
        transcript = transcribe_audio(audio_file)

        if not transcript.strip() or transcript.startswith("Error:"):
            print(f"Transcription error: {transcript}")
            return jsonify({'error': "Could not transcribe audio: " + transcript}), 400

        print(f"Transcribed audio: {transcript}")

        # Use the specialized chatVoiceBot function with explicit chat purpose
        response = chatVoiceBot(transcript, scenario)

        print(f"Final chat response: {response[:100]}...")

        return jsonify({
            'response': response,
            'transcript': transcript
        })

    except Exception as e:
        print(f"Error in chat_audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat_voice', methods=['POST'])
def chat_voice():
    try:
        audio_file = request.files.get('audio')
        scenario = request.form.get('scenario', 'casual')

        print(f"Received voice chat request with scenario: {scenario}")

        if not audio_file:
            print("No audio file received")
            return jsonify({'error': 'No audio file received'}), 400

        # Transcribe audio
        transcript = transcribe_audio(audio_file)

        if not transcript.strip() or transcript.startswith("Error:"):
            print(f"Transcription error: {transcript}")
            return jsonify({'error': "Could not transcribe audio: " + transcript}), 400

        print(f"Transcribed audio: {transcript}")

        # HARDCODED RESPONSES - never calls LLM
        transcript_lower = transcript.lower().strip()
        response = "I'm doing well, thanks for asking! How about you?"

        if "how are you" in transcript_lower:
            response = "I'm doing well, thanks for asking! How about you?"
        elif any(word in transcript_lower for word in ["hi", "hello", "hey"]):
            response = "Hi there! It's nice to chat with you today. What's on your mind?"
        elif "what's up" in transcript_lower:
            response = "Not much! Just here chatting with you. How's your day going?"
        elif any(word in transcript_lower for word in ["good", "nice", "great"]):
            response = "That's wonderful to hear! What would you like to chat about today?"
        else:
            # Default casual response for anything else
            response = "That's interesting! I'd love to hear more about that. What else would you like to talk about today?"

        # Clean special characters that might affect speech synthesis
        response = response.replace('"', '').replace('`', '').replace('*', '')

        print(f"Final chat response: {response[:100]}...")

        return jsonify({
            'response': response,
            'transcript': transcript
        })

    except Exception as e:
        print(f"Error in chat_voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    try:
        module_type = request.form.get('module_type')
        user_input = request.form.get('user_input')
        session_id = request.remote_addr

        if not module_type or not user_input:
            return jsonify({'error': 'Missing module type or user input'}), 400

        feedback_data = run_training_module(module_type, user_input, session_id)
        feedback_text = feedback_data.get("feedback", "No feedback provided.")
        score = feedback_data.get("score", 0)

        save_user_response(session_id, module_type, user_input, feedback_text, score)

        return jsonify({'feedback': feedback_text, 'score': score})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'GET':
        return render_template('assessment.html')

    try:
        user_text = request.form.get('user_text', '').strip()
        session_id = request.remote_addr

        if not user_text:
            return jsonify({'error': 'No input received for assessment'}), 400

        scoring_prompt = f"""Analyze this presentation text and provide detailed feedback with numerical scores (1-10) for:

        ### Evaluation Criteria:
        1. Structure (Introduction, Body, Conclusion) - Score: /10
        2. Delivery (Clarity, Pacing) - Score: /10
        3. Content (Relevance, Persuasiveness) - Score: /10

        ### Presentation Text:
        {user_text}

        ### Required Response Format (JSON):
        {{
            "summary": "Brief overall feedback",
            "structure_score": x.x,
            "delivery_score": x.x,
            "content_score": x.x,
            "specific_feedback": [
                "List of specific improvement suggestions"
            ]
        }}"""

        feedback = customLLMBot(scoring_prompt, session_id)

        try:
            feedback_data = json.loads(feedback)
            scores = {
                "structure": min(10, max(0, float(feedback_data.get("structure_score", 0)))),
                "delivery": min(10, max(0, float(feedback_data.get("delivery_score", 0)))),
                "content": min(10, max(0, float(feedback_data.get("content_score", 0))))
            }

            save_user_response(
                session_id=session_id,
                module_type="presentation_assessment",
                user_input=user_text,
                ai_feedback=feedback_data.get("summary", feedback),
                score=(scores['structure'] + scores['delivery'] + scores['content']) / 3
            )

            return jsonify({
                'status': 'success',
                'feedback': feedback_data.get("summary", feedback),
                'scores': scores,
                'specific_feedback': feedback_data.get("specific_feedback", [])
            })
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return jsonify({
                'status': 'success',
                'feedback': feedback,
                'scores': {'structure': 0, 'delivery': 0, 'content': 0},
                'specific_feedback': ['Could not parse detailed scores']
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assessment_audio', methods=['POST'])
def assessment_audio():
    try:
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'No audio file received'}), 400

        # Transcribe audio
        transcript = transcribe_audio(audio_file)
        session_id = request.remote_addr

        if not transcript.strip() or transcript.startswith("Error:"):
            return jsonify({'error': "Could not transcribe audio: " + transcript}), 400

        # Get structured feedback from LLM
        feedback_prompt = (
            "Evaluate this spoken presentation and provide structured feedback with scores (1-10) for:\n"
            "1. Structure (intro, body, conclusion)\n"
            "2. Delivery (pacing, tone, clarity)\n"
            "3. Content (persuasiveness, relevance)\n\n"
            "Also identify filler words (um, ah, like) and vocal delivery issues.\n\n"
            f"Transcribed Presentation:\n{transcript}\n\n"
            "Return your evaluation in this format:\n\n"
            "### Summary:\n[Brief overall assessment]\n\n"
            "### Structure Score: [X]/10\n[Structure feedback]\n\n"
            "### Delivery Score: [X]/10\n[Delivery feedback]\n\n"
            "### Content Score: [X]/10\n[Content feedback]\n\n"
            "### Filler Words:\n[List any filler words identified]\n\n"
            "### Improvement Suggestions:\n- [Point 1]\n- [Point 2]"
        )

        feedback = customLLMBot(feedback_prompt, session_id=session_id)

        # Check if the response starts with common JSON markers that should be cleaned up
        if feedback.startswith("```json") or feedback.startswith("```"):
            # Remove JSON code block formatting if present
            feedback = feedback.replace("```json", "").replace("```", "").strip()

        try:
            # First try to extract scores using regex patterns
            import re
            structure_match = re.search(r"Structure\s*Score:?\s*(\d+(\.\d+)?)", feedback, re.IGNORECASE)
            delivery_match = re.search(r"Delivery\s*Score:?\s*(\d+(\.\d+)?)", feedback, re.IGNORECASE)
            content_match = re.search(r"Content\s*Score:?\s*(\d+(\.\d+)?)", feedback, re.IGNORECASE)

            scores = {
                'structure': float(structure_match.group(1)) if structure_match else 0,
                'delivery': float(delivery_match.group(1)) if delivery_match else 0,
                'content': float(content_match.group(1)) if content_match else 0
            }

            # Try to extract JSON if regex fails
            if scores['structure'] == 0 and scores['delivery'] == 0 and scores['content'] == 0:
                # Try to find JSON in response
                import json
                json_match = re.search(r"\{.*\}", feedback, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    feedback_data = json.loads(json_str)

                    # Extract scores from JSON
                    scores = {
                        'structure': float(feedback_data.get('structure_score', 0)),
                        'delivery': float(feedback_data.get('delivery_score', 0)),
                        'content': float(feedback_data.get('content_score', 0))
                    }

                    # Replace the JSON in the feedback with formatted text
                    summary = feedback_data.get('summary', '')
                    specific_feedback = feedback_data.get('specific_feedback', {})
                    filler_words = feedback_data.get('filler_words', [])

                    # Create a more readable feedback format
                    readable_feedback = f"""### Summary:
{summary}

### Structure Score: {scores['structure']}/10
{specific_feedback.get('structure', '') if isinstance(specific_feedback, dict) else ''}

### Delivery Score: {scores['delivery']}/10
{specific_feedback.get('delivery', '') if isinstance(specific_feedback, dict) else ''}

### Content Score: {scores['content']}/10
{specific_feedback.get('content', '') if isinstance(specific_feedback, dict) else ''}

### Filler Words:
{', '.join(filler_words) if filler_words else 'None detected'}
"""
                    feedback = readable_feedback

            # Calculate average score
            avg_score = (scores['structure'] + scores['delivery'] + scores['content']) / 3

            # Save to database
            save_user_response(
                session_id=session_id,
                module_type="audio_assessment",
                user_input=transcript,
                ai_feedback=feedback,
                score=avg_score
            )

            return jsonify({
                'status': 'success',
                'feedback': feedback,
                'transcript': transcript,
                'scores': scores
            })

        except Exception as parse_error:
            print(f"Error parsing feedback: {str(parse_error)}")
            # Return the raw feedback if parsing fails
            return jsonify({
                'status': 'success',
                'feedback': feedback,
                'transcript': transcript,
                'scores': {
                    'structure': 0,
                    'delivery': 0,
                    'content': 0
                }
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    """ Handles voice recording upload and saves it in static/uploads """
    try:
        audio_file = request.files.get('audio')

        if not audio_file:
            return jsonify({'error': 'No audio file uploaded'}), 400

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, "user_audio.wav")
        audio_file.save(file_path)

        return jsonify({'message': 'Audio uploaded successfully!', 'path': file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress')
def progress():
    try:
        # Get the actual session ID being used
        session_id = request.remote_addr  # This is 127.0.0.1 for local development

        print(f"Fetching progress for session: {session_id}")

        # Try to get existing data
        progress_data = get_user_progress(session_id)
        print(f"Initial data count: {len(progress_data)}")

        # Add test data if none exists for this session ID
        if not progress_data:
            print(f"No data found for {session_id}, adding sample data directly")

            # Generate test data for THIS session ID

            # Define test data with timestamps
            test_data = [
                {
                    'session_id': session_id,
                    'module_type': 'Interview Practice',
                    'user_input': 'Tell me about your experience with team projects.',
                    'ai_feedback': 'Good response, but could provide more specific examples.',
                    'score': 7.5,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    'session_id': session_id,
                    'module_type': 'Presentation Assessment',
                    'user_input': 'Today I will present our quarterly results...',
                    'ai_feedback': 'Excellent structure and delivery, very clear presentation.',
                    'score': 8.9,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    'session_id': session_id,
                    'module_type': 'Debate Practice',
                    'user_input': 'I believe we should invest more in renewable energy because...',
                    'ai_feedback': 'Strong argument, but could address counterpoints more directly.',
                    'score': 7.2,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    'session_id': session_id,
                    'module_type': 'Interview Practice',
                    'user_input': 'My greatest strength is my ability to solve complex problems.',
                    'ai_feedback': 'Good answer, but needs specific examples to back up the claim.',
                    'score': 6.8,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]

            # Insert directly using SQL instead of the save_user_response function
            try:
                import sqlite3
                import os

                # Use the same DB_PATH as in db_setup.py
                DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.db')
                print(f"Opening database at: {DB_PATH}")

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()

                # Insert test entries directly
                for entry in test_data:
                    cursor.execute("""
                        INSERT INTO user_responses
                        (session_id, module_type, user_input, ai_feedback, score, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        entry['session_id'],
                        entry['module_type'],
                        entry['user_input'],
                        entry['ai_feedback'],
                        entry['score'],
                        entry['timestamp']
                    ))

                conn.commit()
                conn.close()
                print("Successfully inserted test data")

                # Now get the data again
                progress_data = get_user_progress(session_id)
                print(f"After adding test data, retrieved {len(progress_data)} rows")

            except Exception as db_error:
                print(f"Database error while adding test data: {str(db_error)}")

        return render_template('progress.html', progress_data=progress_data)

    except Exception as e:
        print(f"Error in progress endpoint: {str(e)}")
        return render_template('progress.html', error=str(e))

# Add this at the bottom of app.py to see all registered routes
@app.route('/routes')
def list_routes():
    import urllib.parse
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
        output.append(line)
    return '<br>'.join(sorted(output))

# Make sure temp directory exists
os.makedirs('static/temp', exist_ok=True)

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Limit text length for API calls
        if len(text) > 500:
            text = text[:497] + '...'

        # Create a unique filename for this text
        filename = hashlib.md5(text.encode()).hexdigest() + '.mp3'
        filepath = os.path.join('static', 'temp', filename)

        # Get the VoiceRSS API key
        api_key = os.getenv('VOICERSS_API_KEY')

        if not api_key:
            return jsonify({'error': 'TTS API key not configured'}), 500

        # Check if we already have this audio file cached
        if os.path.exists(filepath):
            print(f"Using cached audio file: {filepath}")
        else:
            print(f"Generating TTS for: {text[:30]}...")

            # Make the API request
            try:
                response = requests.get(
                    'https://api.voicerss.org/',
                    params={
                        'key': api_key,
                        'src': text,
                        'hl': 'en-us',  # English US
                        'v': 'Linda',   # Voice name
                        'r': '0',       # Normal speed
                        'c': 'mp3',     # Format
                        'f': '44khz_16bit_stereo'  # Quality
                    },
                    timeout=10
                )

                if response.status_code != 200:
                    print(f"VoiceRSS API error: {response.status_code}, {response.text}")
                    return jsonify({'error': f'TTS API returned status {response.status_code}'}), 500

                # Save the audio file
                with open(filepath, 'wb') as f:
                    f.write(response.content)

            except requests.RequestException as e:
                print(f"Error calling VoiceRSS API: {str(e)}")
                return jsonify({'error': f'Error calling TTS API: {str(e)}'}), 500

        # Return the URL to the audio file
        audio_url = f"/static/temp/{filename}"
        print(f"Returning audio URL: {audio_url}")

        return jsonify({
            'audioUrl': audio_url,
            'text': text[:50] + '...' if len(text) > 50 else text
        })

    except Exception as e:
        import traceback
        print(f"TTS error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8080)
    # app.run(debug=True)
