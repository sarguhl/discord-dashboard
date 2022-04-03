from quart import redirect, url_for
from quart import Quart, render_template, request, session
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc


app = Quart(__name__)
ipc_client = ipc.Client(secret_key = "test1234")

app.config["SECRET_KEY"] = "test1233"
app.config["DISCORD_CLIENT_ID"] = 960085723896229918
app.config["DISCORD_CLIENT_SECRET"] = "56fK0xKLatDi4laWZzSic44BO8CfktZn"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

discord = DiscordOAuth2Session(app)


@app.route("/")
async def home():
	return await render_template("index.html", authorized = await discord.authorized)

@app.route("/login")
async def login():
	return await discord.create_session()

@app.route("/callback")
async def callback():
	try:
		await discord.callback()
	except:
		return redirect(url_for("login"))

	user = await discord.fetch_user()
	return redirect(url_for("dashboard")) #You should return redirect(url_for("dashboard")) here

@app.route("/dashboard")
async def dashboard():
	if not await discord.authorized:
		return redirect(url_for("login")) 

	guild_count = await ipc_client.request("get_guild_count")
	guild_ids = await ipc_client.request("get_guild_ids")
	bot_name = await ipc_client.request("get_bot")

	user_guilds = await discord.fetch_guilds()

	guilds = []

	for guild in user_guilds:

		if guild.permissions.administrator:			
			guild.class_color = "yes_card" if guild.id in guild_ids else "card"
			guilds.append(guild)

	guilds.sort(key = lambda x: x.class_color == "red-border")
	name = (await discord.fetch_user()).name
	return await render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name, bot_name = bot_name, guild_ids = guild_ids, user_guilds = user_guilds,)

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
	if not await discord.authorized:
		return redirect(url_for("login")) 

	fake_data = [
		("15-03-2022", 216),
		("16-03-2022", 224),
		("17-03-2022", 230),
		("18-03-2022", 239),
		("19-03-2022", 245),
		("20-03-2022", 256),
		("21-03-2022", 268),
		("22-03-2022", 286),
		("23-03-2022", 314),
		("24-03-2022", 363),
		("25-03-2022", 401),
		("26-03-2022", 430),
		("27-03-2022", 410),
		("28-03-2022", 424),
		("29-03-2022", 440),
		("30-03-2022", 455),
		("31-03-2022", 462),
		("01-04-2022", 489),
		("02-04-2022", 512),
		("03-04-2022", 532),
	]

	labels = [row[0] for row in fake_data]
	values = [row[1] for row in fake_data]

	guild = await ipc_client.request("get_guild", guild_id = guild_id)
	if guild is None:
		return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
	return await render_template("guild_view.html", guild_name = guild["name"], guild_members = guild["members"], guild_roles = guild["roles"], guild_created = guild["created"], guild_prefix = guild["prefix"],labels=labels, values=values)

if __name__ == "__main__":
	app.run(debug=True)