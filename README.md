━━━━━━━━━━━━━━━━━━━━

<h2 align="center">
ᴜʟᴛɪᴍᴀᴛᴇ ꜰɪʟᴇ ꜱᴛᴏʀᴇ
</h2>

<p align="center">
  <img src="https://files.catbox.moe/5o6qbm.jpg">
</p>


![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=ULTIMATE+FILESTORE+BOT!;CREATED+BY+REALM+BOTS!;A+ADVANCE+BOT+WITH+COOL+FEATURE!)
</p>

 ━━━━━━━━━━━━━━━━━



<details><summary><b>📌 ғᴇᴀᴛᴜʀᴇs:</b></summary>

<b>🚀 Core Features:</b>

• <b>Multi-Bot Deployment:</b> Run multiple bots simultaneously from a single `setup.json` — each with its own token, DB, and configuration  
• <b>Batch & Custom Batch Links:</b> Create links for one or multiple posts using <code>/batch</code>, <code>/genlink</code>, and <code>/autobatch</code>  
• <b>Auto Batch with Quality Grouping:</b> Automatically detects and groups files by quality (4K, 1080p, 720p, 480p, HDRip, BluRay, WEB-DL, HEVC) and generates separate links  
• <b>Custom Autobatch Template:</b> Fully customizable output format using placeholders like <code>{1080p}</code>, <code>{720plink}</code>, <code>{totalfilecount}</code> etc.  
• <b>Migrator Bot Integration:</b> A separate redirect bot that routes users to the correct file bot, preventing link breakage when switching bots  
• <b>Broadcast Tools:</b> Send messages to all users via <code>/broadcast</code>, <code>/pbroadcast</code> (pinned), or <code>/dbroadcast</code> (auto-delete after a timer)  
• <b>Auto File Deletion:</b> Files sent to users auto-delete after a configurable timer to handle copyright concerns  
• <b>User Management:</b> Ban/unban users and view user count via <code>/ban</code>, <code>/unban</code>, <code>/users</code>  
• <b>Multi Force Subscription:</b> Add unlimited FSub channels supporting both request-to-join and public invite links, each with a configurable expiry timer  
• <b>Admin Control:</b> Add or remove multiple admins directly from the Settings Menu  
• <b>Bot Analytics:</b> Get total user count with <code>/users</code> and full system stats with <code>/usage</code>  
• <b>Deployment Ready:</b> Deploy on <b>Heroku</b>, <b>Koyeb</b>, <b>Railway</b>, <b>Render</b>, or a <b>VPS</b> in minutes  

<b>🗄️ Database Features:</b>

• <b>Primary & Secondary DB Channels:</b> Manage multiple database channels for file storage  
• <b>Backup Database:</b> Automatically backs up uploaded files to a separate channel for redundancy  
• <b>Smart Fallback Fetching:</b> If a file is missing from the primary DB, the bot automatically fetches it from the backup channel  

<b>🔗 Shortener & Credit System:</b>

• <b>URL Shortener Integration:</b> Any shortener supporting the standard API (e.g., `arolinks.com`) can be configured  
• <b>Credit System:</b> Users earn credits by completing shortener links and spend them to access files — fully configurable earn amount, cost per file, and max limit  
• <b>Tutorial Link:</b> Configurable tutorial link shown to users on the shortener page  
• <b>Premium Users:</b> Grant premium access (bypasses shortener/credits) with permanent or timed expiry using <code>/addpremium</code>  

<b>✅ Auto Approval System:</b>

• <b>Auto-Approve Join Requests:</b> Automatically approve pending join requests for configured channels  
• <b>Per-Channel Control:</b> Enable or disable auto-approval on a per-channel basis  
• <b>Configurable Delay:</b> Set a delay (in seconds) before approving requests  
• <b>Bulk Approval:</b> Manually approve all pending requests for a channel using <code>/approveall</code>  
• <b>Welcome Message on Approval:</b> Send a custom photo + text + buttons to users when their request is approved  

<b>📂 Gofile.io Integration:</b>

