
# @bot.event
# async def on_ready():
#     print(f"Ready, {bot.user.name}")
#
# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server {member.name}")
#
# @bot.command()
# async def assign(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=botRole)
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"{ctx.author.mention} is now asssigned to {botRole}")
#     else:
#         await ctx.send("Role doesn't exist")
#
# @bot.command()
# async def remove(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=botRole)
#     if role:
#         await ctx.author.remove_roles(role)
#         await ctx.send(f"{ctx.author.mention} is now removed from {botRole}")
#     else:
#         await ctx.send("Role doesn't exist")
#
# @bot.command()
# @commands.has_role(botRole)
# async  def secret(ctx):
#     await ctx.send("Welcome to secret")
#
# @secret.error
# async def secret_error(ctx, error):
#     if isinstance(error, commands.MissingRole):
#         await ctx.send("No permission")
#
#
# @bot.command()
# async def dm(ctx, *, msg):
#     await ctx.author.send(f"You said {msg}")
#
# @bot.command()
# async def reply(ctx):
#     await ctx.reply("This is a reply")