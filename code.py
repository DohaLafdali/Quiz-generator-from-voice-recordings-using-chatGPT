import streamlit as st
import sounddevice as sd
import soundfile as sf
import openai
import speech_recognition as sr
import json
import google.auth
from googleapiclient import discovery
from google.oauth2 import service_account
import json
import webbrowser
from oauth2client import client, file, tools
from googleapiclient.http import HttpRequest
from httplib2 import Http
from PIL import Image
import config

# Set up your OpenAI API key
api_key = config.API_KEY
openai.api_key = api_key 

questions = []
choices = []
st.set_page_config(page_title="SpeechQuizzer", page_icon="Speech2.png")
def generate_google_form():
    
    SCOPES = "https://www.googleapis.com/auth/forms.body"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    store = file.Storage('token.json')
    creds = None
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build('forms', 'v1', http=creds.authorize(
        Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

    # Request body for creating a form
    NEW_FORM = {
        "info": {
            "title": "SpeechQuizzer",
        }
    }
    # Request body to add a multiple-choice question
    NEW_QUESTION = {
        "requests": []
    }
    for i in range(len(questions)):
        question = questions[i]
        options = list(choices[i])
        create_item = {
            "createItem": {
                "item": {
                    "title": question,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": option} for option in options
                                ],
                                "shuffle": True
                            }
                        }
                    }
                },
                "location": {
                    "index": 0
                }
            }
        }

        NEW_QUESTION["requests"].insert(0,create_item)

    # Creates the initial form
    result = form_service.forms().create(body=NEW_FORM).execute()
    responder_uri = result['responderUri']

    # Adds the question to the form
    question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTION).execute()
    #print('Questions ', question_setting)
    # Prints the result to show the question has been added
    get_result = form_service.forms().get(formId=result["formId"]).execute()
    #print('get-result',get_result)
    
    return responder_uri
