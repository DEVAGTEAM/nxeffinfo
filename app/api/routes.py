from flask import jsonify, request, Blueprint, Response
import requests
import binascii
from datetime import datetime
import json
from app.core.jwt_token import get_jwt
from app.core.encrypt import Encrypt_ID, encrypt_api
from app.core.parser import get_available_room


routes = Blueprint("routes", __name__)

# Icon URL base for Free Fire items
ICON_BASE_URL = "https://www.library.freefireinfo.site/icons/"

# Rank icons mapping
RANK_ICONS = {
    # BR Ranks
    "Bronze": "🥉",
    "Silver": "⚪",
    "Gold": "🥇",
    "Platinum": "💠",
    "Diamond": "💎",
    "Heroic": "👑",
    "Grandmaster": "🏆",
    # CS Ranks
    "Unranked": "❓",
}


@routes.route("/api/player-info", methods=["GET"])
def get_player_info():
    try:
        player_id = request.args.get("id")
        if not player_id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Player ID is required",
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 400

        token = get_jwt()
        if not token:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to generate JWT token",
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 500

        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(player_id)}1007"))
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        headers = {
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": "OB48",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-GA": "v1 1",
            "Authorization": f"Bearer {token}",
            "Content-Length": "16",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }

        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            hex_response = binascii.hexlify(response.content).decode("utf-8")
            json_result = get_available_room(hex_response)
            parsed_data = json.loads(json_result)

            try:
                # Get rank name based on points
                def get_rank_name(points):
                    if points < 1000:
                        return "Bronze"
                    elif points < 1400:
                        return "Silver"
                    elif points < 1800:
                        return "Gold"
                    elif points < 2100:
                        return "Platinum"
                    elif points < 3100:
                        return "Diamond"
                    elif points < 4500:
                        return "Heroic"
                    else:
                        return "Grandmaster"
                
                # Get avatar and banner images if available
                avatar_id = parsed_data["1"]["data"].get("4", {}).get("data", "")
                banner_id = parsed_data["1"]["data"].get("19", {}).get("data", "")
                
                # Get rank points
                rank_points = parsed_data["1"]["data"].get("8", {}).get("data", 0)
                rank_name = get_rank_name(rank_points)
                rank_icon = RANK_ICONS.get(rank_name, "")
                
                # Basic Info first with enhanced data and icons
                player_data = {
                    "playerInformation": {
                        "name": parsed_data["1"]["data"]["3"]["data"],
                        "uid": player_id,
                        "likes": f"❤️ {parsed_data['1']['data']['21']['data']}",
                        "level": f"⭐ {parsed_data['1']['data']['6']['data']}",
                        "server": parsed_data["1"]["data"]["5"]["data"],
                        "signature": parsed_data["9"]["data"]["9"]["data"],
                        "booyah_pass_level": f"🎮 {parsed_data['1']['data']['18']['data']}",
                        "account_created": f"📅 {datetime.fromtimestamp(parsed_data['1']['data']['44']['data']).strftime('%Y-%m-%d %H:%M:%S')}",
                        "rank": f"{rank_icon} {rank_name} ({rank_points} points)",
                        "avatar_url": f"{ICON_BASE_URL}{avatar_id}.png" if avatar_id else None,
                        "banner_url": f"{ICON_BASE_URL}{banner_id}.png" if banner_id else None,
                    }
                }

                # Animal Info second with icon
                try:
                    animal_name = parsed_data["8"]["data"]["2"]["data"]
                    animal_id = parsed_data["8"]["data"].get("1", {}).get("data", "")
                    player_data["animal"] = {
                        "name": f"🐾 {animal_name}",
                        "icon_url": f"{ICON_BASE_URL}{animal_id}.png" if animal_id else None
                    }
                except:
                    player_data["animal"] = None

                # Guild Info last with enhanced formatting
                try:
                    guild_name = parsed_data["6"]["data"]["2"]["data"]
                    guild_id = parsed_data["6"]["data"]["1"]["data"]
                    guild_level = parsed_data["6"]["data"]["4"]["data"]
                    guild_members = parsed_data["6"]["data"]["6"]["data"]
                    
                    # Get leader info with enhanced formatting
                    leader_uid = parsed_data["6"]["data"]["3"]["data"]
                    leader_name = parsed_data["7"]["data"]["3"]["data"]
                    leader_level = parsed_data["7"]["data"]["6"]["data"]
                    leader_bp_level = parsed_data["7"]["data"]["18"]["data"]
                    leader_likes = parsed_data["7"]["data"]["21"]["data"]
                    leader_created = datetime.fromtimestamp(parsed_data["7"]["data"]["44"]["data"]).strftime("%Y-%m-%d %H:%M:%S")
                    
                    player_data["Guild"] = {
                        "guildName": f"🏰 {guild_name}",
                        "guildId": guild_id,
                        "guildLevel": f"📊 Level {guild_level}",
                        "guildMembers": f"👥 {guild_members} members",
                        "guildLeader": {
                            "uid": leader_uid,
                            "nickName": f"👑 {leader_name}",
                            "playerLevel": f"⭐ {leader_level}",
                            "booyah_pass_level": f"🎮 {leader_bp_level}",
                            "likes": f"❤️ {leader_likes}",
                            "account_created": f"📅 {leader_created}",
                        },
                    }
                except:
                    player_data["Guild"] = None

                # Add stats section if available
                try:
                    kills = parsed_data.get("10", {}).get("data", {}).get("3", {}).get("data", 0)
                    wins = parsed_data.get("10", {}).get("data", {}).get("2", {}).get("data", 0)
                    matches = parsed_data.get("10", {}).get("data", {}).get("1", {}).get("data", 0)
                    
                    if kills or wins or matches:
                        player_data["stats"] = {
                            "kills": f"☠️ {kills}",
                            "wins": f"🏆 {wins}",
                            "matches": f"🎮 {matches}",
                            "kd_ratio": f"📊 {round(kills/max(1, matches-wins), 2)}"
                        }
                except:
                    pass
               
                result = {
                    "data": player_data,
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success"
                }

                return Response(
                    json.dumps(result, indent=2, sort_keys=False),
                    mimetype="application/json"
                )

            except Exception as e:
                return jsonify(
                    {
                        "message": f"Failed to parse player information: {str(e)}",
                        "credits": "nexxlokesh"
                    }
                ), 500

        return jsonify(
            {
                "message": f"API request failed with status code: {response.status_code}",
                "credits": "nexxlokesh"
            }
        ), response.status_code

    except Exception as e:
        return jsonify(
            {
                "message": f"An unexpected error occurred: {str(e)}",
                "credits": "nexxlokesh"
            }
        ), 500