• <b>Background Upload:</b> When a user accesses a single file link, the bot silently uploads the file to Gofile.io in the background  
• <b>Multi-Token Support:</b> Rotate between multiple Gofile API tokens for load balancing  
• <b>Persistent Link Storage:</b> Gofile links are saved in the database so the same file is never uploaded twice  
• <b>Inline Button:</b> A "⚡️ Gofile Link" button is added to the file message for direct download  

<b>🔗 Link Sharing System:</b>

• <b>Invite Link Generator:</b> Generate temporary invite links (normal + request-to-join) for configured channels  
• <b>Auto-Expiry:</b> Links automatically expire after 5 minutes to protect against copyright strikes  
• <b>Bulk Link Generation:</b> Generate links for multiple channels at once using <code>/bulklink</code>  
• <b>Paginated Channel Management:</b> View, add, and remove link-sharing channels with pagination  

<b>🖼️ File Delivery Features:</b>

• <b>Protect Content:</b> Prevent users from forwarding files received from the bot  
• <b>Hide Caption:</b> Strip captions from files before sending to users  
• <b>Channel Button:</b> Add a custom inline button (with your text and URL) to every file sent  
• <b>Web Page Detection:</b> Correctly handles text links without treating them as media  

<b>⚙️ Fully Configurable Messages & UI:</b>

• <b>Custom Start, About, FSub, Reply, Help messages</b> — all editable from the Settings Menu  
• <b>Custom photos</b> for Start, About, FSub, Shortner, and Approval messages  
• <b>Settings split across 3 pages</b> for a clean, organized UI  
• <b>Live config reset</b> via <code>/reset</code> without wiping user or link data  

<b>✨ More features & enhancements coming soon...</b>
</details>


<details><summary><b> - ꜱᴇᴛᴜᴘ.ᴊꜱᴏɴ ᴠᴀʀɪᴀʙʟᴇꜱ :</b></summary>

## ᴠᴀʀɪᴀʙʟᴇꜱ

Each entry in `setup.json` configures one bot. You can add multiple entries to run a fleet.

