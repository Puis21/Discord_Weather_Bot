from discord.ext import commands
import asyncio

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx):
        user = ctx.author
        guild = ctx.guild

        async with self.bot.db_pool.acquire() as conn:
            # Insert user
            await conn.execute(
                """
                INSERT INTO discord_users (id, username, joined_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
                """,
                user.id, str(user), user.joined_at
            )

            # Insert guild
            await conn.execute(
                """
                INSERT INTO discord_guilds (id, name)
                VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                """,
                guild.id, guild.name
            )

            # Insert default settings
            await conn.execute(
                """
                INSERT INTO user_guild_settings (user_id, guild_id)
                VALUES ($1, $2)
                ON CONFLICT DO NOTHING
                """,
                user.id, guild.id
            )

        await ctx.send(f"{user.mention}, you've been registered in **{guild.name}**!")

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def sync_members(self, ctx):
        guild = ctx.guild
        batch_size = 25
        members = [m for m in guild.members if not m.bot]

        async with self.bot.db_pool.acquire() as conn:
            for i in range(0, len(members), batch_size):
                batch = members[i:i + batch_size]

                for member in batch:
                    await conn.execute("""
                            INSERT INTO discord_users (id, username)
                            VALUES ($1, $2)
                            ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
                        """, member.id, str(member))

                    await conn.execute("""
                            INSERT INTO user_guild_settings (user_id, guild_id)
                            VALUES ($1, $2)
                            ON CONFLICT DO NOTHING
                        """, member.id, guild.id)

                await asyncio.sleep(1)  # pause

        await ctx.send(f"Synced {len(members)} members in batches of {batch_size}.")

async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))