@routes.route("/api/player-stats", methods=["GET"])
def get_player_stats():
    try:
        player_id = request.args.get("id")
        if not player_id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Player ID is required",
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 400

        token = get_jwt()
        if not token:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to generate JWT token",
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 500

        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(player_id)}1007"))
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        headers = {
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": "OB48",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-GA": "v1 1",
            "Authorization": f"Bearer {token}",
            "Content-Length": "16",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }

        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            hex_response = binascii.hexlify(response.content).decode("utf-8")
            json_result = get_available_room(hex_response)
            parsed_data = json.loads(json_result)

            try:
                # Get player basic info
                player_name = parsed_data["1"]["data"]["3"]["data"]
                player_level = parsed_data["1"]["data"]["6"]["data"]
                player_server = parsed_data["1"]["data"]["5"]["data"]
                
                # Extract all available stats
                stats_data = {}
                
                # Battle Royale Stats
                try:
                    br_stats = parsed_data.get("10", {}).get("data", {})
                    if br_stats:
                        kills = br_stats.get("3", {}).get("data", 0)
                        wins = br_stats.get("2", {}).get("data", 0)
                        matches = br_stats.get("1", {}).get("data", 0)
                        headshots = br_stats.get("4", {}).get("data", 0)
                        top10 = br_stats.get("5", {}).get("data", 0)
                        survival_time = br_stats.get("7", {}).get("data", 0)
                        distance = br_stats.get("6", {}).get("data", 0)
                        
                        # Calculate derived stats
                        win_rate = round((wins / max(1, matches)) * 100, 2)
                        kd_ratio = round(kills / max(1, matches - wins), 2)
                        headshot_rate = round((headshots / max(1, kills)) * 100, 2)
                        avg_survival = round(survival_time / max(1, matches), 2)
                        
                        stats_data["battleRoyale"] = {
                            "overview": {
                                "matches": f"🎮 {matches}",
                                "wins": f"🏆 {wins}",
                                "winRate": f"📈 {win_rate}%",
                                "kills": f"☠️ {kills}",
                                "kdRatio": f"📊 {kd_ratio}",
                            },
                            "detailed": {
                                "headshots": f"🎯 {headshots}",
                                "headshotRate": f"🎯 {headshot_rate}%",
                                "top10": f"🔝 {top10}",
                                "top10Rate": f"🔝 {round((top10 / max(1, matches)) * 100, 2)}%",
                                "avgSurvivalTime": f"⏱️ {avg_survival} seconds",
                                "totalDistance": f"🏃 {distance} meters",
                            }
                        }
                except:
                    stats_data["battleRoyale"] = None
                
                # Clash Squad Stats if available
                try:
                    cs_stats = parsed_data.get("11", {}).get("data", {})
                    if cs_stats:
                        cs_kills = cs_stats.get("3", {}).get("data", 0)
                        cs_wins = cs_stats.get("2", {}).get("data", 0)
                        cs_matches = cs_stats.get("1", {}).get("data", 0)
                        cs_headshots = cs_stats.get("4", {}).get("data", 0)
                        cs_mvp = cs_stats.get("5", {}).get("data", 0)
                        
                        # Calculate derived stats
                        cs_win_rate = round((cs_wins / max(1, cs_matches)) * 100, 2)
                        cs_kd_ratio = round(cs_kills / max(1, cs_matches), 2)
                        cs_headshot_rate = round((cs_headshots / max(1, cs_kills)) * 100, 2)
                        
                        stats_data["clashSquad"] = {
                            "overview": {
                                "matches": f"🎮 {cs_matches}",
                                "wins": f"🏆 {cs_wins}",
                                "winRate": f"📈 {cs_win_rate}%",
                                "kills": f"☠️ {cs_kills}",
                                "kdRatio": f"📊 {cs_kd_ratio}",
                            },
                            "detailed": {
                                "headshots": f"🎯 {cs_headshots}",
                                "headshotRate": f"🎯 {cs_headshot_rate}%",
                                "mvp": f"🌟 {cs_mvp}",
                                "mvpRate": f"🌟 {round((cs_mvp / max(1, cs_matches)) * 100, 2)}%",
                            }
                        }
                except:
                    stats_data["clashSquad"] = None
                
                # Weapon stats if available
                try:
                    weapon_stats = parsed_data.get("12", {}).get("data", {})
                    if weapon_stats:
                        weapons_data = []
                        for weapon_id, weapon_info in weapon_stats.items():
                            if isinstance(weapon_info, dict) and "data" in weapon_info:
                                weapon_data = weapon_info["data"]
                                weapon_name = weapon_data.get("1", {}).get("data", "Unknown Weapon")
                                weapon_kills = weapon_data.get("2", {}).get("data", 0)
                                weapon_headshots = weapon_data.get("3", {}).get("data", 0)
                                
                                if weapon_kills > 0:
                                    weapons_data.append({
                                        "name": weapon_name,
                                        "kills": f"☠️ {weapon_kills}",
                                        "headshots": f"🎯 {weapon_headshots}",
                                        "headshotRate": f"🎯 {round((weapon_headshots / max(1, weapon_kills)) * 100, 2)}%",
                                        "icon": f"{ICON_BASE_URL}weapon_{weapon_id}.png"
                                    })
                        
                        # Sort weapons by kills
                        if weapons_data:
                            weapons_data.sort(key=lambda x: int(x["kills"].split(" ")[1]), reverse=True)
                            stats_data["weapons"] = weapons_data[:5]  # Top 5 weapons
                except:
                    stats_data["weapons"] = None
                
                # Character/Pet stats if available
                try:
                    character_stats = parsed_data.get("13", {}).get("data", {})
                    if character_stats:
                        characters_data = []
                        for char_id, char_info in character_stats.items():
                            if isinstance(char_info, dict) and "data" in char_info:
                                char_data = char_info["data"]
                                char_name = char_data.get("1", {}).get("data", "Unknown Character")
                                char_level = char_data.get("2", {}).get("data", 0)
                                char_skill = char_data.get("3", {}).get("data", "Unknown Skill")
                                
                                characters_data.append({
                                    "name": char_name,
                                    "level": f"⭐ {char_level}",
                                    "skill": char_skill,
                                    "icon": f"{ICON_BASE_URL}character_{char_id}.png"
                                })
                        
                        if characters_data:
                            characters_data.sort(key=lambda x: int(x["level"].split(" ")[1]), reverse=True)
                            stats_data["characters"] = characters_data[:3]  # Top 3 characters
                except:
                    stats_data["characters"] = None
                
                # Compile the final response
                result = {
                    "playerInfo": {
                        "name": player_name,
                        "uid": player_id,
                        "level": f"⭐ {player_level}",
                        "server": player_server
                    },
                    "stats": stats_data,
                    "credits": "Imonxdre",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success"
                }

                return Response(
                    json.dumps(result, indent=2, sort_keys=False),
                    mimetype="application/json"
                )

            except Exception as e:
                return jsonify(
                    {
                        "status": "error",
                        "message": f"Failed to parse player statistics: {str(e)}",
                        "credits": "Imonxdre",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                ), 500

        return jsonify(
            {
                "status": "error",
                "message": f"API request failed with status code: {response.status_code}",
                "credits": "Imonxdre",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ), response.status_code

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
                "credits": "Imonxdre",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ), 500
