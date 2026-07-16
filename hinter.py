from google import genai
import json
import config
import pathlib

contexto_hint_file = f"{pathlib.Path(__file__).parent.resolve()}/contexto_answers.json"

client = genai.Client(
    api_key=config.GENAI_API_KEY
)

def getHint(gameid: int) -> str:
    with open(contexto_hint_file, "r") as f:
        data = json.load(f)
        answer = data.get("answers", {}).get(str(gameid), None)
        if answer is None:
            return "No hint available for this game ID."
        word = answer.strip().lower()
    prompt = f"Provide a one-word adjective hint for contexto for the word '{word}' in a few words. Don't give the answer, just a hint. Make it challenging but not impossible."
    response = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt
    )
    response.output_text = response.output_text.strip().replace(".", "").replace("!", "").replace("?", "").replace("*", "").lower()
    return response.output_text