#remove made with streamlit
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def main():
    if "text" not in st.session_state:
        st.session_state["text"] = ""
    
    st.header("Hello 👋, would you like to generate a quiz?" ) 
    st.text("Click on  button '🎙️ Start Recording ' and simply state your topic,everything will be generated.")  
    st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            margin-left: -30px;
            margin-top: -140px;
            padding-top: -15px;

        }
        .css-1629p8f.e16nr0p31 h1 {
         margin-top: -60px;
        }
        [data-testid=stSidebar] h1{
            font-size: 32px;
    font-weight: bold;
    text-align: center;
    color: #C3DAF9;
    padding: 10px;
    border-radius: 5px;
    text-shadow: 2px 2px 4px rgba(0, 0.3, 0.5, 1);
  
        }
        [data-testid=stSidebar] h3{
         color: #333333;
         text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }
        [data-testid=stSidebar] {
         color: #333333;
        }
    </style>
    """, unsafe_allow_html=True
    )     
    def add_logo(logo_path, width, height):
        """Read and return a resized logo"""
        logo = Image.open(logo_path)
        modified_logo = logo.resize((width, height))
        return modified_logo

    my_logo = add_logo(logo_path="Speech.png", width=200, height=180)
    st.sidebar.image(my_logo)
    # Titre de l'application
    st.sidebar.title("Welcome to  :blue[_SpeechQuizzer!_]")
    # Introduction et description de l'application
    st.sidebar.subheader("👀 About ")
    st.sidebar.markdown("Welcome to SpeechQuizzer! Test your speech and quiz skills with our interactive app. Improve your speaking, listening and thinking skills by answering engaging questions. Get ready to take on the challenge and become a true master of speech. Let the adventure begin!")
    st.sidebar.markdown("Follow the steps below to use the app:")
    # Instructions d'utilisation
    st.sidebar.subheader("👉 Instructions")
    st.sidebar.markdown("1. Click the 'Record' button to start audio recording.")
    st.sidebar.markdown("2. When the recording is complete, the audio file will be displayed.")
    st.sidebar.markdown("3. Click on the 'Generate Quiz' button to generate a quiz based on the transcribed text.")
    st.sidebar.markdown("4. The generated quiz will appear on the screen with the questions and possible choices.")
    st.sidebar.markdown("5. You can then copy the link to the Google Form containing the quiz.")
    # Témoignages ou commentaires des utilisateurs
    st.sidebar.subheader("⭐Testimonials")
    st.sidebar.markdown("Here is what our satisfied users say:")
    # Afficher les témoignages ou les commentaires des utilisateurs
    # Liens sociaux ou de contact
    st.sidebar.subheader("📇Contact")
    st.sidebar.markdown("You can contact us or follow us on social networks:")
     # Exemples ou démonstrations
    st.sidebar.subheader("Exemples")
    st.sidebar.markdown("Voici quelques exemples d'enregistrements audio et de quiz générés précédemment :")
    # Inclure des exemples ou des démonstrations sous forme de texte, d'images ou de vidéos
    # FAQ
    st.sidebar.subheader("FAQ")
    st.sidebar.markdown("Voici les réponses aux questions fréquemment posées :")
    # Inclure une liste de questions fréquentes avec leurs réponses
    response = None  # Initialize response with a default value
    # Display a button to start recording audio
    col = st.columns(2)
    st.markdown(
    """
    <style>
    .ou{
    margin-left: 170px;
    text-align: left;
    margin-top: 15px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);

    }
    div.stButton > button:first-child {
    background-color: #C3DAF9;
    color:#333333;
    height:3em;
    width:30em;
    border-radius:10px 10px 10px 10px;
    }
    </style>
    """,
    unsafe_allow_html=True)   
    col[1].markdown(
    """
    <p class="ou">
    press to record ↵
    </p>
    """,
    unsafe_allow_html=True)  
    
    if col[0].button("🎙️ Start Recording"):
        # Start recording audio
        fs = 44100  # Sample rate
        duration = 5  # Duration in seconds
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)

        # Wait for the recording to finish
        sd.wait()

        # Save the recorded audio to a WAV file
        wav_file = "audio.wav"
        sf.write(wav_file, recording, fs)

        # Display the recorded audio
        st.audio(wav_file)

        # Convert the audio to text using Google Speech-to-Text API
        # Start the transcription
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio = recognizer.record(source)

        # Wait for the transcription to finish
        try:
            transcribed_text = recognizer.recognize_google(audio, language="en-US")
        except sr.UnknownValueError:
            print("Speech recognition failed")
        except sr.RequestError as e:
            print("An error occurred: {}".format(e))
        text = recognizer.recognize_google(audio)
        # Display the converted text in the prompt
        st.session_state["text"] = transcribed_text
        st.text_area("Transcribed Text", value=transcribed_text)
                
    if st.button("🪄 Generate Quiz"):
        # Generate quiz questions based on the audio prompt using the ChatGPT API
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Generate a quiz with 8 questions. Each question should have 3 choices. The following text is the audio prompt: {st.session_state['text']}",
            temperature=0.7,
            max_tokens=800,
            n=1,  # Number of quiz questions to generate
        )

        # Display the generated quiz questions
        st.subheader("Generated Quiz Questions:")
        quiz_questions = set()  # Use a set to store unique questions
        for i, choice in enumerate(response.choices):
            question = choice["text"].strip()
         # Split the text into questions and choices
            questions_and_choices = question.split("\n\n")
         # Extract each question and choices
            for qa in questions_and_choices:
                qa = qa.strip()
                if qa:
                    parts = qa.split("\n")
                    question = parts[0].strip()
                    choices.append(parts[1:])
                    questions.append(question)
        ques_tabs = st.tabs(["Question 1", "Question 2", "Question 3", "Question 4", "Question 5","Question 6","Question 7","Question 8"])
        # Display the questions and choices
        for i, question in enumerate(questions):
            if i < len(ques_tabs):
                with ques_tabs[i]:
                    st.write(f"Question : {question}")
                    if i < len(choices):
                        for j, choice in enumerate(choices[i]):
                            st.write(f"Choice {choice}")
                            print()
            else:
                st.write("Not enough tabs for questions")
            
        st.write(f"Google Form generated: [Link]({generate_google_form()})")

        
if __name__ == "__main__":
    main()
