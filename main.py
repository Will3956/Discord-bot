import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# In-memory punishment log {user_id: [ {type, reason, moderator, duration} ]}
punishments = {}

# Helper: log punishment
def add_punishment(user_id, p_type, reason, moderator, duration=None):
    if user_id not in punishments:
        punishments[user_id] = []
    punishments[user_id].append({
        "type": p_type,
        "reason": reason,
        "moderator": str(moderator),
        "duration": duration
    })

# Helper: DM user
async def dm_user(member, message):
    try:
        await member.send(message)
    except:
        pass  # user has DMs off

# ---------------- Events ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ---------------- Slash Commands ----------------
@bot.slash_command(name="kick", description="Kick a member")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    add_punishment(member.id, "Kick", reason, ctx.author)
    await ctx.respond(f"👢 {member} was kicked. Reason: {reason}")
    await dm_user(member, f"You were kicked from **{ctx.guild.name}**.\nReason: {reason}")

@bot.slash_command(name="ban", description="Ban a member")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, reason: str = "No reason", duration: str = None):
    await member.ban(reason=reason)
    add_punishment(member.id, "Ban", reason, ctx.author, duration)
    await ctx.respond(f"🔨 {member} was banned. Reason: {reason} Duration: {duration or 'Permanent'}")
    await dm_user(member, f"You were banned from **{ctx.guild.name}**.\nReason: {reason}\nDuration: {duration or 'Permanent'}")

@bot.slash_command(name="mute", description="Mute a member")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, reason: str = "No reason", duration: str = None):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role, reason=reason)
    add_punishment(member.id, "Mute", reason, ctx.author, duration)
    await ctx.respond(f"🤐 {member} has been muted. Reason: {reason} Duration: {duration or 'Indefinite'}")
    await dm_user(member, f"You were muted in **{ctx.guild.name}**.\nReason: {reason}\nDuration: {duration or 'Indefinite'}")

@bot.slash_command(name="warn", description="Warn a member")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, reason: str = "No reason"):
    add_punishment(member.id, "Warn", reason, ctx.author)
    await ctx.respond(f"⚠️ {member} was warned. Reason: {reason}")
    await dm_user(member, f"You were warned in **{ctx.guild.name}**.\nReason: {reason}")

@bot.slash_command(name="logs", description="Check punishment logs for a user")
async def logs(ctx, member: discord.Member):
    user_logs = punishments.get(member.id, [])
    if not user_logs:
        await ctx.respond(f"📂 No logs found for {member}.")
        return

    embed = discord.Embed(title=f"Punishment Logs - {member}", color=discord.Color.red())
    for i, log in enumerate(user_logs, start=1):
        embed.add_field(
            name=f"{i}. {log['type']} ({log['duration'] or 'N/A'})",
            value=f"Reason: {log['reason']}\nBy: {log['moderator']}",
            inline=False
        )
    await ctx.respond(embed=embed)

# ---------------- Run bot ----------------
keep_alive()
bot.run(os.getenv("TOKEN"))
