import random

import discord
from aiohttp import request
import time
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, BucketType
import logging
from dotenv import load_dotenv
import os
import requests
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from wordsList import words
from random import choice

load_dotenv()
app = FastAPI()

#Targeting message vars
cooldowns = {}
target_user_id = None

token = os.getenv('DISCORD_TOKEN')
weatherToken = os.getenv('WEATHER_TOKEN')

WEATHER_BASE_URL = "https://api.weatherapi.com/v1/current.json"


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

botRole = "botss"

#CONST VARS
COOLDOWN_SECONDS = 5

#normal fetch
def fetch_weather(city: str):
    response = requests.get(WEATHER_BASE_URL, params={
        "key": weatherToken,
        "q": city,
        "aqi": "no"
    })

    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")

    data = response.json()
    return {
        "location": data["location"]["name"],
        "country": data["location"]["country"],
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "icon": data["current"]["condition"]["icon"],
        "last_updated": data["current"]["last_updated"]
    }

#TODO: Not needed
@app.get("/weather")
def get_weather(city: str = Query(..., description="City name to get weather for")):
    response = requests.get(WEATHER_BASE_URL, params={
        "key": weatherToken,
        "q": city,
        "aqi": "no"
    })

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch weather data"
        )

    data = response.json()
    custom_data = {
        "location": data["location"]["name"],
        "country": data["location"]["country"],
        "temperature_c": data["current"]["temp_c"],
        "condition": data["current"]["condition"]["text"],
        "icon": data["current"]["condition"]["icon"],
        "last_updated": data["current"]["last_updated"]
    }

    return custom_data

@bot.command()
@commands.has_permissions(administrator=True)
async def set_target(ctx, user: discord.User):
    global target_user_id
    target_user_id = user.id

    # Send confirmation privately to the command user
    try:
        await ctx.author.send(f"Target user set to {user.name} (ID: {user.id})")
    except discord.Forbidden:
        # If user has DMs closed, fallback to channel but warn
        await ctx.send(
            f"{ctx.author.mention} I couldn't DM you, so here's the confirmation here: Target user set to {user.name}.")

    # Delete the command message to keep the channel clean
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

@bot.command(description="Show the current target user privately")
async def show_target(ctx):

    try:
        user = await bot.fetch_user(target_user_id)
        await ctx.author.send(f"Current target: {user.name} (ID: {user.id})")
    except discord.Forbidden:
        # If user has DMs closed, fallback to channel but warn
        await ctx.send(
            f"{ctx.author.mention} I couldn't DM you, so here's the confirmation here: Target user{user.name}.")

        # Delete the command message to keep the channel clean
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

@bot.command()
async def clear_target(ctx):
    global target_user_id
    target_user_id = None

    try:
        await ctx.author.send("Target user cleared.")
    except discord.Forbidden:
        # If user has DMs closed, fallback to channel but warn
        await ctx.send(
            f"{ctx.author.mention} I couldn't DM you, target user removed")

        # Delete the command message to keep the channel clean
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

@bot.event
#@commands.cooldown(rate=1, per=30, type=BucketType.user)
async def on_message(message):
    if message.author == bot.user:
        return

    if target_user_id is not None and message.author.id == target_user_id:
        now = time.time()
        cooldown_expiry = cooldowns.get(message.author.id, 0)

        if now < cooldown_expiry:
            # Still on cooldown, ignore or send message
            return
        else:
            cooldowns[message.author.id] = now + COOLDOWN_SECONDS  # 30 seconds cooldown
            await message.channel.send(f"{message.author.mention}{random.choice(words)}")

    await bot.process_commands(message)


@bot.command()
async def weather(ctx, city):
    try:
        weather_info = fetch_weather(city)
        await ctx.send(f"{ctx.author.mention} For {weather_info['location']}, {weather_info['country']}: "
                       f"{weather_info['temperature_c']}°C, {weather_info['condition']}")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention} Sorry, could not fetch weather for '{city}'. Error: {e}")

@weather.error
async def weather(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention} Please specify a city name!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
