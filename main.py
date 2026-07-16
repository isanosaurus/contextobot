import aiohttp
import nextcord
from nextcord.ext import commands
import config
import pathlib
import random
import json
import asyncio
from render_card import save_card_image
from hinter import getHint

API_BASE = config.API_BASE
data_file = f"{pathlib.Path(__file__).parent.resolve()}/data.json"
client = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

def addChannel(channelid):
    base_structure = {
        "gameId": None,
        "channelId": channelid,
        "lastMessageId": None,
        "guesses": []
    }
    with open(data_file, "r") as f:
        data = json.load(f)
        if str(channelid) not in data.keys():
            data[str(channelid)] = base_structure
        with open(data_file, "w") as f:
            json.dump(data, f, indent=4)
        f.close()
        return data[str(channelid)]

def getChannelGameId(channelid: int):
    with open(data_file, "r") as f:
        data = json.load(f)
        if str(channelid) not in data:
            return None
        f.close()
        return data.get(str(channelid), {}).get("gameId", None)

def generateGameID(channelid: int):
    gameid = getChannelGameId(channelid)
    if gameid is None:
        with open(data_file, "r") as f:
            data = json.load(f)
            if str(channelid) not in data:
                addChannel(channelid)
            data[str(channelid)]["gameId"] = 1
            with open(data_file, "w") as f:
                json.dump(data, f, indent=4)
            f.close()
        return 1
    else:
        with open(data_file, "r") as f:
            data = json.load(f)
            if str(channelid) not in data:
                addChannel(channelid)
            data[str(channelid)]["gameId"] = int(gameid) + 1
            data[str(channelid)]["lastMessageId"] = None
            with open(data_file, "w") as f:
                json.dump(data, f, indent=4)
            f.close()
        return int(gameid) + 1
    
def sortGuessesByDistance(channelid: int):
    with open(data_file, "r") as f:
        data = json.load(f)
        if str(channelid) not in data:
            addChannel(channelid)
        guesses = data.get(str(channelid), {}).get("guesses", [])
        sorted_guesses = sorted(guesses, key=lambda x: x["distance"])
        data[str(channelid)]["guesses"] = sorted_guesses
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)


def addGuess(word, distance, gameID, userid, channelid):
    with open(data_file, "r") as f:
        data = json.load(f)
        if word in [guess["word"] for guess in data.get(str(channelid), {}).get("guesses", [])]:
            return None
        if str(gameID) not in data[str(channelid)]:
            data[str(channelid)]["guesses"].append({"word": word, "distance": distance, "userId": userid})
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)
    sortGuessesByDistance(channelid)
    if distance == 0:
        return True

def clearGuesses(channelid: int):
    with open(data_file, "r") as f:
        data = json.load(f)
        if str(channelid) not in data:
            addChannel(channelid)
        data[str(channelid)]["guesses"] = []
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

async def getWordDistance(word: str, gameID: int) -> int:
    url = f"{API_BASE}/{gameID}/{word}"
    with open(data_file, "r") as f:
        data = json.load(f)
        if word in [guess["word"] for guess in data.get(str(gameID), {}).get("guesses", [])]:
            return data[str(gameID)]["guesses"][word]["distance"]
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            await session.close()
            print(response.status, await response.text())
            if response.status == 200:
                data = await response.json()
                return data.get("distance", False)
            elif response.status == 404:
                return None
            else:
                return False

async def status_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await client.change_presence(activity=nextcord.Game(name="RNV Simulator"))
        await asyncio.sleep(60)
        await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="Felix' schnarchen"))
        await asyncio.sleep(60)
        await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.streaming, name="Du musst rauchen.", url="https://www.twitch.tv/jesnzip"))
        await asyncio.sleep(60)
        await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="Awruff!"))

async def scrape_loop():
    await client.wait_until_ready()
    print("Starting scrape loop...")
    while not client.is_closed():
        try:
            from scrape_contexto import scrape
            scrape()
        except Exception as e:
            print(f"Error in scrape_loop: {e}")
        await asyncio.sleep(3600)  # Scrape every hour

@client.event
async def on_ready():
    print(f"{client.user} has logged in!")
    client.loop.create_task(status_loop())
    client.loop.create_task(scrape_loop())

