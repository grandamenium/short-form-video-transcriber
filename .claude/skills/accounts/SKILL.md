---
name: accounts
description: Manage TikTok profiles to scrape. Switch accounts, add multiple profiles, or list saved profiles.
user_invocable: true
---

# Accounts - Manage TikTok Profiles

This command lets users manage which TikTok profiles they want to scrape from.

## Workflow

### Step 1: Show Options

Display:

---

**Manage TikTok Profiles**

What would you like to do?

1. **Switch profile** - Change to a different TikTok account
2. **Add profile** - Add another profile to your list
3. **List profiles** - See all saved profiles
4. **Remove profile** - Remove a profile from your list
5. **Process multiple** - Scrape from multiple profiles at once

---

### Step 2: Handle User Choice

#### Option 1: Switch Profile

Ask:
> What TikTok profile URL do you want to switch to?
>
> Example: `https://www.tiktok.com/@newusername`

Then:
1. Validate the URL format
2. Test that the profile exists (quick yt-dlp check)
3. Save to `accounts.json` as the active profile
4. Confirm the switch

#### Option 2: Add Profile

Ask:
> What TikTok profile URL do you want to add?
>
> Example: `https://www.tiktok.com/@anotherusername`

Then:
1. Validate the URL
2. Add to `accounts.json` profiles list
3. Confirm addition

#### Option 3: List Profiles

Read `accounts.json` and display:

```
Saved Profiles:
---------------
1. @agentic.james (active)
   https://www.tiktok.com/@agentic.james

2. @techcreator
   https://www.tiktok.com/@techcreator

3. @aiexplainer
   https://www.tiktok.com/@aiexplainer
```

#### Option 4: Remove Profile

Show list and ask which to remove.

#### Option 5: Process Multiple

Ask:
> Which profiles do you want to process? (comma-separated numbers or "all")

Then run `/bulk` for each selected profile sequentially.

---

## accounts.json Format

Store profile configuration in project root:

```json
{
  "active": "https://www.tiktok.com/@agentic.james",
  "profiles": [
    {
      "url": "https://www.tiktok.com/@agentic.james",
      "name": "agentic.james",
      "added": "2024-01-21"
    },
    {
      "url": "https://www.tiktok.com/@techcreator",
      "name": "techcreator",
      "added": "2024-01-21"
    }
  ]
}
```

## Creating/Reading accounts.json

To read:
```bash
cat accounts.json 2>/dev/null || echo '{"active": null, "profiles": []}'
```

To write (use Python for proper JSON handling):
```bash
python3 -c "
import json
from pathlib import Path

accounts_file = Path('accounts.json')
if accounts_file.exists():
    data = json.loads(accounts_file.read_text())
else:
    data = {'active': None, 'profiles': []}

# Modify data as needed...
# data['active'] = 'NEW_URL'
# data['profiles'].append({'url': 'URL', 'name': 'NAME', 'added': 'DATE'})

accounts_file.write_text(json.dumps(data, indent=2))
print('Saved!')
"
```

## Integration with Other Commands

When `/bulk` or `/transcribe` runs, check for active profile:

1. If `accounts.json` exists and has an active profile, offer to use it
2. Otherwise, ask for profile URL as normal

## Validation

Before adding/switching, validate the profile:

```bash
source .venv/bin/activate && python -c "
from short_form_scraper.scraper.tiktok import TikTokScraper

url = 'PROFILE_URL_HERE'
scraper = TikTokScraper(url)

try:
    videos = list(scraper.get_video_urls(limit=1))
    if videos:
        print(f'Valid profile! Found videos.')
        print(f'Latest: {videos[0].title}')
    else:
        print('Profile exists but has no videos.')
except Exception as e:
    print(f'Error: Could not access profile - {e}')
"
```

## Example Session

User: `/accounts`

Claude:
**Manage TikTok Profiles**

What would you like to do?
1. Switch profile
2. Add profile
3. List profiles
4. Remove profile
5. Process multiple

User: 2

Claude: What TikTok profile URL do you want to add?

User: https://www.tiktok.com/@techreviewer

Claude:
[Validates profile]
Added @techreviewer to your profiles!

You now have 2 saved profiles. Run `/accounts` again to switch between them or process multiple at once.
