from discord.ext import commands
import discord
from discord.ext.commands import MissingRequiredArgument, BucketType, CommandNotFound
from discord import app_commands
import os
import time
import random
from wordsList import words, words2

#Targeting message vars
cooldowns = {}
target_user_id = None

#CONST VARS
COOLDOWN_SECONDS = 10

#TODO: IF I EVER WANT TO NEATLY USE AND IMPLEMENT SLASH COMMANDS, PUT commands.GroupCog in the class instead
class Target(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    # @app_commands.command(name="ping", description="Responds with Pong!")
    # async def ping(self, interaction):
    #     await interaction.response.send_message("Pong!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_target(self, ctx, user: discord.Member):
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

    @commands.command(description="Show the current target user privately")
    async def show_target(self, ctx):

        try:
            user = await self.bot.fetch_user(target_user_id)
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

    @commands.command()
    async def clear_target(self, ctx):
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

    @commands.Cog.listener()
    # @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if target_user_id is not None and message.author.id == target_user_id:
            now = time.time()
            cooldown_expiry = cooldowns.get(message.author.id, 0)

            if now < cooldown_expiry:
                # Still on cooldown, ignore or send message
                return
            else:
                cooldowns[message.author.id] = now + COOLDOWN_SECONDS  # cooldown
                await message.channel.send(f"{message.author.mention}{random.choice(words2)}")

        # ctx = await self.bot.get_context(message)
        # if ctx.valid:
        #     await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(Target(bot))