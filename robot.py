import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import requests
import webbrowser
import sys
import shutil
import random
from googletrans import Translator

def recognize_speech_from_mic(recognizer, microphone):
    
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")
    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def get_ai_response(text):

    url = "http://api-free.ir/api/bard.php"
    params = {'text': text}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("result_en", "I didn't understand that.")
        else:
            return "Error: Unable to reach AI service."
    except requests.RequestException as e:
        return f"Error: {str(e)}"

def download_image(text):
    
    try:
        response = requests.get(f"http://api-free.ir/api/img.php?text={text}&v=3.5")
        response.raise_for_status()
                
        data = response.json()
        result = data["result"]
            
        # Select a random element from the result list
        random_link = random.choice(result)
            
        response = requests.get(random_link, stream=True)
        response.raise_for_status()
            
        with open("downloaded_image.jpg", "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
            os.system("start downloaded_image.jpg")
            
      
            
        
        return "Image downloaded and saved as 'downloaded_image.jpg'."
    except requests.RequestException as e:
        return f"Error: Unable to download image. {str(e)}"

def respond_to_greeting(text):
    
    if text:
        text = text.lower()
        if "hello" in text:
            return "Hello!"
        elif "hi" in text:
            return "Hi!"
        elif "how are you" in text:
            return "I'm fine, thank you!"
        elif "exit" in text:
            return "exit"
        elif "amirhossein" in text:
            return "Amirhossein is my love and creator!"
        elif "open notepad" in text:
            os.system("start notepad")
            return "Opening Notepad."
        elif "open google" in text:
            webbrowser.open("http://www.google.com")
            return "Opening Google."
        elif "shut down" in text or "shutdown" in text:
            os.system("shutdown /s /t 1")
            return "Shutting down the system."
        elif "restart" in text:
            os.system("shutdown /r /t 1")
            return "Restarting the system."
        elif "image" in text:
            # Extract the text after the word 'image'
            image_text = text.split("image", 1)[1].strip()
            if image_text:
                return download_image(image_text)
            else:
                return "Please provide text for the image."
        else:
            return get_ai_response(text)
    else:
        return "I didn't understand that."

def translate_text_to_persian(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='fa')
    return translation.text

def play_sound_with_pygame(file_path):
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"Error occurred while playing sound: {e}")
    finally:
        pygame.mixer.quit()

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    file_path = "translations.txt"

    while True:
        print("Say something in English...")

        response = recognize_speech_from_mic(recognizer, microphone)

        if response["success"]:
            print(f"You said: {response['transcription']}")
            reply = respond_to_greeting(response["transcription"])
            print(f"Response: {reply}")

            persian_translation = translate_text_to_persian(response["transcription"])
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(f"English: {response['transcription']}\nPersian: {persian_translation}\n\n")

            if reply == "exit":
                print("Exiting the program...")
                break

            tts = gTTS(reply, lang="en")
            tts.save("response.mp3")

          
            play_sound_with_pygame("response.mp3")

          
            os.remove("response.mp3")
        else:
            print("I didn't catch that. What did you say?\n")

    print("Goodbye!")
    sys.exit()

if __name__ == "__main__":
    main()
