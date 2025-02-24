from dotenv import load_dotenv
import os
import google.generativeai as genai
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_fact():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """Generate me a fact of bleach , the fact should be rare, amazing, mind blowing. keep the language simple. They should be derived from light novels, mangas etc that were not present in anime or something. It should be deep from the story content don't worry about spoiling just go wwith it. explain the fact between "80 to 110" . use words like : did you know, remember when. keep the script catchy and must keep the reader hooked. start right away with words rather than saying salutatuions. also dont write extra words like okay here is your script. I just need the the fact merged with the script not them independent like fact1+script should be one point not them separately. I have to feed it to an AI voice tts engine so make it the way the tts engine could spell each word of the anime correctly. like for names like ywach make the word be written as it would be pronounced i.e yuhabaha. dont't worrry about spelling changes. so make it calm mysterious and to the point start reightway without sayig alright, listen up etc, just start with remember, did you know etc. If there are seperate paragagraohs, merge them into 1."""
    response = model.generate_content(prompt)
    return response.text
