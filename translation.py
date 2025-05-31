import os
from dotenv import load_dotenv
import deepl
import json

# Load environment variables from the .env file
load_dotenv()

# Retrieve the DeepL API token from the environment variables
TOKEN = os.getenv("TOKEN_DEEPL")
# Initialize the DeepL translator object with the API token
translator = deepl.Translator(TOKEN)


# Function to obtain flags (emoji) from a JSON configuration file
def get_flag():
    try:
        # Attempts to open and read the file 'emoji_config.json',
        # 'encoding='utf-8' ensures correct handling of special characters
        with open('emoji_config.json', 'r', encoding='utf-8') as f:
            # Load the JSON content of the file into a variable 'flags'
            flags = json.load(f)
            return flags
    except FileNotFoundError:
        # Handles the error if the file 'emoji_config.json' is not found
        print("Error: emoji_config.json file not found.")
        # Returns an empty dictionary in case of error
        return {}
    except json.JSONDecodeError:
        # Handles the error if the JSON file is not formatted correctly
        print("Error: The emoji_config.json file contains invalid JSON.")
        # Returns an empty dictionary in case of error
        return {}


# Funzione per ottenere le informazioni sull'utilizzo dell'API DeepL.
def get_usage():
    # Retrieve the usage object from the DeepL translator.
    usage = translator.get_usage()
    # Check if any translation limits have been reached
    if usage.any_limit_reached:
        return 'Translation limit reached.'
    # If the character limit is valid
    if usage.character.valid:
        return f"Character usage: {usage.character.count} of {usage.character.limit}"
    # If the document limit is valid
    if usage.document.valid:
        return f"Document usage: {usage.document.count} of {usage.document.limit}"


# Function to obtain a dictionary of source languages supported by DeepL
def get_source_language():
    # Initialize an empty dictionary for source languages
    source_dict = {}
    # Iterate over all source languages available via the DeepL API
    for language in translator.get_source_languages():
        # Create a new key-value pair
        new_data = {language.name: language.code}
        # Add the new pair to the source language dictionary
        source_dict.update(new_data)

    # Returns the dictionary of source languages
    return source_dict


# Function to obtain a dictionary of target languages supported by DeepL
def get_target_language():
    # Initialize an empty dictionary for target languages
    target_dict = {}
    # Defines a list of language codes not to be included in the target dictionary
    skip_language = ["EN", "PT", "ZH"]
    # Itera on all target languages available via the DeepL API
    for language in translator.get_target_languages():
        # If the language code is in the skip list, ignore it
        if language.code in skip_language:
            pass
        else:
            # Otherwise, create a new key-value pair
            new_data = {language.name: language.code}
            # Adds the new pair to the target language dictionary
            target_dict.update(new_data)

    # Returns the dictionary of target languages
    return target_dict


# Main function to perform a translation
def translation(text_original, source="", target="EN-GB"):
    # Translates the text
    result = translator.translate_text(text_original, source_lang=source, target_lang=target)
    # Extracts the translated text from the result
    text = result.text
    # Extracts the source language detected by DeepL
    detected_source = result.detected_source_lang

    # Returns the translated text and the detected source language
    return text, detected_source

