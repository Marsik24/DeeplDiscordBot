import discord
from discord.ext import commands
from discord import app_commands, ui
from translation import translation, get_source_language, get_target_language, get_flag
import datetime

# Global dictionary for source languages
SOURCE_DICT = get_source_language()
# Global dictionary for target languages
TARGET_DICT = get_target_language()
# Global dictionary for translations via reactions
EMOJI_TO_LANGUAGE = get_flag()


# This class defines a UI with a single button to send the translation in DM to the user who requested it
class SendPrivateButton(ui.View):
    def __init__(self, original_text: str, text_to_send: str, author: str):
        # Initialize the view, setting a timeout of 3 minutes
        super().__init__(timeout=180)
        # The original text that was translated
        self.original_text = original_text
        # The translated text to be sent
        self.text_to_send = text_to_send
        # The user object that requested the translation
        self.author = author
        # Adds a button labeled “Send to DM”
        self.add_item(discord.ui.Button(label="Send to DM", style=discord.ButtonStyle.primary))
        # Assigns the `send_private_message` callback to the added button
        self.children[0].callback = self.send_private_message
        # Reference to the message in which the view was sent, used to disable buttons at timeout
        self.message = None

    # Method called when view reaches timeout
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    # Callback method for the “Send to DM” button
    async def send_private_message(self, interaction: discord.Interaction):
        # Checks whether the interaction is from the user who requested the translation
        if interaction.user == self.author:
            try:
                # Create an embed with the title, color and description
                embed = discord.Embed(
                    title="Your Translation",
                    color=discord.Color.blue(),
                    description=f"Here's the translated text you requested:"
                )
                # Adds fields for original text and translated text
                embed.add_field(name="Original Text", value=self.original_text, inline=False)
                embed.add_field(name="Translated", value=self.text_to_send, inline=False)
                # Set the footer and timestamp of the embed.
                embed.set_footer(text="Powered by Marsik24 \nSome languages may not be supported.")
                embed.timestamp = datetime.datetime.now()
                # Attempt to send embed in DM to author
                await self.author.send(embed=embed)
            # Responds to interaction (on channel) informing that DM has been sent|
            except discord.errors.Forbidden:
                await interaction.response.send_message(
                    "I couldn't send you a DM. Please make sure your DMs are open.", ephemeral=True)
                # Handles the error if the bot fails to send a DM
            except Exception as e:
                await interaction.response.send_message(f"An error occurred while sending the DM: {e}", ephemeral=True)
        else:
            # If a different user tries to click the button
            await interaction.response.send_message(
                "This button is only for the user who requested the translation.", ephemeral=True)


# This class creates a view with a drop-down menu for language selection supporting pagination
class PagedLanguageView(ui.View):
    def __init__(self, language_codes, language_names, is_from=True):
        # 1 minute timeout for language selection
        super().__init__(timeout=60)
        # List of language codes
        self.language_codes = language_codes
        # List of language names
        self.language_names = language_names
        # Number of options per page in the drop-down menu
        self.page_size = 25
        # Current page displayed
        self.current_page = 0
        # True if selecting the source language, False for the target language
        self.is_from = is_from
        # The language code selected by the user
        self.selected_language_code = None
        # Update the UI components of the view based on the current page
        self._update_view()
        # Reference to the original interaction to update the message
        self.interaction = None

    # Internal method to obtain the select menu options for the current page
    def _get_current_page_options(self):
        start = self.current_page * self.page_size
        end = min((self.current_page + 1) * self.page_size, len(self.language_codes))
        options = []
        # Builds the options for the select menu
        for i in range(start, end):
            if i < len(self.language_codes) and i < len(self.language_names):
                options.append(discord.SelectOption(label=self.language_names[i], value=self.language_codes[i]))
        return options

    # Internal method for updating the drop-down menus and buttons of the view
    def _update_view(self):
        # Removes all existing components
        self.clear_items()
        # Get options for the current page
        options = self._get_current_page_options()

        if options:
            # Create the select menu with the options on the current page
            select_menu = ui.Select(
                placeholder=f"Select {'source' if self.is_from else 'target'} language "
                            f"(Pages {self.current_page + 1})",
                options=options
            )

            # Defines the callback for selection in the menu
            async def select_callback(interaction: discord.Interaction):
                # Set the selected language code
                self.selected_language_code = select_menu.values[0]
                # Stop the view, indicating that the selection is complete
                self.stop()
                # Deferred response to avoid timeout errors
                await interaction.response.defer()
            select_menu.callback = select_callback
            # Adds the select menu to the view
            self.add_item(select_menu)

        # Adds the “Prev Page” button if we are not on the first page
        if self.current_page > 0:
            prev_button = ui.Button(label="Prev Page", style=discord.ButtonStyle.primary)

            # Defines the callback for the “Prev Page” button
            async def prev_callback(interaction: discord.Interaction):
                # Decrement the current page
                self.current_page -= 1
                # Update the view with the new page
                self._update_view()
                # Deferred response
                await interaction.response.defer()
                # Modify the original message to show the new page
                await interaction.edit_original_response(view=self)

            prev_button.callback = prev_callback
            self.add_item(prev_button)

        # Adds the “Next Page” button if there are other pages available
        if (self.current_page + 1) * self.page_size < len(self.language_codes):
            next_button = ui.Button(label="Next Page", style=discord.ButtonStyle.primary)

            # Defines the callback for the “Next Page” button
            async def next_callback(interaction: discord.Interaction):
                # Increment the current page
                self.current_page += 1
                # Update the view with the new page
                self._update_view()
                # Deferred response
                await interaction.response.defer()
                # Modify the original message to show the new page
                await interaction.edit_original_response(view=self)

            next_button.callback = next_callback
            self.add_item(next_button)

    # Method to display the view to the user and wait for a selection
    async def prompt(self, interaction: discord.Interaction):
        self.interaction = interaction
        # Modify the original reply message to display the view
        await interaction.edit_original_response(view=self)
        # Waits for the view to be stopped by selection or timeout
        await self.wait()
        # Returns the selected language code
        return self.selected_language_code


