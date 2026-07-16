import json
import pathlib
from html2image import Html2Image

def get_bar_color(distance):
    """Return the fill color for a guess bar based on distance"""
    if distance <= 300:
        return "#12c48b"
    elif distance <= 1500:
        return "#f2994a"
    elif distance <= 2500:
        return "#ec4899"
    else:
        return "#dc2646"

def get_bar_width(distance):
    """Return the fill width (%) for a guess bar, banded to mirror Contexto's ramp"""
    if distance <= 300:
        return 100 - (distance / 300) * 35
    elif distance <= 1500:
        return 60 - ((distance - 300) / 1200) * 40
    elif distance <= 2500:
        return 18 - ((distance - 1500) / 1000) * 10
    else:
        return 4

def generate_guess_row(guess, current_word=None):
    """Generate HTML for a single guess row"""
    word = guess["word"]
    distance = guess["distance"]
    color = get_bar_color(distance)
    width = get_bar_width(distance)
    highlight_class = " highlight" if word == current_word else ""

    return f'''      <div class="guess-row{highlight_class}">
        <div class="guess-fill" style="width: {width}%; background: {color};"></div>
        <div class="guess-content">
          <span class="guess-word">{word}</span>
          <span class="guess-distance">{distance}</span>
        </div>
      </div>\n'''

def generate_guess_html(guesses, current_word=None):
    """Generate HTML for a list of guess rows"""
    return "".join(generate_guess_row(guess, current_word) for guess in guesses)

def render_game_card(channel_id=None, current_word=None):
    """Render a game card from the latest game data"""

    data_file = pathlib.Path(__file__).parent / "data.json"

    with open(data_file, "r") as f:
        data = json.load(f)

    # Use the provided channel ID or pick the one with most guesses
    if channel_id is None:
        channel_id = max(data.keys(), key=lambda k: len(data[k].get("guesses", [])))

    channel_data = data[str(channel_id)]
    guesses = channel_data.get("guesses", [])
    game_id = channel_data.get("gameId", 0)

    # Get top 10 closest guesses (guesses is sorted ascending by distance)
    top_guesses = guesses[:10]
    guess_count = len(guesses)

    # Pin the just-made guess above the list so its rank is always visible,
    # even if it didn't make the top 10
    pinned_guess = next((g for g in guesses if g["word"] == current_word), None)
    pinned_html = generate_guess_row(pinned_guess, current_word) if pinned_guess else ""

    guess_html = generate_guess_html(top_guesses, current_word)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Contexto Card</title>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      width: 500px;
      height: 1000px;
      background: #141c26;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    .card {{
      width: 100%;
      height: 100%;
      background: #141c26;
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }}

    .header {{
      display: flex;
      align-items: baseline;
      gap: 20px;
      margin-bottom: 20px;
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 0.5px;
      color: #8a9bad;
      flex-shrink: 0;
      text-transform: uppercase;
    }}

    .header .value {{
      color: #fff;
      font-size: 18px;
      font-weight: 700;
    }}

    .guesses-list {{
      display: flex;
      flex-direction: column;
      gap: 5px;
      overflow-y: auto;
      flex: 1;
    }}

    .guess-row {{
      position: relative;
      margin: 0 auto;
      padding: 0;
      height: 35px;
      margin-top: 5px;
      border-radius: 10px;
      overflow: hidden;
      background: #1c2733;
      flex-shrink: 0;
      width: 95%;
    }}

    .guess-row.highlight {{
      box-shadow: 0 0 0 2px #ffffff;
    }}

    .guess-fill {{
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      border-radius: 10px;
    }}

    .guess-content {{
      position: relative;
      z-index: 1;
      height: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 18px;
    }}

    .guess-word {{
      font-size: 19px;
      font-weight: 700;
      color: #fff;
    }}

    .guess-distance {{
      font-size: 19px;
      font-weight: 700;
      color: #fff;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <span>GAME: <span class="value">#{game_id}</span></span>
      <span>GUESSES: <span class="value">{guess_count}</span></span>
    </div>
    <div class="guesses-list">
{pinned_html}{guess_html}    </div>
  </div>
</body>
</html>'''

    return html_content

def save_card_image(output_path, channel_id, current_word=None):
    """Generate and save the card as an image"""

    html_content = render_game_card(channel_id, current_word)
    output_path = pathlib.Path(output_path)

    # Create converter, writing directly into the target directory
    hti = Html2Image(output_path=str(output_path.parent))

    # Convert HTML string to image
    hti.screenshot(html_str=html_content, save_as=output_path.name, size=(500, 570))

    print(f"Card rendered and saved to {output_path}")
    return str(output_path)

if __name__ == "__main__":
    import sys

    output_file = sys.argv[1] if len(sys.argv) > 1 else "contexto_card.png"
    channel_id = sys.argv[2] if len(sys.argv) > 2 else None

    save_card_image(output_file, channel_id)
