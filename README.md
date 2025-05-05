# Free Fire Info API

A powerful API for retrieving Free Fire player information and statistics with enhanced formatting and icons.

## Features

- 🎮 Get detailed player information with icons
- 📊 Retrieve comprehensive player statistics
- 🏆 View Battle Royale and Clash Squad performance
- 🔫 See top weapons and characters
- 🏰 Guild information with member details

## API Endpoints

### 1. Player Information

```
GET /api/player-info?id={player_id}
```

Returns basic player information including:
- Player name, UID, level, and server
- Account creation date and likes
- Rank information with icon
- Booyah Pass level
- Guild information (if available)
- Pet/animal information (if available)
- Basic stats summary

### 2. Player Statistics

```
GET /api/player-stats?id={player_id}
```

Returns detailed player statistics including:
- Battle Royale stats (matches, wins, K/D ratio, headshots, etc.)
- Clash Squad stats (if available)
- Top weapons with kill counts and headshot rates
- Character information

## Response Format

All responses are in JSON format with proper formatting and icons for better readability.

Example response from `/api/player-info`:

```json
{
  "data": {
    "playerInformation": {
      "name": "PlayerName",
      "uid": "123456789",
      "likes": "❤️ 1000",
      "level": "⭐ 50",
      "server": "IND",
      "signature": "Player's signature",
      "booyah_pass_level": "🎮 75",
      "account_created": "📅 2020-01-01 12:00:00",
      "rank": "💎 Diamond (2500 points)",
      "avatar_url": "https://www.library.freefireinfo.site/icons/902000045.png",
      "banner_url": "https://www.library.freefireinfo.site/icons/901000009.png"
    },
    "animal": {
      "name": "🐾 Falco",
      "icon_url": "https://www.library.freefireinfo.site/icons/pet_id.png"
    },
    "Guild": {
      "guildName": "🏰 GuildName",
      "guildId": "987654321",
      "guildLevel": "📊 Level 6",
      "guildMembers": "👥 20 members",
      "guildLeader": {
        "uid": "123456789",
        "nickName": "👑 LeaderName",
        "playerLevel": "⭐ 60",
        "booyah_pass_level": "🎮 80",
        "likes": "❤️ 2000",
        "account_created": "📅 2019-01-01 12:00:00"
      }
    },
    "stats": {
      "kills": "☠️ 1500",
      "wins": "🏆 200",
      "matches": "🎮 1000",
      "kd_ratio": "📊 1.88"
    }
  },
  "credits": "Imonxdre",
  "timestamp": "2023-06-15 12:34:56",
  "status": "success"
}
```

## Credits

Developed by Imonxdre

## Note

This API is for educational purposes only. Use responsibly and respect Garena's terms of service.