| Variable | Required | Description |
|---|---|---|
| `session` | ✅ | Unique session name for this bot (e.g. `"bot_1"`) |
| `token` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `api_id` | ✅ | Your API ID from [my.telegram.org](https://my.telegram.org) |
| `api_hash` | ✅ | Your API Hash from [my.telegram.org](https://my.telegram.org) |
| `workers` | ✅ | Number of concurrent workers (recommended: `8`) |
| `db_uri` | ✅ | Your MongoDB connection URI |
| `db_name` | ✅ | Name of your MongoDB database |
| `databases` | ✅ | Object with `primary` (channel ID), `secondary` (list), `backup` (channel ID or null) |
| `fsubs` | ✅ | List of FSub entries: `[channel_id, request_enabled, timer_in_minutes]` |
| `auto_del` | ✅ | Auto-delete timer in seconds (`0` = disabled) |
| `admins` | ✅ | List of admin user IDs (in addition to OWNER_ID) |
| `disable_btn` | ✅ | `true` to hide the "Get File" button on DB channel posts |
| `protect` | ✅ | `true` to enable content protection on all sent files |
| `gofile_enabled` | ❌ | `true` to enable Gofile.io background uploads |
| `gofile_tokens` | ❌ | List of Gofile.io API tokens |
| `messages` | ❌ | Object containing all customizable text and photo URLs (see below) |

### messages Object

| Key | Description |
|---|---|
| `START` | Start message. Supports `{mention}`, `{first}`, `{last}`, `{username}`, `{id}` |
| `FSUB` | Force subscribe prompt text |
| `ABOUT` | About message. Supports `{owner_id}`, `{bot_username}`, user placeholders |
| `HELP` | Help message body text |
| `REPLY` | Message sent to non-admin users who send unsupported messages |
| `START_PHOTO` | URL or file ID for the start message photo |
| `FSUB_PHOTO` | URL or file ID for the FSub message photo |
| `ABOUT_PHOTO` | URL or file ID for the about message photo |
| `SHORTNER_PHOTO` | URL or file ID shown on the shortener page |
| `SHORTNER_MSG` | Caption shown on the shortener page |
| `PREMIUM_CONTACT` | Telegram link for premium purchases |
| `SUPPORT_GRP` | Telegram link to your support group |
| `OWNER_URL` | Telegram link to the owner |
| `NETWORK_URL` | Telegram link to your network/updates channel |
| `APPROVAL_PHOTO` | Photo sent to users when their join request is approved |
| `APPROVAL_WELCOME_TEXT` | Text for the approval welcome message. Supports `{mention}`, `{chat_title}` |
| `APPROVAL_BUTTONS` | List of button rows to attach to the approval welcome message |

</details>


<details><summary><b> - ᴄᴏɴꜰɪɢ.ᴘʏ ᴠᴀʀɪᴀʙʟᴇꜱ :</b></summary>

## config.py

Edit these values in `config.py` before running:

| Variable | Description |
|---|---|
| `OWNER_ID` | Your Telegram user ID — has full owner access |
| `PORT` | Web server port (default: `8091`) |
| `SHORT_URL` | Default shortener domain (e.g. `arolinks.com`) |
| `SHORT_API` | Default shortener API key |

</details>


## 𝐶𝑜𝑚𝑚𝑎𝑛𝑑𝑠

```
start       - Start the bot
batch       - Create a batch link for a range of messages
genlink     - Create a single file link
autobatch   - Auto-group files by quality and generate batch links
broadcast   - Broadcast a message to all users
pbroadcast  - Pin a broadcast message for all users
dbroadcast  - Broadcast with an auto-delete timer (e.g. /dbroadcast 3600)
users       - See the total user count
ban         - Ban one or more users
unban       - Unban one or more users
usage       - View system resource usage (disk, RAM, CPU)
reset       - Reset bot config settings (preserves users & links)
addpremium  - Grant premium access to a user (supports duration)
delpremium  - Remove premium access from a user
premiumusers- List all current premium users
addcredit   - Add credits to a user
delcredit   - Remove credits from a user
setcredit   - Set a user's credit balance
resetcredit - Reset a user's credits to zero
showcredit  - View all users with credits (paginated)
credit      - Check your own credit balance
getcredit   - Get a shortener link to earn credits
approveall  - Approve all pending join requests for a channel
addch       - Add a channel to the link sharing system
delch       - Remove a channel from the link sharing system
channels    - View all link sharing channels (paginated)
links       - Show normal + request links for all channels
reqlink     - Show request-to-join links with buttons
bulklink    - Generate links for multiple channels at once
linkhelp    - Help guide for the link sharing system
shortner    - Manage shortener settings (command access)
database    - Manage database channels (command access)
help        - Open the help message

*Everything else can be changed from the Settings Menu*
```

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

<details>
<summary><h3>
- <b> ᴅᴇᴘʟᴏʏᴍᴇɴᴛ ᴍᴇᴛʜᴏᴅs </b>
</h3></summary>

### ⚙️ Pre-Setup (Required for all methods)

Before deploying, you need:

1. **Telegram API credentials** — Get `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org)
2. **Bot Token** — Create a bot via [@BotFather](https://t.me/BotFather) and copy the token
3. **MongoDB URI** — Create a free cluster at [mongodb.com](https://www.mongodb.com), go to **Connect → Drivers** and copy the connection string
4. **Database Channel** — Create a private Telegram channel, add your bot as admin with **Post Messages** permission, and copy the channel ID (format: `-100xxxxxxxxxx`)
5. **Migrator Bot** — Set up the migrator bot (`migrator.py`) separately with its own token. Update the `BOT_FLEET` dict and `TOKEN` in `migrator.py` to point to your file bots
6. **Edit `config.py`** — Set your `OWNER_ID` and optionally your default shortener credentials
7. **Edit `setup.json`** — Fill in each bot's token, api_id, api_hash, db_uri, db_name, and primary database channel ID

---

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://heroku.com/deploy?">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy On Heroku">
</a></p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ᴋᴏʏᴇʙ 」─
</h3>
<p align="center"><a href="https://app.koyeb.com/deploy?">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy On Koyeb">
</a></p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʀᴀɪʟᴡᴀʏ 」─
</h3>
<p align="center"><a href="https://railway.app/deploy?">
     <img height="45px" src="https://railway.app/button.svg">
</a></p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʀᴇɴᴅᴇʀ 」─
</h3>
<p align="center"><a href="https://render.com/deploy?">
<img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a></p>

<h3 align="center">
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ᴠᴘs 」─
</h3>
<p>
<pre>
# Clone the repository
git clone https://github.com/TypeAbdullah/FileStoreBot
cd FileStoreBot

# Install dependencies
pip3 install -U -r requirements.txt

# Edit your config files
nano config.py        # Set OWNER_ID, SHORT_URL, SHORT_API
nano setup.json       # Set token, api_id, api_hash, db_uri, databases, etc.

# Start the main bot (also launches migrator automatically via start.sh)
bash start.sh

# Or start them separately:
python3 migrator.py &
python3 main.py
</pre>
</p>

</details>

<details><summary><b>❓ ꜰᴀǫ & ᴛʀᴏᴜʙʟᴇꜱʜᴏᴏᴛɪɴɢ</b></summary>

**Q: The bot sends files but deletes them immediately.**  
A: Check `auto_del` in `setup.json`. Set it to `0` to disable auto-deletion.

**Q: Force subscribe isn't working.**  
A: Make sure the bot is admin in the FSub channel with the **Invite Users via Link** permission. Use `yes` or `no` for the request flag, not `true`/`false`.

**Q: Gofile.io upload never completes.**  
A: Check that `gofile_enabled` is `true` and a valid token is set in `gofile_tokens`. The upload runs in the background and only triggers on single-file links containing a video or document.

**Q: The shortener button appears but the link doesn't work.**  
A: Test your shortener from Settings → Shortener → Test. Ensure the domain and API key are correct and that your shortener supports the standard API format.

**Q: I want to add a second bot to the fleet.**  
A: Add a new entry to `setup.json` with a unique `session` name, then add the new bot's username to the `BOT_FLEET` dict in `migrator.py`.

**Q: How do I reset all settings without losing users?**  
A: Use the `/reset` command as the owner. This only drops the `bot_settings` collection — all users, links, premium members, and backup mappings are preserved.

</details>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

<h3>「 ᴏᴛʜᴇʀ ʙʀᴀɴᴄʜᴇs 」
</h3>

- <b>[sʜᴏʀᴛɴᴇʀ](https://github.com/TypeAbdullah/FileStoreBot/tree/shortner)

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

<h3>「 ᴄʀᴇᴅɪᴛs 」
</h3>

- <b>[ʀᴇᴀʟᴍ ʙᴏᴛs](https://t.me/realm_bots)  ➻  [ᴜᴘᴅᴀᴛᴇs](https://t.me/realm_bots) </b>
- <b>[ɴᴀᴘᴀᴇxᴛʀᴀ](https://github.com/NaapaExtra)  ➻  [sᴏᴍᴇᴛʜɪɴɢ](https://t.me/realm_bots) </b>
 
<b>ᴀɴᴅ ᴀʟʟ [ᴛʜᴇ ᴄᴏɴᴛʀɪʙᴜᴛᴏʀs](https://telegram.me/realm_bots) ᴡʜᴏ ʜᴇʟᴩᴇᴅ ɪɴ ᴍᴀᴋɪɴɢ file store ʙᴏᴛ ᴜsᴇꜰᴜʟ & ᴩᴏᴡᴇʀꜰᴜʟ 🖤 </b>

## 📌  𝑵𝒐𝒕𝒆

ᴊᴜꜱᴛ ꜰᴏʀᴋ ᴛʜᴇ ʀᴇᴘᴏ ᴀɴᴅ ᴇᴅɪᴛ ᴀꜱ ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅꜱ.

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
