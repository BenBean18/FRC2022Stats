import json, sys
event = sys.argv[1]
print(event)
with open("all_"+event+"_matches.json", "r") as f:
    data = json.load(f)

class TeamStats:
    auto_points = 0.0
    teleop_non_endgame_points = 0.0
    endgame_points = 0.0
    upper_hub_cargo = 0.0
    lower_hub_cargo = 0.0
    team_climb = 0.0 # 0 = none, 1 = mid, 2 = high, 3 = traversal
    win_percent = 0

class TeamTotalStats:
    auto_points = 0.0
    teleop_non_endgame_points = 0.0
    endgame_points = 0.0
    upper_hub_cargo = 0.0
    lower_hub_cargo = 0.0
    team_climb = 0.0 # 0 = none, 1 = mid, 2 = high, 3 = traversal
    won = 0
    matches = 0

    def get_avg_stats(self):
        t = TeamStats()
        t.auto_points = self.auto_points / self.matches
        t.teleop_non_endgame_points = self.teleop_non_endgame_points / self.matches
        t.endgame_points = self.endgame_points / self.matches
        t.upper_hub_cargo = self.upper_hub_cargo / self.matches
        t.lower_hub_cargo = self.lower_hub_cargo / self.matches
        t.team_climb = self.team_climb / self.matches
        t.win_percent = self.won / self.matches
        return t

def string_climb_to_int(s):
    if s == "Traversal":
        return 3
    elif s == "High":
        return 2
    elif s == "Low":
        return 1
    else:
        return 0

teams = {} # key: id, value: TeamStats
for match in data:
    for alliance in ("blue", "red"):
        team_num = 0
        for team in match["alliances"][alliance]["team_keys"]:
            team_num += 1
            try:
                print(teams[team])
            except:
                teams[team] = TeamTotalStats()
            teams[team].auto_points += match["score_breakdown"][alliance]["autoPoints"] / 3.0
            teams[team].endgame_points += match["score_breakdown"][alliance]["endgamePoints"] / 3.0
            teams[team].teleop_non_endgame_points += match["score_breakdown"][alliance]["teleopPoints"] / 3.0 - match["score_breakdown"][alliance]["endgamePoints"] / 3.0
            teams[team].upper_hub_cargo += match["score_breakdown"][alliance]["teleopCargoUpperBlue"] + match["score_breakdown"][alliance]["teleopCargoUpperFar"] + match["score_breakdown"][alliance]["teleopCargoUpperNear"] + match["score_breakdown"][alliance]["teleopCargoUpperRed"]
            teams[team].lower_hub_cargo += match["score_breakdown"][alliance]["teleopCargoLowerBlue"] + match["score_breakdown"][alliance]["teleopCargoLowerFar"] + match["score_breakdown"][alliance]["teleopCargoLowerNear"] + match["score_breakdown"][alliance]["teleopCargoLowerRed"]
            teams[team].team_climb += string_climb_to_int(match["score_breakdown"][alliance]["endgameRobot"+str(team_num)])
            if match["winning_alliance"] == alliance:
                teams[team].won += 1
            teams[team].matches += 1

# Find best defense bot
# To calculate defense for team 9999, compare the average points per match of every other team when not playing 9999 vs when playing 9999
best_defense_bot = ""
best_defense_bot_impact = 0 # negative is good, means the bot is making other teams be below average
defense_bots = {}
for defense_bot in teams:
    average_impact = 0
    matches = 0
    for match in data:
        blue_teams = []
        blue_avg = 0
        blue_pts = match["score_breakdown"]["blue"]["totalPoints"]
        for team in match["alliances"]["blue"]["team_keys"]:
            blue_avg += teams[team].get_avg_stats().auto_points + teams[team].get_avg_stats().teleop_non_endgame_points + teams[team].get_avg_stats().endgame_points
            blue_teams.append(team)
        red_teams = []
        red_pts = match["score_breakdown"]["red"]["totalPoints"]
        red_avg = 0
        for team in match["alliances"]["red"]["team_keys"]:
            red_avg += teams[team].get_avg_stats().auto_points + teams[team].get_avg_stats().teleop_non_endgame_points + teams[team].get_avg_stats().endgame_points
            red_teams.append(team)
        if (defense_bot in blue_teams):
            average_impact += red_pts - red_avg
            matches += 1
        if (defense_bot in red_teams):
            average_impact += blue_pts - blue_avg
            matches += 1
    impact = average_impact / matches
    defense_bots[defense_bot] = impact
    if impact < best_defense_bot_impact:
        best_defense_bot_impact = impact
        best_defense_bot = defense_bot
print("This program believes that the best defense bot was " + best_defense_bot + ", with an average impact of " + str(best_defense_bot_impact) + " points")

csv = "team,auto,teleop,endgame,upper,lower,individual_climb,defensive_impact,win%\n"
for team in teams:
    stats = teams[team].get_avg_stats()
    csv += team + "," + str(stats.auto_points) + "," + str(stats.teleop_non_endgame_points) + "," + str(stats.endgame_points) + "," + str(stats.upper_hub_cargo) + "," + str(stats.lower_hub_cargo) + "," + str(stats.team_climb) + "," + str(defense_bots[team]) + "," + str(stats.win_percent) + "\n"

with open("all_"+event+"_teams.csv", "w") as f:
    f.write(csv)