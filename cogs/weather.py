# general.py
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, BucketType
from discord import app_commands
import os
import requests

weatherToken = os.getenv('WEATHER_TOKEN')

WEATHER_BASE_URL = "https://api.weatherapi.com/v1/current.json"


# normal fetch
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

#TODO: IF I EVER WANT TO NEATLY USE AND IMPLEMENT SLASH COMMANDS, PUT commands.GroupCog in the class instead
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def ping(self, ctx):
    #     await ctx.send("Pong!")

    @commands.command()
    async def weather(self, ctx, city):
        try:
            weather_info = fetch_weather(city)
            await ctx.send(f"{ctx.author.mention} For {weather_info['location']}, {weather_info['country']}: "
                           f"{weather_info['temperature_c']}°C, {weather_info['condition']}")
        except Exception as e:
            await ctx.send(f"{ctx.author.mention} Sorry, could not fetch weather for '{city}'. Error: {e}")


    @weather.error
    async def error_weather(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention} Please specify a city name!")

    # @app_commands.command(name="ping", description="Responds with Pong!")
    # async def ping(self, interaction):
    #     await interaction.response.send_message("Pong!")


async def setup(bot):
    await bot.add_cog(Weather(bot))