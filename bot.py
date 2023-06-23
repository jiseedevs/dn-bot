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

    @tasks.loop(minutes=30.0)
    async def schedule_tasks(self, guild):

        if self.db.get_all_url():

            for url in self.db.get_all_url():
                id, username, link, target, html, encrypted, date_added = url
                response = self.controls.get(link)
                if response:

                    new_html = str(self.controls.find_target(response.text, 'table', _class='bbs_list', multiple=False))

                    old_html = str(self.controls.find_target(html, 'table', _class='bbs_list', multiple=False))

                    hashed = self.controls.convert(bytes(new_html, encoding='utf-8')).hexdigest()

                    if hashed != encrypted:

                        # Store all created links here
                        links = []

                        # Get text channels.
                        channels = guild[0].text_channels


                        new = self.controls.remove_whitespace(new_html)
                        old = self.controls.remove_whitespace(old_html)
                        comparison = self.controls.compare(new, old)

                        for item in comparison:
                            # Check the changes returned by the compare method which is marked with "-" as starting of the string.

                            if item.startswith('-'):
                                # Used to get the id of th post that will be used to build the url.
                                match = self.controls.find(item)

                                # This logic is tailored for DN website which has 4 sequence digit that act as an id for their news updates.
                                if match and len(match.group(0)) >= 4 and guild:

                                    url_id = match.group(0)

                                    for channel in channels:

                                        if channel.name == 'dn-news' and self.is_for_dn:
                                            created_url = self.controls.build_url(f"{link}/all", url_id)

                                            if created_url not in links:
                                                links.append(created_url)

                                            for url in links:

                                                await channel.send(
                                                    f'Update!\n{url}'
                                                )

                            # Update the current HTML & encrypted(hash) record in the database with the newest updates.

                            record = {
                                'username': 'jiseoh',
                                'url': link,
                                'html': new_html,
                                'encrypted': hashed,
                            }

                            self.db.update_record(record)

                    else:
                        print(f'{datetime.datetime.now()} Same hash.')
        else:

            record = {
                        'username': 'jiseoh',
                        'url': 'https://sea.dragonnest.com/news/notice',
                        'html': '',
                        'target': '',
                        'encrypted': '',
                    }
            self.db.insert_to_webpage(record)

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    mybot = DiscordCommand()

    @client.event
    async def on_ready():
        mybot.set_is_url_for_dn(True)
        await mybot.schedule_tasks.start(client.guilds)

    client.run(os.getenv('TOKEN'))
