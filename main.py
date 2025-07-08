import asyncio
import logging
import logging.handlers
import os
from dotenv import load_dotenv

from typing import List, Optional

import asyncpg
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from aiohttp import ClientSession

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
postgres_user = os.getenv("postgres_user")
postgres_password = os.getenv("postgres_password")

bot = None

class CustomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            await ctx.send(f"{ctx.author.mention} Unknown command. Use `!help` to see available commands.")
        elif isinstance(error, MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention} Missing required argument(s).")
        else:
            await ctx.send(f"{ctx.author.mention} An unexpected error occurred.")
            raise error

    async def on_guild_join(self, guild: discord.Guild):
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO discord_guilds (id, name)
                VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
            """, guild.id, guild.name)


    async def on_member_join(self, member: discord.Member):
        if member.bot and member.guild is not None:
            return  # Skip bots

        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO discord_users (id, username)
                VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
            """, member.id, str(member))

            await conn.execute("""
                INSERT INTO user_guild_settings (user_id, guild_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
            """, member.id, member.guild.id)

async def main():
    global bot

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with ClientSession() as our_client,  asyncpg.create_pool(
        user=postgres_user, password=postgres_password, database='DiscordDB', host='localhost'
    ) as db_pool:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        exts = ["cogs.weather", "cogs.target", "cogs.database"]

        bot = CustomBot(
            "!",
            web_client=our_client,
            db_pool=db_pool,
            initial_extensions=exts,
            intents=intents,
            testing_guild_id=452227126889021440
        )

        await bot.start(token)



# Start the program
asyncio.run(main())