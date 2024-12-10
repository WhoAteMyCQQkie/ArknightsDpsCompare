# Discord Bot for Comparing Operators' DPS

This repository contains a Discord bot that creates graphs comparing different operators' DPS depending on enemy defense and resistance.  
It is currently active on the Discord server of **DragonGJY** ([YouTube Channel](https://www.youtube.com/@DragonGJY)) in the **operation-room** channel.

---

## 1. How to Use

To use the bot, follow these steps:

1. The bot requires a `token.txt` file containing the Discord bot token. This file should be in the same directory as the `discoBot.py` file.
2. Modify the `valid_channels` variable (located just below the imports in `discoBot.py`) to specify the channels where the bot will respond.
3. You can then type `!help` in those channels to get a quick explanation on how to use the bot.

---

## 2. Disclaimer

The bot was originally not designed to be as complex as it is now, resulting in some spaghetti-ish code. Viewer discretion is advised.

- The bot only calculates DPS based on damage per hit and attack interval. 
- It does **not** account for animation frames and sp lockout is always assumed to be 1.2 seconds (example: Horn S1).
- For example, Exusiai's S3 multiplies the damage by 5, even though each shot takes some time.
- The total damage is calculated by multiplying DPS by the skill duration, regardless of whether the duration aligns with the attack interval or not. Therefore, you may get the damage of something like 17.42 attacks.

**TL;DR**: The numbers are not 100% accurate, and users should use them with some discretion. The bot is best used for comparing operators against themselves (considering skill masteries, module levels, etc.).

---

## 3. How to Contribute

The easiest way to contribute is by adding to the `damageformulas.py` or `healingformulas.py` files.  
Here's how to do it:

1. Copy the code of existing operators or the blueprint class.
2. Modify the copied class to fit the new operator. For the contents (including the order) of the talent and skill parameters you can check [Aceship](https://aceship.github.io/AN-EN-Tags/akhrchars.html).
3. Add the new operator to the dictionary and list at the end of the file.

---

## 4. Miscellaneous

- If you want the `!stage` command (and the enemy/stage prompt for the DPS calculation) to work, you will need to pull the submodule from [Kengxxiao](https://github.com/Kengxxiao) which contains the game data.

---

## 5. How to Maintain

Currently, the bot is still being worked on, so just pull updates occasionally. However, it's possible that development may cease at some point in the future, so here is a guide on how to maintain it:

1. Whenever the game updates, the repository of Kengxxiao will (hopefully) be updated.  
   You can update the submodule to get the latest game data.
   
2. To make this data accessible to the bot, you need to update `database/JsonReader.py`. Add the newly added operators to the large dictionary at the start of the file.

3. The `fileHelper()` method can help you read out missing IDs, but you can also find them listed on [arknights.wiki.gg](https://arknights.wiki.gg).

4. After updating the data, run the file to create a new `.pkl` file with the operator data.

5. From here, follow the steps in the "How to Contribute" section.

---

### Feel free to contribute!
