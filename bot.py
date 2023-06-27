import os
import datetime

import database
import controls

import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


class DiscordCommand:
    def __init__(self, *args, **kwargs):
        self.db = database.DatabaseHandler()
        self.db.start()
        self.is_for_dn = False
        if self.db.connection:
            self.db.create_table()

        self.controls = controls.Controls()

    def set_is_url_for_dn(self, is_for_dn):
        self.is_for_dn = is_for_dn

    async def setup_hook(self):
        if self.is_ready:
            await self.schedule_tasks.start()

    def check(self, guild):
        """
        Perform GET request to all URLs in the database and check if there's news or changes in the website.
        """
        if self.db.get_all_url():
            for url in self.db.get_all_url():
                id, username, link, target, html, encrypted, date_added = url
                response = self.controls.get(link)
                if response:
                    new_html = str(
                        self.controls.find_target(
                            response.text,
                            target="table",
                            _class="bbs_list",
                            multiple=False,
                        )
                    )

                    old_html = str(
                        self.controls.find_target(
                            html, target="table", _class="bbs_list", multiple=False
                        )
                    )

                    hashed = self.controls.convert(
                        bytes(new_html, encoding="utf-8")
                    ).hexdigest()

                    # Check if new hashed html if same with old hashed html.
                    # This will perform updating of url html content if new and old hashed is not the same.
                    if hashed != encrypted:
                        # Store all created links here
                        links = []

                        # Get text channels.
                        channels = guild.text_channels

                        new = self.controls.remove_whitespace(new_html)
                        old = self.controls.remove_whitespace(old_html)
                        comparison = self.controls.compare(new, old)

                        # Used to get the id of th post that will be used to build the url.
                        url_id = ""

                        for item in comparison:
                            # Check the changes returned by the compare method which is marked with "-" as starting of the string.
                            new_url_id = self.controls.find(item)

                            if new_url_id and new_url_id != url_id:
                                url_id = new_url_id.group(0)

                            if item.startswith("-"):
                                # This logic is tailored for DN website which has 4 sequence digit that act as an id for their news updates.
                                if guild and url_id:
                                    for channel in channels:
                                        created_url = self.controls.build_url(
                                            f"{link}/all", url_id
                                        )

                                        if created_url not in links:
                                            links.append(created_url)

                        # Update the current HTML & encrypted(hash) record in the database with the newest updates.

                        record = {
                            "username": "jiseoh",
                            "url": link,
                            "html": new_html,
                            "encrypted": hashed,
                        }

                        self.db.update_record(record)

                        return links

                    else:
                        print(f"{datetime.datetime.now()} Same hash.")
                        return None
        else:
            # Initialize database first row that can be checked once schedule ran.
            record = {
                "username": "jiseoh",
                "url": "https://sea.dragonnest.com/news/notice",
                "html": "",
                "target": "",
                "encrypted": "",
            }
            self.db.insert_to_webpage(record)
            print(f"{datetime.datetime.now()} Initialized first row.")

    async def send_update(self, channels, urls, context=False):
        """
        Sends the created URLs in the discord guild.
        """
        if urls and not context:
            for url in urls:
                for channel in channels:
                    if channel.name == "dn-news":
                        print(f"url and no context {url}")

                        # await channel.send(f"Update\n{url}")

        elif urls and context:
            for url in urls:
                for url in urls:
                    print(f"url and context {url}")
                    # await channel.send(f"Update\n{url}")

        elif not urls and context:
            print(f"No updates")
            # await channels.send("No new updates yet.")

    @tasks.loop(minutes=15.0)
    async def schedule_tasks(self, guild):
        guild = guild[0]
        channels = guild.text_channels

        urls = self.check(guild)

        await self.send_update(channels, urls)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    client = commands.Bot(command_prefix="$", intents=intents)
    mybot = DiscordCommand()

    @client.event
    async def on_ready():
        mybot.set_is_url_for_dn(True)
        await mybot.schedule_tasks.start(client.guilds)

    @client.command(name="check")
    async def check(context):
        if (
            context.channel.name in ("spam-command", "dn-news")
            and context.author != context.me
        ):
            guild = client.guilds
            channels = context.channel
            urls = mybot.check(guild)
            await mybot.send_update(channels, urls, context=True)

    client.run(os.getenv("TOKEN"))
