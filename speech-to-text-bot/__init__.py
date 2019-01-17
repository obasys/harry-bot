from flask import Flask, request
import requests
import os
import io

app = Flask(__name__)

token = '' # <-- Telegram bot token
URL = 'https://api.telegram.org/{}/'.format(token)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '' # <-- Path to google private key json file

def get_bot_info():
    getBotInfoRequest = requests.get(URL + 'getMe')
    return getBotInfoRequest.json()

def get_updates():
    getUpdatesRequest = requests.get(URL + 'getUpdates')
    return getUpdatesRequest.json()

def fetch_chat_id(request):
    return request['message']['chat']['id']

def fetch_text(request):
    return request['message']['text']

def get_voice_file(message):
    """Fetch the audio file from the message."""
    
    file_id = message['voice']['file_id']
    file_path = requests.get('https://api.telegram.org/{}/getFile?file_id={}'.format(token, file_id)).json()
    
    file_name = 'voices/' + file_id + ".ogg"
    
    response = requests.get('https://api.telegram.org/file/{}/{}'.format(token, file_path['result']['file_path']))
    
    # open method to open a file on your system and write the contents
    with open(file_name, "wb") as code:
        code.write(response.content)
    
    return file_name

def get_text_from_audio(file_name):
    """Transcribes the audio file."""
    
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()
    
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
    
    config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
                                     sample_rate_hertz=16000,
                                     language_code='uk-UA',
                                     enable_automatic_punctuation=True)

    response = client.recognize(config, audio)

    result = 'Seems this file is empty'
        
    for result in response.results:
        result = result.alternatives[0].transcript

    return result

def send_response_message(request):
    answer = {'chat_id': fetch_chat_id(request)}
    
    message = request['message']
    
    if 'text' in message:
        answer['text'] = fetch_text(request)
    if 'voice' in message:
        answer['reply_to_message_id'] = message['message_id']
        answer['text'] = get_text_from_audio(get_voice_file(message))
    if 'video_note' in message:
        answer['reply_to_message_id'] = message['message_id']
        answer['text'] = "We received video message"
    if 'audio' in message:
        answer['reply_to_message_id'] = message['message_id']
        answer['text'] = "That's an audio file, not looks like voice message."
    if 'video' in message:
        answer['reply_to_message_id'] = message['message_id']
        answer['text'] = "That's an video file, not looks like video message."
    
    postMessageRequest = requests.post(URL + 'sendMessage', answer)

    print(postMessageRequest.text)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        fetched_request = request.get_json()
        
        print(fetched_request)
        
        if "message" in fetched_request:
            send_response_message(fetched_request)
            return "ok!", 200

    return "<h1 style='text-align: center;'>Speech-to-Text Chat-Bot</h1>"

if __name__ == '__main__':
    app.run(debug=True)

