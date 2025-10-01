import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_NAME = "mod-logs"  # channel name for logs

# ---------------- Events ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_ban(guild, user):
    # Global ban: ban user from all servers if banned in one
    for g in bot.guilds:
        if g != guild:
            try:
                await g.ban(user, reason="Global ban")
                log_channel = discord.utils.get(g.text_channels, name=LOG_CHANNEL_NAME)
                if log_channel:
                    await log_channel.send(f"🔨 {user} was globally banned (from {guild.name}).")
            except:
                pass

# ---------------- Commands ----------------
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"{member} was kicked. Reason: {reason}")
    log_channel = discord.utils.get(ctx.guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(f"👢 {member} was kicked by {ctx.author}. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"{member} was banned. Reason: {reason}")
    log_channel = discord.utils.get(ctx.guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(f"🔨 {member} was banned by {ctx.author}. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason"):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role, reason=reason)
    await ctx.send(f"{member} has been muted.")
    log_channel = discord.utils.get(ctx.guild.text_channels, name=LOG_CHANNEL_NAME)
    if log_channel:
        await log_channel.send(f"🤐 {member} was muted by {ctx.author}. Reason: {reason}")

# ---------------- Run bot ----------------
keep_alive()
bot.run(os.getenv("TOKEN"))
