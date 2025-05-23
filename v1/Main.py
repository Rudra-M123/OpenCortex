import os
import json
import ollama
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyttsx3
import actionsList

# kFLFBx9T7XJmrr3p2F/fmAj+8DS8GqnKeq/TOIAPcuI=
# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Persistent actions file
ACTIONS_FILE = 'actions.json'

class VirtualAssistant:
    def __init__(self, STT_bool, TTS_bool):
        self.name = input("Your name: ").capitalize()
        print(f"Welcome {self.name}.")
        self.model = "phi3"
        self.actions = self.load_actions()
        self.STT_bool = STT_bool
        self.TTS_bool = TTS_bool
        self.run()
    
    def run(self):
        while True:
            user_input = self.get_input(self.STT_bool)
            if user_input.lower() in ["stop", "bye"]:
                break
            self.process_input(user_input)
        
        print("Over and out.")

    def load_actions(self):
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: The file {ACTIONS_FILE} contains invalid JSON. Loading default actions.")
                return {}
            except Exception as e:
                print(f"Error loading actions: {e}")
                return {}
        return {}

    def save_actions(self):
        with open(ACTIONS_FILE, 'w') as f:
            json.dump(self.actions, f, indent=4)

    def unified_search(self, query):
        prompt = query.replace(" ", "-")
        search_url = f"https://www.google.com/search?q={prompt}"

        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for g in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
            results.append(g.get_text())
        return results[0:4] if len(results) > 5 else ("Sorry, I couldn't fetch the details right now." if len(results) == 0 else results[0:len(results) -1])
    
    def query_model(self, prompt):
        response = ollama.generate(model=self.model, prompt=prompt)
        return response["response"]

    def process_input(self, prompt):
        for action in self.actions:
            if action in prompt.lower():
                returnAction = self.execute_action(self.actions[str(action)])
                break
        else: 
            if "learn" in input("Action not recognized. Do you want to learn a new action or should I answer your question? (Learn/Answer): ").lower():
                tag = input("What is the function tag? ")
                func_name = input("What is the function name? ")
                params = input("List all parameters, space separated if any. ")
                params_list = [p.strip() for p in params.split() if p.strip()]
                newAction = {tag: {"function": func_name, "parameters": params_list}}
                
                returnAction = self.learn_actions(newAction)
            else:
                returnAction = self.get_response(prompt)

        return self.respond(returnAction)

    def get_response(self, prompt):
        response = self.query_model(f"Can this prompt be answered by you with at least 90% confidence or truthfulness: {prompt}. If yes, say \'yes\'. If no, requires the internet, real-time information, further research or etc, answer with a \'no\'.")
        
        return self.query_model(prompt) if "yes" in response else self.query_model(f"Alright, here's what I've got from my research: {self.unified_search(prompt)}. Now, answer the user's question: {prompt}. Consider it all part of my understanding. Since I'm not just summarizing someone else's work, make sure your response is accurate and relevant.")
    
    def execute_action(self, action):
        function = getattr(actionsList, action['function'])
        return function(*action['parameters'])
    
    def learn_actions(self, action):
        tag=list(action.keys())[0]
        action_name = action[tag]['function']

        functionExist =  any(action[tag] == v for v in self.actions.values() if isinstance(v, dict))

        if(not functionExist):
            # Create a string that contains the function definition based on the function_info dictionary.
            parameters = ", ".join(action[tag]["parameters"])
            callableParams = "parameter/s: {" + parameters.replace(', ', '}, {') + '}' if action[tag]['parameters'] != [] else 'no parameters.' 

            function_string = f"\ndef {action_name}({parameters}):\n\treturn f'Function {action_name} called with {callableParams}'\n"
                
            with open(f"{actionsList.__name__}.py", "a") as f:
                f.write(function_string)
            
            # Dynamically load the new action
            exec(function_string, globals())
            setattr(actionsList, action_name, globals()[action_name])
            self.actions.update(action)

            # Save actions to file
            self.save_actions() # for the JSON
            
            return f"Learned new action: {action_name}()"
        return "Action already exists."
    
    def get_input(self, speak_bool):
            print(f"{self.name}:", end=" ")
            return self.listen() if speak_bool else input()
    
    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
            try:
                return r.recognize_google(audio)
            except sr.UnknownValueError:
                return "Sorry, I did not understand that."
    
    def speak(self, text):
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    def respond(self, response):
        print("AI:", response)
        if(self.TTS_bool):
            self.speak(response)

if __name__ == "__main__":
    VirtualAssistant(input("Speak input? (Y/N): ").lower() == 'y', input("Speak output? (Y/N): ").lower() == 'y')
