import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import os

# Supported audio formats
SUPPORTED_FORMATS = ["wav", "mp3", "ogg", "flac"]

def transcribe_audio(audio_file):
    """Converts speech to text using Google Speech Recognition and ensures correct format."""
    recognizer = sr.Recognizer()
    temp_path = "temp_audio.wav"

    # Save uploaded file
    audio_file.save(temp_path)

    # ✅ Check if file exists before processing
    if not os.path.exists(temp_path):
        return "Error: Audio file was not saved correctly."

    try:
        # Debugging: Print file size
        print(f"🔹 Debug: File '{temp_path}' exists. Size: {os.path.getsize(temp_path)} bytes")

        # Convert audio if necessary
        sound = AudioSegment.from_file(temp_path)
        if sound.sample_width != 2 or sound.frame_rate != 16000 or sound.channels != 1:
            sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            sound.export(temp_path, format="wav")

        # Transcribe speech
        with sr.AudioFile(temp_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.record(source)

        # Clean up file
        os.remove(temp_path)
        return recognizer.recognize_google(audio)

    except Exception as e:
        return f"Error: {str(e)}"



def synthesize_speech(text, speed="normal"):
    """Converts text to speech with adjustable speed and saves it as an MP3 file."""
    if not text.strip():
        return "static/speech_output.mp3"  # Return a default file if empty

    file_path = "static/speech_output.mp3"

    # Speed mapping for Google Text-to-Speech
    speed_mapping = {
        "slow": True,
        "normal": False,  # Default speed
        "fast": False  # Fast mode workaround
    }

    try:
        tts = gTTS(text=text, lang="en", slow=speed_mapping.get(speed, False))  # Generate speech

        # Workaround for fast speech (gTTS doesn't have a direct fast mode)
        if speed == "fast":
            sound = AudioSegment.from_file(tts.save(file_path), format="mp3")
            sound = sound.speedup(playback_speed=1.3)  # Increase speed by 30%
            sound.export(file_path, format="mp3")
        else:
            tts.save(file_path)

    except Exception as e:
        return f"Error generating speech: {str(e)}"

    return file_path
