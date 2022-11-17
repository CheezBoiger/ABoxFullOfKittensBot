"""
    Sometimes a box full of kittens is not enough to stop the fuzz!
"""
import discord
from discord.ext import commands
import youtube_dl
import messages.hellodict as messages

import re
import os
import random
import math
import asyncio

TOKEN = 'token'
cmd_symbol = 'kat$'
client = commands.Bot(command_prefix=commands.when_mentioned_or(cmd_symbol))
players = {}

# song playlist.
# TODO: Turn this into a playlist data structure
songs = []
max_cached_songs = 25
songs_queue = []
song_format = 'mp3'
song_requests_channel = 'any'
current_song = ''
current_audio_volume = 1.0
last_song = ''


def set_volume(voice, vol: float):
    global current_audio_volume
    current_audio_volume = vol / 100.0
    voice.source.volume = current_audio_volume
    return


def parse_to_file(string):
    regex = re.compile('[/]')
    new_str = regex.sub('_', string)
    print(new_str)
    new_str = new_str.replace('?', '')
    new_str = new_str.replace('"', '\'')
    new_str = new_str.replace(':', ' -')
    return new_str


def already_cached(song):
    for temp in songs:
        if temp == song:
            return True
    return False


def cache_file(filename):
    if len(songs) >= max_cached_songs:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # We need to remove least recently used song.
        remove_song = songs[0]
        filepath = os.path.join(dir_path, remove_song)
        #print(f'song to remove {filepath}')
        os.remove(filepath)
        songs.pop(0)
    songs.append(filename)


def sort_by_time(file):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ss = os.stat(os.path.join(dir_path, file))
    return ss.st_mtime


def sort_cache_by_oldest():
    songs.sort(key=sort_by_time)


def play_song(voice, parsed_title):
    voice.play(discord.FFmpegPCMAudio(parsed_title))
    voice.source = discord.PCMVolumeTransformer(voice.source, volume=1.0)
    voice.source.volume = current_audio_volume
    return


async def check_in_voice_channel(ctx):
    if not ctx.message.author.voice.channel:
        await ctx.channel.send(f'{ctx.message.author.mention}-san, you are not in a voice channel!! ばか!!')
        return False
    if not ctx.voice_client:
        await ctx.channel.send(f'{ctx.message.author.mention}, we haven\'t joined a voice channel!!')
        return False
    return True


async def play_next(ctx, source=None):
    if len(songs_queue) >= 1:
        song_name = songs_queue[0]
        del songs_queue[0]
        vc = discord.utils.get(client.voice_clients, guild=ctx.guild)
        vc.play(discord.FFmpegPCMAudio(source), after=lambda e: play_next(ctx))
        await ctx.channel.send(f'Playing next song: f{song_name[:-4]}!')


@client.event
async def on_ready():
    # Check for existing songs. Only sort based on time modified.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path, file)
        if not os.path.isdir(filepath):
            filepath, ext = os.path.splitext(filepath)
            if ext == f'.{song_format}':
                cache_file(file)
                sort_cache_by_oldest()
    print('We have logged in as {0.user}, We will rule this serber!!'.format(client))


@client.event
async def on_message(message):
    await client.process_commands(message)


@client.command(pass_context=True, help='Make us join your voice channel!')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.channel.send(f'{ctx.message.author.mention}, you are not in voice channel!!')
        return
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.channel.send(f'{ctx.message.author.mention}, you are not in a channel!!')
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        if voice.channel == ctx.message.author.voice.channel:
            await ctx.channel.send(f'あの? {ctx.message.author.mention} We are already here!')
        else:
            await voice.move_to(channel)
            await ctx.send('We move to the other voice server!')
    else:
        await channel.connect()
        await ctx.channel.send(messages.get_joining_message())


@client.command(pass_context=True, help='Make us leave your voice channel! ( T ^ T )')
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.channel.send(f'We leave your voice channel {ctx.message.author.mention}!')
    else:
        await ctx.channel.send('We haven\'t joined a voice channel!!')


