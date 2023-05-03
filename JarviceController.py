import sys

import openai
import os
import pyaudio
from google.cloud import speech
from google.cloud import texttospeech
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from gtts import gTTS
import requests

url = ""

auth = {

}


openai.api_key = ""
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

# Define speech recognition client
client = speech.SpeechClient()

# Define text-to-speech client
tts_client = texttospeech.TextToSpeechClient()

# Define audio configuration
audio_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
)

# Define text-to-speech voice configuration
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Wavenet-F",
)

# Define text-to-speech audio configuration
audio_config_tts = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)

# Define microphone input
r = sr.Recognizer()
mic = sr.Microphone(device_index=1)

# Define Spotify API client
scope = "user-read-playback-state,user-modify-playback-state"
# Set up Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="",
                                               client_secret="",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-read-playback-state,user-modify-playback-state"))


online = False

# Continuously listen for voice commands
with mic as source:
    r.adjust_for_ambient_noise(source)
    print("Say something!")
    while True:
        audio = r.listen(source)

        try:
            # Recognize speech from audio
            text = r.recognize_google(audio)
            print("You said: " + text)

            if "jarvis online" in text.lower():
                online = True
                print("Jarvis is now online!")
            elif "jarvis offline" in text.lower():
                online = False
                print("Jarvis is now offline.")
            elif online:

                if ("Open Google" or "Open Chrome") in text.lower():
                    os.startfile('Google Chrome.lnk')
                    print("Opening Google Chrome")
                # Check if user wants to play a song
                if "play" in text:
                    query = text.replace("play", "").strip()
                    result = sp.search(q=query, limit=1, type='track')

                    # Play the first track in the search results
                    if result['tracks']['items']:
                        track_uri = result['tracks']['items'][0]['uri']
                        sp.start_playback(uris=[track_uri])
                        message = "Playing " + result['tracks']['items'][0]['name'] + " by " + result['tracks']['items'][0]['artists'][0]['name']
                    else:
                        message = "Sorry, I could not find any tracks with that name."

                else:
                    # Generate response from OpenAI GPT-3 API
                    response = openai.Completion.create(
                        engine="davinci",
                        prompt=text,
                        max_tokens=60,
                        n=1,
                        stop=None,
                        temperature=0.7,
                    )
                    message = response.choices[0].text.strip()
                # Define text to be spoken
                text = message

                # Create gTTS object and save as mp3 file
                tts = gTTS(text=text, lang='en')
                tts.save("jarvis.mp3")

                # Play the mp3 file using the default system player
                os.system("start jarvis.mp3")

                print("Jarvis said: " + message)

                # Convert response to speech
                synthesis_input = texttospeech.SynthesisInput(text=message)
                audio_response = tts_client.synthesize_speech(input=synthesis_input, voice=voice,
                                                              audio_config=audio_config_tts)

                # Play audio response
                os.system(
                    "play -t raw -r 16k -e signed -b 16 -c 1 -V1 <(echo \"" + audio_response.audio_content + "\")")

        except Exception as e:
            print("Error occurred: ", e)
