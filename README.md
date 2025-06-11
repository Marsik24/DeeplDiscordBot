# Translator Discord BOT Deepl

This Discord bot performs translations using the [Deepl API](https://www.deepl.com/en/products/api).
You can translate using slash commands, context menu commands, and flag reactions to messages.

The translation can be done by automatically detecting the source language or by selecting it.

The translation carried out using the reaction with the flags of the nations is available for 97 nations.

Thanks to Deepl APIs, 35 different languages are currently available, and if new languages are added, they will be implemented automatically.

## Slash commands

- translate_from_to: with this command, you can perform the translation by selecting the source language and the target language.

  ![translate_1](https://github.com/user-attachments/assets/941bfd95-6653-4113-a068-58e81525fc06)
  
  Once you have entered the message to be translated, the bot will send a drop-down menu to select the source language.

  ![menu](https://github.com/user-attachments/assets/83e73c0d-c3d9-4e7b-a7ed-255e50281948)

  After you have chosen the source language, it will modify the message, allowing you to choose the target language.

  ![menu_2](https://github.com/user-attachments/assets/c9a19d29-0440-4a8d-a83e-85526468a317)

  Finally, you will get an embed with the message containing all the information related to the translation.

  ![embed](https://github.com/user-attachments/assets/3461e377-8a84-4613-8a20-1acbd59b04a7)
  
- translate_to: with this command, you can translate by selecting only the target language, the source language will be detected automatically.

  ![translate_to](https://github.com/user-attachments/assets/30abf54e-352f-46f0-875a-800d179ad8f6)

  Once you have entered the message to be translated, the bot will send a drop-down menu to select the target language.

  ![menu_2](https://github.com/user-attachments/assets/b38ba97b-d67f-4f4c-bd38-506d07e4f5a3)

  Finally, you will get an embed with the message containing all the information related to the translation.

  ![image](https://github.com/user-attachments/assets/49cf6331-3d0e-4e8f-86e3-df4da1753932)


  ## Context menu commands

  - Translate Message: with this command, you can translate a message sent by a user by selecting the source language and target language.
  
  ![image](https://github.com/user-attachments/assets/04b5d27b-1486-4d38-a90b-a88575874520)

  Once you have selected the message, the bot will send a message with a drop-down menu allowing you to choose the source language.

  ![image](https://github.com/user-attachments/assets/cd852429-7aa5-4791-bd03-33388d3a63b6)

  You will then be shown the menu to choose the target language.
  
  ![image](https://github.com/user-attachments/assets/11ebb9d9-09b7-4277-8da0-aa4fc43e0e46)

   To receive the embed with the translation details via message.
  
  ![image](https://github.com/user-attachments/assets/e9d4db42-d821-4cc2-a33b-af876c5c9d36)

  
  ## Flag reactions to messages

   -By reacting to a message with a flag emote, you will get the translation in the main language of that country.

  ![image](https://github.com/user-attachments/assets/a70d8a48-6abd-42c2-abf5-8bdcf4b2c084)

  ## Sent to DM button

  -This button will send the translation you just made via DM.

  ![image](https://github.com/user-attachments/assets/05970b49-9d62-4a65-876d-bdc107997414)