# This class is a Discord.py Cog, which groups commands, listeners, and translation logic
class TranslatorCommand(commands.Cog):
    def __init__(self, bot):
        # Reference to the bot instance
        self.bot = bot
        # Prepare lists of names and codes of languages for paginated views
        self.source_name_list = [k for k in SOURCE_DICT.keys()]
        self.source_code_list = [k for k in SOURCE_DICT.values()]
        self.target_name_list = [k for k in TARGET_DICT.keys()]
        self.target_code_list = [k for k in TARGET_DICT.values()]

    # Async method to perform translation and send the result
    async def perform_translation_and_send(self, interaction: discord.Interaction = None,
                                           message: discord.Message = None, text_to_translate: str = None,
                                           source_lang_code: str = None, target_lang_code: str = None,
                                           reactor: discord.User = None, author: str = None):
        try:
            # Performs translation using the imported function
            text_translated, source_lang_code = translation(text_to_translate, source=source_lang_code,
                                                            target=target_lang_code)
            source_language_name = [name for name, code in SOURCE_DICT.items() if code == source_lang_code][0]
            target_language_name = [name for name, code in TARGET_DICT.items() if code == target_lang_code.upper()][0]
            # Create an embed to show the translation result
            embed = discord.Embed(
                title="Your Translation",
                color=discord.Color.blue(),
                # Use the author's mention to make the message clearer
                description=f"Here are the translation requested by <@{author}>:"
            )
            embed.add_field(name=f"Original Text in {source_language_name}", value=text_to_translate, inline=False)
            embed.add_field(name=f"Translated to {target_language_name}",
                            value=text_translated if text_translated else "Error", inline=False)
            # Set the footer and timestamp of the embed
            embed.set_footer(text="Powered by Marsik24 \nSome languages may not be supported.",
                             icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.timestamp = datetime.datetime.now()

            # Create a view with the “Send to DM” button, Pass the original text of the message
            view = SendPrivateButton(original_text=message, text_to_send=text_translated, author=author)
            # Decide where to send the embed message based on whether the interaction is a slash command or a reaction
            if interaction:
                view.message = await interaction.followup.send(embed=embed, view=view)
            elif message:
                # This branch is activated for reactions
                await message.channel.send(embed=embed, view=view)

        except Exception as e:
            print(f"Error during translation: {e}")
            # Send an error message to the appropriate channel
            if interaction:
                await interaction.followup.send(f"An error occurred during translation: {e}", ephemeral=True)
            elif message:
                await message.channel.send(f"An error occurred during translation: {e}")

    # This method is called every time a reaction is added to a message.
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # Ignore reactions added by the bot itself
        if user.bot:
            return

        # Check if the reaction emoji is mapped to a language
        if reaction.emoji in EMOJI_TO_LANGUAGE:
            target_language_code = EMOJI_TO_LANGUAGE[reaction.emoji]
            # The message to which the reaction was added
            message = reaction.message

            # Removes user reaction for cleaning or to prevent re-triggering
            await reaction.remove(user)

            # Translates based on the message content and the language of the reaction
            await self.perform_translation_and_send(
                message=message,
                text_to_translate=message.content,
                target_lang_code=target_language_code,
                reactor=user,
                author=str(user.id)
            )

    # Allows the user to specify both the source and target languages
    @app_commands.command(name="translate_from_to", description="translate from a source language to a target language")
    async def translate_command(self, interaction: discord.Interaction, message: str):
        # Set the interaction to “loading” (ephemeral = visible only to the user)
        await interaction.response.defer(ephemeral=True)

        # Requires the user to select the source language via a paginated view
        source_lang_view = PagedLanguageView(self.source_code_list, self.source_name_list, is_from=True)
        source_lang_code = await source_lang_view.prompt(interaction)

        if source_lang_code is None:
            await interaction.followup.send("Starting language selection cancelled or expired.", ephemeral=True)
            return

        # Requires the user to select the target language via a paginated view
        target_lang_view = PagedLanguageView(self.target_code_list, self.target_name_list, is_from=False)
        # Update the original message with the new view for selecting the target language
        await interaction.edit_original_response(view=target_lang_view)
        target_lang_code = await target_lang_view.prompt(interaction)

        if target_lang_code is None:
            await interaction.followup.send("Destination language selection cancelled or expired.",
                                            ephemeral=True)
            return

        # Translates using the selected languages
        await self.perform_translation_and_send(
            interaction=interaction,
            message=message,
            text_to_translate=message,
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
            author=interaction.user
            )

    # Allows the user to specify only the target language, the source language is automatically detected
    @app_commands.command(name="translate_to",
                          description="autodetect the source language and translate to a target language")
    async def translate_to(self, interaction: discord.Interaction, message: str):
        # Set the interaction to “loading” (ephemeral = visible only to the user)
        await interaction.response.defer(ephemeral=True)
        # Requires the user to select the target language
        target_lang_view = PagedLanguageView(self.target_code_list, self.target_name_list, is_from=False)
        await interaction.edit_original_response(view=target_lang_view)
        target_lang_code = await target_lang_view.prompt(interaction)

        if target_lang_code is None:
            await interaction.followup.send("Destination language selection cancelled or expired.",
                                            ephemeral=True)
            return

        # Performs the translation, DeepL will automatically detect the source language
        await self.perform_translation_and_send(
            interaction=interaction,
            message=message,
            text_to_translate=message,
            target_lang_code=target_lang_code,
            author=interaction.user
        )


# Function required by discord.py to load a Cog
async def setup(bot):
    await bot.add_cog(TranslatorCommand(bot))
    bot.tree.add_command(translate_message_context)


# This command appears when a user right-clicks on a message
@app_commands.context_menu(name="Translate Message")
async def translate_message_context(interaction: discord.Interaction, message: discord.Message):
    # Obtains the Cog TranslatorCommand instance from the bot
    translator_cog = interaction.client.get_cog("TranslatorCommand")
    if translator_cog:
        await interaction.response.defer(ephemeral=True)

        source_name_list = [k for k in SOURCE_DICT.keys()]
        source_code_list = [k for k in SOURCE_DICT.values()]
        target_name_list = [k for k in TARGET_DICT.keys()]
        target_code_list = [k for k in TARGET_DICT.values()]

        # Requires the user to select the source language
        source_lang_view = PagedLanguageView(source_code_list, source_name_list, is_from=True)
        source_lang_code = await source_lang_view.prompt(interaction)

        if source_lang_code is None:
            await interaction.followup.send("Starting language selection cancelled or expired.", ephemeral=True)
            return

        # Requires the user to select the target language
        target_lang_view = PagedLanguageView(target_code_list, target_name_list, is_from=False)
        await interaction.edit_original_response(view=target_lang_view)
        target_lang_code = await target_lang_view.prompt(interaction)

        if target_lang_code is None:
            await interaction.followup.send("Destination language selection cancelled or expired.",
                                            ephemeral=True)
            return

        # Performs translation using the Cog TranslatorCommand method
        await translator_cog.perform_translation_and_send(
            interaction=interaction,
            message=message,
            text_to_translate=message.content,
            source_lang_code=source_lang_code,
            target_lang_code=target_lang_code,
            author=interaction.user
        )
    else:
        # If the Cog is not available (unlikely if setup() is called correctly)
        await interaction.response.send_message("Translator command is not available.", ephemeral=True)