@client.command(pass_context=True, help='Have us play a song from youtube! I must be in voice chat!')
async def play(ctx, url):
    # TODO: Check if we are in a voice channel!
    # TODO: Cache existing songs!
    # TODO: Cache Playlist!
    global current_song
    global last_song
    if not await check_in_voice_channel(ctx):
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        number = int(url)
        if not voice.is_playing():
            play_song(voice, songs[number])
            last_song = current_song
            current_song = songs[number]
            await ctx.channel.send(f'We now playing {current_song[:-4]}!')
        else:
            await ctx.channel.send('Already playing song!')
    except ValueError as e:
        YDL_OPTIONS = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': song_format,
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }
        title = ''
        parsed_title = ''
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']
            parsed_title = f'{parse_to_file(title)}.{song_format}'
            if not already_cached(parsed_title):
                ydl.download([url])
                cache_file(parsed_title)
        if not voice.is_playing():
            play_song(voice, parsed_title)
            # voice.is_playing()
            # swap our last with our current
            last_song = current_song
            current_song = parsed_title
            await ctx.channel.send(f'We now playing {title}!')
        else:
            await ctx.channel.send('Already playing song!')


@client.command(pass_context=True, help='Force us to say something, senpai uwu.')
async def echo(ctx, *args):
    response = ''
    for arg in args:
        response = response + " " + arg
    await ctx.channel.send(response)


@client.command(pass_context=True, aliases=['hi'], help='Hewo owo!!')
async def hello(ctx):
    await ctx.channel.send(messages.get_hello_message())


@client.command(pass_context=True)
async def queue(ctx, url):
    return


@client.command(pass_context=True, help='Make us stop the current song!')
async def stop(ctx):
    if not await check_in_voice_channel(ctx):
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()


@client.command(pass_context=True, help='Make us pause the song, can be resumed later uwu.')
async def pause(ctx):
    if not await check_in_voice_channel(ctx):
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()


@client.command(pass_context=True, help='Make us resume the current paused song!')
async def resume(ctx):
    if not await check_in_voice_channel(ctx):
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()


@client.command(pass_context=True, help='Roll a number between 0 and your specified number, senpai!')
async def roll(ctx, max_roll):
    if max_roll == None:
        await ctx.channel.send('Give us a max number to roll, senpai!!')
    max_roll = int(max_roll)
    if max_roll < 1:
        await ctx.channel.send(f'ばか {ctx.message.author.mention}!! We can not roll less than 1!!!')
    number = random.randint(0, max_roll)
    indefinite = 'a'
    if number != 0:
        string = repr(number)
        if string.startswith('8') or string.startswith('11'):
            indefinite = 'an'
    await ctx.channel.send(f'We roll {indefinite} {number}!')


def clamp(value, mi, ma):
    return max(mi, min(ma, value))


@client.command(pass_context=True, help='Adjust our voice between [0-100]')
async def volume(ctx, vol):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    vol = clamp(int(vol), 0, 100)
    if voice and voice.source:
        set_volume(voice, float(vol))
        await ctx.channel.send(f'We adjusted our volume! Currently: {vol}')
    else:
        await ctx.channel.send(f'{ctx.message.author.mention}-san, we can\' adjust volume! No current song!')


@client.command(pass_context=True, description='Replay the last song!', help='Replay a last song!')
async def replay(ctx):
    if not await check_in_voice_channel(ctx):
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if current_song != '':
        if voice.is_playing():
            await ctx.channel.send('Currently playing a song! If you want to play something new, stop me first!!')
            return
        play_song(voice, current_song)
        await ctx.channel.send(f'Repeating last song! {current_song[:-4]}')
    else:
        await ctx.channel.send('We don\'t have a last song on record!')


@client.command(pass_context=True, help='Look at past songs!')
async def seelist(ctx):
    if len(songs) == 0:
        await ctx.channel.send('No songs are currently found from last records, Senpai!!')
        return
    results = ''
    count = 0
    for song in songs:
        results += f'{count}. ' + song[:-4] + '\n'
        count += 1
    await ctx.channel.send(f'Here are the songs we found from last record!\n{results}')


@client.command(pass_context=True, help='Your onee sans have surprises too uwu')
async def hentai(ctx):
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', messages.get_hentai_img())
    await ctx.channel.send(file=discord.File(filepath))
    return


@client.command(pass_context=True, help='Run a youtube playlist online!')
async def playlist(ctx, url):
    return

client.run(TOKEN)
