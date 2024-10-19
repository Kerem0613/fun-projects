import discord
from discord.ext import commands
import os
import random
from collections import deque

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Path to music folder
MUSIC_FOLDER = r'C:\Users\thunf\Music\Anasheed'

# Queue for songs
queue = deque()
is_playing = False

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready!')

async def play_next(ctx):
    global is_playing
    if queue:
        song_name = queue.popleft()  # Take next song from queue
        song_path = os.path.join(MUSIC_FOLDER, song_name)

        # Check if file exists
        if not os.path.isfile(song_path):
            await ctx.send(f"song named: {song_name} doesn't exist!")
            return

        # Play music file
        try:
            ctx.voice_client.play(discord.FFmpegPCMAudio(song_path), after=lambda e: bot.loop.create_task(play_next(ctx)))
            await ctx.send(f"Now playing: {song_name}")
        except Exception as e:
            await ctx.send(f"Error while playing song: {e}")
    else:
        await ctx.send("The queue is empty.")
        is_playing = False
        await ctx.voice_client.disconnect()  # Disconnect if there's no songs in queue

@bot.command()
async def playsong(ctx, song_name: str):
    global is_playing
    if not ctx.author.voice:
        await ctx.send("You have to be in a voice channel")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    # Add specific song to queue
    queue.append(song_name)
    await ctx.send(f"{song_name} has been added to the queue")

    if not is_playing:
        is_playing = True
        await play_next(ctx)

@bot.command()
async def playshuffle(ctx):
    global is_playing
    if not ctx.author.voice:
        await ctx.send("You have to be in a voice channel")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    # Clear queue and add music folder
    queue.clear()
    all_songs = os.listdir(MUSIC_FOLDER)

    # Show all found songs in log
    print("Found songs:", all_songs)

    if not all_songs:
        await ctx.send("No music files found in folder")
        return

    #  Check audio file format (e.g; .mp3, .wav)
    audio_files = [f for f in all_songs if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]
    random.shuffle(audio_files)  # Shuffle songs
    queue.extend(audio_files)

    if not is_playing:
        is_playing = True
        await play_next(ctx)

@bot.command()
async def next(ctx):
    global is_playing
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()  # Pause current song
        await ctx.send("Cancelled current song - playing next")
    
    await play_next(ctx)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left voice channel")
    else:
        await ctx.send("Not in any voice channel")
        
bot.run('INSERT DISCORD BOT TOKEN')
