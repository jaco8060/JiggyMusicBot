# bot/views/pagination_view.py

import discord
from discord.ui import View, Button
import math

class QueuePaginationView(View):
    def __init__(self, queue, interaction, per_page=10):
        super().__init__(timeout=120)
        self.queue = queue
        self.interaction = interaction
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = math.ceil(len(self.queue) / self.per_page)
        self.message = None

        # Disable buttons if only one page
        if self.total_pages <= 1:
            self.stop()

        # Initialize buttons
        self.previous_button = Button(label="Previous", style=discord.ButtonStyle.primary)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        # Add buttons to the view
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        # Update button states
        self.update_buttons()

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    async def send_initial_message(self):
        content = self.get_page_content()
        self.message = await self.interaction.followup.send(content, view=self)

    def get_page_content(self):
        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        page_queue = self.queue[start_idx:end_idx]
        queue_list = "\n".join(
            [f"{idx + 1}. {song['title']}" for idx, song in enumerate(page_queue, start=start_idx)]
        )
        content = f"Current song queue (Page {self.current_page + 1}/{self.total_pages}):\n\n{queue_list}"
        return content

    async def update_message(self):
        content = self.get_page_content()
        await self.message.edit(content=content, view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        self.update_buttons()
        await self.update_message()
        await interaction.response.defer()

    async def previous_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.update_buttons()
        await self.update_message()
        await interaction.response.defer()

    async def on_timeout(self):
        # Disable all components when view times out
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)
