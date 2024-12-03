import sounddevice as sd
from openai import OpenAI
import numpy as np
import time
import io
import wave
import whisper as wh

client = OpenAI(api_key='')
     
def transcribe_audio_with_whisper(filename, sample_rate=16000):
    try:
        print("Transcribing audio using Whisper model...")
        audio_file = open(filename, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text")
        return transcription
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def record_audio(duration=5, sample_rate=16000):
    print("Recording audio...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until the recording is finished
    print("Audio recording finished.")
    return np.squeeze(audio_data)

def audio_to_wav(audio_data, sample_rate=16000):
    """Convert numpy array audio to WAV format"""
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    wav_io.seek(0)
    return wav_io

# def main(args=None):
#     rclpy.init(args=args)

#     command_publisher = CommandLinePublisher()

#     print("Listening for speech every 0.9 seconds. Say 'exit' to stop.")

#     command_publisher.get_logger().info("Starting recording.")

#     try:
#         while True:
#             audio_data = record_audio(duration=5.0)
#             wav_io = audio_to_wav(audio_data)
#             filename = '/home/pi/pupper_llm/pupper_llm/simple_scripts/test_audio.wav'
#             with open(filename, 'wb') as f:
#                 f.write(wav_io.read())
#             command_publisher.get_logger().info("Audio saved to test_audio.wav")

#             t1 = time.time()
#             user_input = command_publisher.transcribe_audio_with_whisper(filename)
#             t2 = time.time()
            
#             command_publisher.get_logger().info(f"Time taken: {t2 - t1}")
            
#             if user_input and user_input.lower() == 'exit':
#                 print("Exiting the publisher.")
#                 break

#             if user_input:
#                 command_publisher.publish_message(user_input)

#             time.sleep(0.9)