@client.event
async def on_message(message: nextcord.Message):
    message_content = message.content.lower()
    if message.author == client.user:
        return
    
    if message_content.startswith("!hint") or message_content.startswith("!h"):
        hint_messages = [
            "Motivating the electrons...",
            "Waking up the hamsters in the wheel...",
            "Polishing the bits...",
            "Brewing coffee for the server...",
            "Sorting the zeros and ones...",
            "Yelling at the CPU...",
            "Pushing data through the tube...",
            "Server is catching its breath...",
            "Placing pixels by hand...",
            "Processing backend bureaucracy...",
            "Still looking for the right cable...",
            "Loading bar pretends to do something...",
            "Intern is searching for the file...",
            "Greasing the gears...",
            "Preparing the magic...",
            "Almost done (lying)...",
            "Server is still thinking...",
            "Politely asking the connection to work...",
            "The last 10% always takes the longest...",
            "Making up the result...",
            "Reticulating splines...",
            "Convincing the database to cooperate...",
            "Dividing by zero...",
            "Bribing the servers to go faster...",
            "Untangling the wires...",
        ]
        try:
            random_hint_message = random.choice(hint_messages)
            msg = await message.reply(f"<a:loading:1527367411756433419> {random_hint_message}")
            gameID = getChannelGameId(message.channel.id)
            if not gameID:
                embed = nextcord.Embed(title="Oopsies!", description="No game ID found for this channel.", color=nextcord.Color.red())
                embed.add_field(name="Wanna start a game?", value="Use the command `/start` to start a new game in this channel.")
                await message.reply(embed=embed)
                return
            hint = getHint(gameID)
            embed = nextcord.Embed(title="Hint", description=f"Here's your hint: **{hint}**", color=nextcord.Color.blue())
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            print(f"Error in hint command: {e}")
            embed = nextcord.Embed(title="Oopsies!", description="Something went wrong while fetching the hint.", color=nextcord.Color.red())
            await message.reply(embed=embed)

    if message_content.startswith("guess ") or message_content.startswith("g "):
        parts = message_content.split(" ")
        word = parts[1]

        gameID = getChannelGameId(message.channel.id)
        if not gameID:
            embed = nextcord.Embed(title="Oopsies!", description="No game ID found for this channel.", color=nextcord.Color.red())
            embed.add_field(name="Wanna start a game?", value="Use the command `/start` to start a new game in this channel.")
            await message.reply(embed=embed)
            return
        distance = await getWordDistance(word, gameID)
        if distance is None:
            embed = nextcord.Embed(title="Oopsies!", description="Something went wrong while fetching the distance.", color=nextcord.Color.red())
            embed.add_field(name="Did you type in english?", value="Contexto only supports english words.")
            await message.reply(embed=embed)
            return
        
        msg = await message.reply(f"https://klipy.com/gifs/loading-discord-discord-loading")
        
        add = addGuess(word, distance, gameID, message.author.id, message.channel.id)
        if add is True:
            try:
                card_image_path = f"{pathlib.Path(__file__).parent.resolve()}/contexto_card_{message.channel.id}.png"
                save_card_image(card_image_path, message.channel.id, word)
                data = json.load(open(data_file, "r"))
                user = await client.fetch_user(data[str(message.channel.id)]["guesses"][-1]["userId"])
                embed = nextcord.Embed(title="Congratulations!", description=f"You guessed the correct word: **{word}**", color=nextcord.Color.green())
                await msg.edit(file=nextcord.File(card_image_path), embed=embed, content="")
                clearGuesses(message.channel.id)
                new_embed = nextcord.Embed(title="New Game Started!", description=f"A new game has been started in this channel.\nGame ID: **{generateGameID(message.channel.id)}**", color=nextcord.Color.green())
                await message.channel.send(embed=new_embed)
            except Exception as e:
                print(f"Error rendering card: {e}")
                embed = nextcord.Embed(title="Oopsies!", description="Something went wrong while rendering the game card.", color=nextcord.Color.red())
                await msg.edit(embed=embed, content="")
            finally:
                return
        # Generate and render the card image
        try:
            card_image_path = f"{pathlib.Path(__file__).parent.resolve()}/contexto_card_{message.channel.id}.png"
            save_card_image(card_image_path, message.channel.id, word)
            await msg.edit(file=nextcord.File(card_image_path), content="")
        except Exception as e:
            print(f"Error rendering card: {e}")
            embed = nextcord.Embed(title="Oopsies!", description="Something went wrong while rendering the game card.", color=nextcord.Color.red())
            await msg.edit(embed=embed, content="")

@client.slash_command(name="start", description="Start a new game in this channel.")
async def start_game(interaction: nextcord.Interaction):
    channelid = interaction.channel.id

    gameID = generateGameID(channelid)

    addChannel(channelid)
    with open(data_file, "r") as f:
        data = json.load(f)
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

    embed = nextcord.Embed(title="New Game Started!", description=f"A new game has been started in this channel.\nGame ID: **{gameID}**", color=nextcord.Color.green())
    await interaction.response.send_message(embed=embed)


client.run(config.TOKEN)


        