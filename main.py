from flask import Flask,render_template,redirect,request,session
import google.generativeai as genai
import requests,shutil
import fal_client
from dotenv import load_dotenv
import time
import os
import random

load_dotenv()

app = Flask(__name__)
app.secret_key = "TQ😘"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

ai_art_prompts = [
    "Mountain sunrise",
    "Ocean sunset",
    "Neon city",
    "Glowing forest",
    "Steampunk airship",
    "Melting desert",
    "Dew web",
    "Bioluminescent sea",
    "Tree face",
    "Cosmic nebula",
    "Snow train",
    "Fairy tea",
    "Cyberpunk samurai",
    "Mechanical dragon",
    "Renaissance fruit",
    "Geometric patterns",
    "Expressive eyes",
    "Pixel level",
    "Floating island",
    "Autumn lake",
    "Stormy sea",
    "Phoenix rising",
    "Architectural sketch",
    "Mythical clay",
    "Butterfly wing",
    "Blooming flower",
    "Glitch landscape",
    "Vintage car",
    "Stained window",
    "Botanical line",
    "Futuristic ship",
    "Dreamscape float",
    "Eye reflection",
    "Starry desert",
    "Zodiac art",
    "Superhero flight",
    "Island map",
    "Vehicle cross",
    "Robotic hand",
    "Time concept",
    "Fluid abstract",
    "Snowy cottage",
    "Vintage collage",
    "Claymation walk",
    "Light trails",
    "Fractal pattern",
    "Steaming coffee",
    "Medieval interior",
    "Animal portrait",
    "Sunflower field",
    "Retro poster",
    "Forest run",
    "River village",
    "Flowing hair",
    "Storm cloud",
    "Mermaid reef",
    "Hand sketch",
    "Face clay",
    "Snowflake macro",
    "Moving clouds",
    "Glitch face",
    "Garage bike",
    "Nature glass",
    "Skeleton line",
    "Underwater city",
    "Impossible dream",
    "Glowing orb",
    "Meteor shower",
    "Celestial art",
    "Knight dragon",
    "Treasure map",
    "Robot cross",
    "Robotic eye",
    "Memory concept",
    "Geometric abstract",
    "Night street",
    "Nature collage",
    "Paper dance",
    "Light draw",
    "Fractal landscape",
    "Sushi plate",
    "Gothic interior",
    "Plant portrait",
    "Lavender field",
    "Horror poster",
    "Mountain climb",
    "Desert oasis",
    "Rainy street",
    "Forest fire",
    "Centaur gallop",
    "Skull sketch",
    "Fantasy clay",
    "Leaf droplet",
    "Rotating stars",
    "Glitch city",
    "Desk typewriter",
    "History glass",
    "Insect line",
    "Space station",
    "Shifting dream",
    "Tattoo face",
    "Volcano eruption",
    "Mythical art",
    "Wizard spell",
    "Lost map",
    "Robot cross",
    "Robot animal",
    "Consciousness concept",
    "Organic abstract",
    "Cozy library",
    "Tech collage",
    "Toy race",
    "Light sculpture",
    "Cosmic fractal",
    "Wine grapes",
    "Baroque interior",
    "Cloud portrait",
    "Cherry orchard",
    "Silent poster",
    "River swim"
]
question = random.choice(ai_art_prompts)

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

@app.route('/')
def home():
    session["P1PROMPTHIST"] = []
    session["P2PROMPTHIST"] = []    
    print("initialised prompt history")
    return render_template("index.html")

@app.route('/player1',methods=['GET','POST'])
def player1():
    player1prompt = request.form.get('player1inpt')
    FinalSubmit = request.form.get('FinalSubmit')
    reply = ""
    if player1prompt:
        # response = model.generate_content(player1prompt)
        # reply = response.text #this will be an image url
        prompthist = session.get("P1PROMPTHIST")
        prompthist.append(player1prompt)
        session["P1PROMPTHIST"] = prompthist
        player1prompt = " ".join(session.get("P1PROMPTHIST"))
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": player1prompt,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        reply = result["images"][0]["url"]
        session["P1"] = reply
    if FinalSubmit:
        if session.get("P1"):
            imgresp = requests.get(session.get("P1"),stream=True)   
            with open("static/images/Player1.jpg","wb") as f:
                shutil.copyfileobj(imgresp.raw,f)
        time.sleep(5)
        return redirect('/winner')
    return render_template("Player1.html",reply=reply,question=question)

@app.route('/player2',methods=['GET','POST'])
def player2():
    player2prompt = request.form.get('player2inpt')
    FinalSubmit = request.form.get('FinalSubmit')
    reply = ""
    if player2prompt:
        # response = model.generate_content(player2prompt)
        # reply = response.text
        # reply = "https://fal.media/files/penguin/a7_SExdI7g13hkjzkU6oM_cc1dbb714c32424f9979b2ae98592284.jpg"
        prompthist = session.get("P2PROMPTHIST")
        prompthist.append(player2prompt)
        session["P2PROMPTHIST"] = prompthist
        player2prompt = " ".join(session.get("P2PROMPTHIST"))
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": player2prompt,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        reply = result["images"][0]["url"]
        session["P2"] = reply
    if FinalSubmit:
        if session.get("P2"):
            imgresp = requests.get(session.get("P2"),stream=True)   
            with open("static/images/Player2.jpg","wb") as f:
                shutil.copyfileobj(imgresp.raw,f)
        time.sleep(5)
        return redirect('/winner')
    return render_template("Player2.html",reply=reply,question=question)

@app.route("/winner",methods=['GET','POST'])
def winner():
    player1 = session.get("P1")
    player2 = session.get("P2")
    winner = ""
    if player1 and player2:
        uploaded_file_1 = genai.upload_file(path="static/images/Player1.jpg", display_name="P1")
        uploaded_file_2 = genai.upload_file(path="static/images/Player2.jpg", display_name="P2")
        prompt = f"""You are the judge of an AI ART GENERATING competition.
                    the contestants were asked to write a prompt to make an image on
                    {question}.
                    Compare the two images and decide who is the winner.
                    Reply with Image 1 for Player 1 and Image 2 for Player 2.
                    The first word of your reply should be Player 1 or Player 2."""
        response = model.generate_content([uploaded_file_1, uploaded_file_2, prompt])
        winner = response.text
        session["P1PROMPTHIST"] = []
        session["P2PROMPTHIST"] = []    
        session.pop("P1")
        session.pop("P2")
    return render_template("Winner.html",winner=winner)
if __name__ == '__main__':

    app.run(debug=True)     