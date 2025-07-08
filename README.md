A multi-purpose Discord bot that combines **real-time weather updates** with **fun social interaction**. Originally built as a lightweight weather bot, it’s now been upgraded with a **modular architecture**, **persistent database syncing**, and **clean error handling**, making it far more scalable and robust.

## Features

-  **Weather Command**  
  Fetches live weather data for any city using an API and gives a quick recommendation on whether it’s a good day to go outside.

-  **Target System**  
  Allows users to set a “target” in their server. When the target sends a message, the bot responds with randomized “friendly bullying” lines. Includes cooldowns to prevent spam and keep it light-hearted.

-  **PostgreSQL Integration**   
  The bot now syncs with a PostgreSQL database using `asyncpg`, saving:
  - All joined servers (guilds)
  - Users and their usernames
  - User-server relationships
  - Command activity (in future versions)

- **Modular Cog System**  
  Code is now organized using `discord.py` cogs:
  - `weather.py`: API requests & weather logic
  - `target.py`: Target/bully logic
  - `database.py`: Database setup and future management commands

- **Custom Bot Class & Setup Hook**  
  Introduced a `CustomBot` subclass for better encapsulation. Initial extensions are auto-loaded, and commands are synced only to a test server or globally, depending on config.

-  **Improved Error Handling** 
  Gracefully handles:
  - Unknown commands
  - Missing arguments
  - Unexpected errors (with logs)

- **Secure Environment Config**  
  Tokens and database credentials are stored using `.env` files for safety and easy deployment.

- **Rotating Log Files**  
  Added structured logging with rotating file handlers to keep logs clean and manageable over time.

## What I Learned

- Managing async workflows with real-world APIs and DB access
- Clean separation of logic using cogs and custom classes
- How to safely and efficiently interact with a PostgreSQL database using connection pooling
- Writing Discord bots with proper error messaging and graceful fallbacks

## Tech Stack

- Python 3
- [discord.py](https://discordpy.readthedocs.io/)
- [asyncpg](https://magicstack.github.io/asyncpg/)
- [aiohttp](https://docs.aiohttp.org/)
- PostgreSQL
- dotenv
- Logging (with rotation)

## Future Features

-  Add Slash commands (for modern Discord UX)
-  Command usage analytics and leaderboard
-  User preferences for weather (metric/imperial)
-  Scheduled weather alerts
-  Opt-out system and custom messages in Target mode
-  Web dashboard for guild/server admins
