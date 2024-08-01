#to function this script needs three jsons (see lines 35ff) from https://github.com/Kengxxiao/ArknightsGameData_YoStar/tree/main/en_US/gamedata/excel

import json
import numpy as np

def levenshtein(word1, word2):
	m = len(word1)
	n = len(word2)
	D = np.zeros((m, n))
	for i in range(m):
		D[i][0] = i
	for j in range(n):
		D[0][j] = j
	if word1[0] != word2[0]: D[0][0] = 1
	for j in range(1,n): #rows
		if word1[0] != word2[0]: D[0][j] = D[0][j]+1
		for i in range(1,m): #columns
			a = D[i-1][j-1] if word1[i]==word2[j] else 2000
			b = D[i-1][j] + 1
			c = D[i][j-1] + 1
			d = D[i-1][j-1] + 1
			D[i][j] = min(a,b,c,d)
	return (int(D[m-1][n-1]))

class OperatorData:
	def __init__(self, name, promotion=2, level=90, module=1, module_lvl=3, skill=3, skill_lvl=10, pot=6, trust=100):
		self.atk = 0
		self.atk_interval = 1.6
		self.skill_data = [] #all the available skill scalings
		self.skill_cost = 50
		self.skill_duration = 30
		self.talent_data = [] #all the available talent scalings, affected by promotion and module.
		self.talent_data2 = []
		self.attack_speed = 100
		
		#These files are like 7MB each, maybe not a good idea to load them each time. 
		with open('character_table.json',encoding="utf8") as json_file:
			character_data = json.load(json_file)
		with open('skill_table.json',encoding="utf8") as json_file:
			skill_data = json.load(json_file)
		with open('battle_equip_table.json',encoding="utf8") as json_file:
			module_data = json.load(json_file)
		
		
		#Get the weird name for the operator
		current_key = None
		for key in character_data.keys():
			if character_data[key]["name"].lower() == name:
				current_key = key
				break
		if current_key == None:
			for key in character_data.keys():
				if levenshtein(character_data[key]["name"].lower(),name) < 2:
					current_key = key
					break
		if current_key == None:
			for key in character_data.keys():
				if levenshtein(character_data[key]["name"].lower(),name) < 3:
					current_key = key
					break
		if current_key == None: raise KeyError
		weird_name =  current_key.split('_')[2]
		
		
		#get atk interval
		self.atk_interval = lvl_1_atk = character_data[current_key]["phases"][promotion]["attributesKeyFrames"][0]["data"]["baseAttackTime"]		
		
		#Get the base atk for the input
		#1.level base atk
		max_level = character_data[current_key]["phases"][promotion]["maxLevel"]
		level = max(1,min(max_level,level))
		lvl_1_atk = character_data[current_key]["phases"][promotion]["attributesKeyFrames"][0]["data"]["atk"]
		lvl_max_atk = character_data[current_key]["phases"][promotion]["attributesKeyFrames"][1]["data"]["atk"]
		self.atk = lvl_1_atk + (lvl_max_atk-lvl_1_atk) * (level-1) / (max_level-1)
		
		#2.Get the trust atk
		trust = max(1,min(100,trust))
		self.atk += character_data[current_key]["favorKeyFrames"][1]["data"]["atk"] * trust / 100
		
		#3.Get the potential atk
		for potential in character_data[current_key]["potentialRanks"]:
			if potential["type"] != "BUFF": continue
			if potential["buff"]["attributes"]["attributeModifiers"][0]["attributeType"] == "ATK":
				self.atk += potential["buff"]["attributes"]["attributeModifiers"][0]["value"]
		
		#4.Get the module atk
		#f this. typically the resKey entry is weird_name + "_equip_2_1_p1" . 2 is the module(y), 1 is the module lvl and p1 is for different talent changes. (example: ashlock atk+ is p1. and atk++ when no ranged tiles around is p2)
		main_key = ""
		if promotion == 2 and level >= max_level - 30 and module > 0:
			main_key = "uniequip_002_" + weird_name #002 is the first module (chronically, not necessarily X), 003 is the second and only ebenholz has 004, which i will not cover here.
			correct_resKey = True
			try:
				"equip" in module_data[main_key]["phases"][1]["parts"][1]["resKey"]
			except TypeError:
				correct_resKey = False
			
			if correct_resKey:
				#Case 1: resKey exists and is correct
				if int(module_data[main_key]["phases"][1]["parts"][1]["resKey"][-6]) == module: 
					for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
						if stat["key"] == "atk":
							self.atk += stat["value"]
						elif stat["key"] == "attack_speed":
							self.attack_speed += stat["value"]
				#Case 2: resKey exists and is false
				else:
					try: #Add the stats from the second module								
						main_key = "uniequip_003_" + weird_name
						for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
							if stat["key"] == "atk":
								self.atk += stat["value"]
							elif stat["key"] == "attack_speed":
								self.attack_speed += stat["value"]
					except KeyError: #TODO: there is no second module, do we return the wrong module or none at all? (right now we return the other module)
						main_key = "uniequip_002_" + weird_name
						for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
							if stat["key"] == "atk":
								self.atk += stat["value"]
							elif stat["key"] == "attack_speed":
								self.attack_speed += stat["value"]
			else:

				has_second_module = True
				try:
					main_key = "uniequip_003_" + weird_name
					_ = int(module_data[main_key]["phases"][1]["parts"][1]["resKey"][-6]) == module
				except KeyError:
					has_second_module = False
					main_key = "uniequip_002_" + weird_name
				
				#Case 3: resKey doesnt exist, but there is only 1 module anyway, so pick that
				if not has_second_module:
					for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
						if stat["key"] == "atk":
							self.atk += stat["value"]
						elif stat["key"] == "attack_speed":
							self.attack_speed += stat["value"]

				#Case 4: resKey doesnt exist, and there is a second module. if that also doesnt have a resKey we can throw an Error, because here we genuinely dont know what to do
				else:
					if int(module_data[main_key]["phases"][1]["parts"][1]["resKey"][-6]) == module: #it is the correct module
						for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
							if stat["key"] == "atk":
								self.atk += stat["value"]
							elif stat["key"] == "attack_speed":
								self.attack_speed += stat["value"]
					else: #it's not the correct module, so the first module has to be the correct one
						main_key = "uniequip_002_" + weird_name
						for stat in module_data[main_key]["phases"][module_lvl-1]["attributeBlackboard"]:
							if stat["key"] == "atk":
								self.atk += stat["value"]
							elif stat["key"] == "attack_speed":
								self.attack_speed += stat["value"]
				
		#get skill data- duration, cost and scalings
		skill_amount = 1
		rarity = int(character_data[current_key]["rarity"][-1])
		if rarity > 3: skill_amount = 2
		if rarity == 6: skill_amount = 3
		skill = max(1,min(skill_amount, skill))
		skill_key = character_data[current_key]["skills"][skill - 1]["skillId"]
		self.skill_duration = skill_data[skill_key]["levels"][skill_lvl-1]["duration"]
		self.skill_cost = skill_data[skill_key]["levels"][skill_lvl-1]["spData"]["spCost"]
		for entry in skill_data[skill_key]["levels"][skill_lvl-1]["blackboard"]:
			self.skill_data.append(entry["value"])
		
		
		#get talent data without module.
		for talent in character_data[current_key]["talents"]:
			for candidate in talent["candidates"]:
				if int(candidate["unlockCondition"]["phase"][-1]) <= promotion and int(candidate["requiredPotentialRank"]) <= pot:
					if candidate["prefabKey"] == "1":
						self.talent_data = []
						for data in candidate["blackboard"]:
							self.talent_data.append(data["value"])
					else:
						self.talent_data2 = []
						for data in candidate["blackboard"]:
							self.talent_data2.append(data["value"])
		#TODO: get talent changes from module
		if promotion == 2 and level >= max_level - 30 and module > 0 and module_lvl > 1:
			for change_data in module_data[main_key]["phases"][module_lvl-1]["parts"]:
				if change_data["target"] == "TRAIT":
					pass
				else:
					for change_candidate in change_data["addOrOverrideTalentDataBundle"]["candidates"]:
						if int(change_candidate["requiredPotentialRank"]) <= pot:
							if change_candidate["prefabKey"] == "1":
								self.talent_data = []
								for change_data in change_candidate["blackboard"]:
									self.talent_data.append(change_data["value"])
							else:
								self.talent_data2 = []
								for change_data in change_candidate["blackboard"]:
									self.talent_data2.append(change_data["value"])






