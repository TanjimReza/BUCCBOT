#--------------------- Requirements ---------------------#
import discord
from discord import member
from discord.ext import commands
import gspread
from gspread.utils import accepted_kwargs
#--------------------------------------------------------#
#Setting Bot Command 
bot = commands.Bot(command_prefix='$')
bot.remove_command("help")
#---------------------- Necessary Variables ----------------------#
# HIDDEN

LOG_CHANNEL_ID = 000000 #*Bot will print logs in this channel 
REALTIME_LOG_CHANNEL_ID = 000000 #*Realtime Log here

# channel = bot.get_channel(LOG_CHANNEL_ID)
# await channel.send(ONLINE_MESSAGE)
BOT_TOKEN = "ENV_TOKEN"
ONLINE_MESSAGE = "Bot Online!"
gc = gspread.service_account(filename='creds.json')
sh = gc.open_by_key('ENV_KEY')
worksheet = sh.sheet1
# pyinstaller -D -F -n main -c "main.py"
#-----------------------------------------------------------------#
ID_COL = 2 
NAME_COL = 3
DEPT_COL = 4
COURSES_COL = 5
async def info(id):
    realtime_log = bot.get_channel(REALTIME_LOG_CHANNEL_ID)
    id_list = worksheet.col_values(ID_COL)[1:]
    if id in id_list:
        name = worksheet.col_values(NAME_COL)[1:]
        dept = worksheet.col_values(DEPT_COL)[1:]
        coursec = worksheet.col_values(COURSES_COL)[1:]
        idx = id_list.index(id)
        courses_list = [x.strip() for x in coursec[idx].split(",")]
        data = [id_list[idx],name[idx], dept[idx],courses_list]
        # print("Data Found:",data)
        
        await realtime_log.send(f"Found: {data}")
    else:
        # null_list = ['none', 'none2', 'none3', 'none4']
        null_list = None
        data = null_list
        # print("No data found for user, returning None")
        await realtime_log.send(f"No data found for this user")
    return data

async def create_embed(student_id,student_name,discord_username): 
    embed=discord.Embed(title="Member Verification", description="Approving BUCC Academy Members", color=0xff0000)
    embed.add_field(name="Name", value=student_name, inline=True)
    embed.add_field(name="Student ID", value=student_id, inline=True)
    embed.add_field(name="Discord ID", value=discord_username, inline=True)
    return embed

#-----------------------------------------------------------------#

#Sending Starting Message 
@bot.event
async def on_ready():
    # channel = bot.get_channel(LOG_CHANNEL_ID)
    # await channel.send(ONLINE_MESSAGE)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    realtime_log = bot.get_channel(REALTIME_LOG_CHANNEL_ID)
    await log_channel.send("BOT RESTARTED!")
    print("Bot Online message sent!")
    await bot.change_presence(activity=discord.Game(name="BUCC"))
    print("Set Online Activity")
    await realtime_log.send("``======== DEBUGING ON ========``")
#----------------------------------------------------------#

@bot.command()
async def author(ctx, message): 
    user = ctx.message.author
    author = user
    await ctx.message.reply(author)

@bot.group(invoke_without_command=True)
async def help(ctx): 
    embed=discord.Embed(title="Commands Help", description="Get verified by following the example command")
    embed.add_field(name="Approve Yourself in the Server", value="$approve StudentID", inline=True)
    embed.add_field(name="Example:", value="$approve 10203040", inline=False)
    await ctx.send(embed=embed)
@bot.command()
async def approve(ctx, message): 
    # log_channel = bot.get_channel(LOG_CHANNEL_ID)
    realtime_log = bot.get_channel(REALTIME_LOG_CHANNEL_ID)
    member_id = message
    await realtime_log.send(f"``----{ctx.message.author}:{member_id}-----``")
    info_data = await info(str(member_id))
    if info_data == None: 
        await realtime_log.send("``--- Verification Failed ---``")
        await ctx.message.reply(f"Your Information not found!\nKindly Fill-up the form first. Check <#{00}>")
        return
    # print(info_data)
    student_id = info_data[0]
    student_name = info_data[1]
    discord_username = info_data[2].replace(" ","")
    student_courses = info_data[3]
    MessageAuthorUserName = str(ctx.message.author)
    MessageAuthorUserName = MessageAuthorUserName.replace(" ","")  
    print(f"ID:{student_id}\nName:{student_name}\nDiscord:{discord_username}\nCourses:{student_courses}\nMessage Author:{MessageAuthorUserName}")
    await realtime_log.send(f"Username in Sheets:``{discord_username}``\nMessage Author:``{MessageAuthorUserName}``\nCourses:{student_courses}")
    
    try:
        if info_data[0] == None or info_data[1] == None or info_data[2] == None or info_data[3] ==None: 
            await ctx.message.reply(f"Information mismatch!\nKindly check this information with the information you filled up.\n**Edit the form according to correct information**\nYour Info:\nYour Discord Username:{MessageAuthorUserName}\nUsername found in form: {discord_username}")
            print("HERE")
            return
        elif MessageAuthorUserName.lower() == discord_username.lower():
            await realtime_log.send("--- Verified Username ---")
            for courses in student_courses: 
                courses = str(courses)
                newrole = discord.utils.get(ctx.guild.roles, name=courses)
                await ctx.message.author.add_roles(newrole)
                print(f"Added Role: {newrole}")
                await realtime_log.send(f"Added Role: {newrole}")
            print("All Roles Added")
            user_nickname = student_id + "_" + student_name
            if len(user_nickname) > 31: 
                await realtime_log.send("Need to short Member Nickname")
                print("Special Case")
                first_name = student_name.split()[0]
                user_nickname = student_id + "_" + first_name
            await ctx.author.edit(nick=user_nickname)
            print("Nickname Changed:", user_nickname)
            await realtime_log.send("Nickname Changed!")
            embed = await create_embed(student_id=student_id,student_name=student_name,discord_username=discord_username)
            print("Embed Sent")
            await ctx.send(embed=embed)
            await realtime_log.send("Embed Sent!\n``----- Verification Complete -----``")
            return
        else:
            await ctx.message.reply(f"**Information mismatch!**\nKindly check this information with the information you filled up.Edit the form according to correct information.\n**Your Info:**\n**Your Discord Username:**``{MessageAuthorUserName}``\n**Username in form:** ``{discord_username}``")
            print("Information not found with debug info sent")
            await realtime_log.send("User information mismatch\n``---- Verification Failed ----``")
            return
    except: 
        await ctx.message.reply(f"``Something went wrong! Kindly move to:`` <#{0000}>")
print("Initating BOT")
bot.run(BOT_TOKEN)