operator_stats = OperatorData("degenbrecher",promotion=2, level=90, module=2, module_lvl=2, skill=3, skill_lvl=9, pot=6, trust=100)

print(operator_stats.talent_data2)






#relevant data, Operator json:
"""
First level: 
	"char_ABCD_something":nextlevel #char id is not helpful, whislash for example is called sophia

		"name": "Op_name" #name is upper case
		"rarity": "TIER_5"
		"phases": [nextnevel] #E1 E2 E3
		
			"maxLevel": 50
			"attributesKeyFrames": [nextlevel] #minLvl data and maxlvl data
			
				"data": nextlevel
					"atk": 390
					"baseAttackTime": 1.6
		
		"skills": [nextnevel] #skill1, skill2, skill3
			"skillId": "skchr_warmy_1"
		
		
		"potentialRanks": [nextlevel] #pot2 - pot6
			"type": "CUSTOM"/"BUFF"
			"description": "ATK +25"
			"buff": nextlevl
				"attributes": nextlevel
					"attributeModifiers": [nextlevel] # seems to be only one element though
						"attributeType": "COST"/"ATK"
						"value": 25.0
			
		"favorKeyFrames": [nextlevel] #0 trust vs max trust
			"data": nextlevel
				"atk": 65
				"attackSpeed": 0.0


#relevant data, skill json:
first level:
	"skchr_vigna_1": nextlevel
		
		"levels":[nextlevel] #10 entries, skill level 1 - mastery 3 
			"duration": 20.0
			"spData": nextlevel
				"maxChargeTime": 2 #is this sp lockout?
				"spCost": 30
			"blackboard": [nextlevel] #list of ALL modifiers of the skill, be it atk scale, aspd, atk, dmg etc
				"key": "atk",
				"value": 0.2,
				"valueStr": null

#"""





