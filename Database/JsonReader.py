#to function this script needs three jsons (see lines 35ff) from https://github.com/Kengxxiao/ArknightsGameData_YoStar/tree/main/en_US/gamedata/excel

import json
import numpy as np

id_dict = {'Lancet2': 'char_285_medic2','Castle3': 'char_286_cast3','THRMEX': 'char_376_therex','JusticeKnight': 'char_4000_jnight','TerraResearchCommission': 'char_4077_palico',
           'UOfficial': 'char_4091_ulika','Friston3': 'char_4093_frston','Yato': 'char_502_nblade','NoirCorne': 'char_500_noirc','Rangers': 'char_503_rang',
           'Durin': 'char_501_durin','12F': 'char_009_12fce','Fang': 'char_123_fang','Vanilla': 'char_240_wyvern','ReserveOperatorMelee': 'char_504_rguard',
           'Plume': 'char_192_falco','Melantha': 'char_208_melan','Popukar': 'char_281_popka','Cardigan': 'char_209_ardign','Beagle': 'char_122_beagle',
           'ReserveOperatorDefender': 'char_514_rdfend','Spot': 'char_284_spot','Kroos': 'char_124_kroos','Adnachiel': 'char_211_adnach','ReserveOperatorSniper': 'char_507_rsnipe',
           'Lava': 'char_121_lava','Hibiscus': 'char_120_hibisc','Ansel': 'char_212_ansel','ReserveOperatorMedic': 'char_506_rmedic','Steward': 'char_210_stward',
           'ReserveOperatorCaster': 'char_505_rcast','Orchid': 'char_278_orchid','Haze': 'char_141_nights','Gitano': 'char_109_fmout','Greyy': 'char_253_greyy',
           'Click': 'char_328_cammou','Indigo': 'char_469_indigo','Pudding': 'char_4004_pudd','Jessica': 'char_235_jesica','Meteor': 'char_126_shotst',
           'Vermeil': 'char_190_clour','May': 'char_133_mm','Shirayuki': 'char_118_yuki','Pinecone': 'char_440_pinecn','Ambriel': 'char_302_glaze','Aciddrop': 'char_366_acdrop',
           'Totter': 'char_4062_totter','Caper': 'char_4100_caper','Courier': 'char_198_blackd','Scavenger': 'char_149_scave','Vigna': 'char_290_vigna','Myrtle': 'char_151_myrtle',
           'Beanstalk': 'char_452_bstalk','Dobermann': 'char_130_doberm','Matoimaru': 'char_289_gyuki','Conviction': 'char_159_peacok','Frostleaf': 'char_193_frostl',
           'Estelle': 'char_127_estell','Mousse': 'char_185_frncat','Cutter': 'char_301_cutter','Utage': 'char_337_utage','Arene': 'char_271_spikes','LuoXiaohei': 'char_4067_lolxh',
           'Quartz': 'char_4063_quartz','Humus': 'char_491_humus','Gravel': 'char_237_gravel','Jaye': 'char_272_strong','Rope': 'char_236_rope','Myrrh': 'char_117_myrrh',
           'Gavial': 'char_187_ccheal','Sussurro': 'char_298_susuro','Perfumer': 'char_181_flower','Purestream': 'char_385_finlpp','Chestnut': 'char_4041_chnut',
           'Matterhorn': 'char_199_yak','Cuora': 'char_150_snakek','Bubble': 'char_381_bubble','Gummy': 'char_196_sunbr','Dur-nar': 'char_260_durnar',
           'Deepcolor': 'char_110_deepcl','Earthspirit': 'char_183_skgoat','Podenco': 'char_258_podego','Roberta': 'char_484_robrta','Ethan': 'char_355_ethan',
           'Shaw': 'char_277_sqrrel','Verdant': 'char_4107_vrdant','Ptilopsis': 'char_128_plosis','Breeze': 'char_275_breeze','Zima': 'char_115_headbr',
           'Texas': 'char_102_texas','Chiave': 'char_349_chiave','Poncirus': 'char_488_buildr','Tulip': 'char_513_apionr','Reed': 'char_261_sddrag',
           'WildMane': 'char_496_wildmn','Elysium': 'char_401_elysm','Blacknight': 'char_476_blkngt','Cantabile': 'char_497_ctable','Puzzle': 'char_4017_puzzle',
           'Swire': 'char_308_swire','Whislash': 'char_265_sophia','Bryophyta': 'char_4106_bryota','Franka': 'char_106_franka','Flamebringer': 'char_131_flameb',
           'Morgan': 'char_154_morgan','Sharp': 'char_508_aguard','Indra': 'char_155_tiger','Flint': 'char_415_flint','Dagda': 'char_157_dagda','Lappland': 'char_140_whitew',
           'Ayerscarpe': 'char_294_ayer','Leto': 'char_194_leto','Wind Chimes': 'char_4083_chimes','Bibeak': 'char_252_bibeak','Tachanka': 'char_459_tachak',
           'Specter': 'char_143_ghost','Broca': 'char_356_broca','Astesia': 'char_274_astesi','Sideroca': 'char_333_sidero','Akafuyu': 'char_475_akafyu',
           'NoirCorneAlter': 'char_1030_noirc2','LaPluma': 'char_421_crow','Highmore': 'char_4066_highmo','Tequila': 'char_486_takila','BluePoison': 'char_129_bluep',
           'Platinum': 'char_204_platnm','GreyThroat': 'char_367_swllow','Stormeye': 'char_511_asnipe','April': 'char_365_aprl','KroosAlter': 'char_1021_kroos2',
           'Insider': 'char_498_inside','Meteorite': 'char_219_meteo','Sesa': 'char_379_sesa','Jieyun': 'char_4078_bdhkgt','Executor': 'char_279_excu','Aosta': 'char_346_aosta',
           'Amiya': 'char_002_amiya','Absinthe': 'char_405_absin','Tomimi': 'char_411_tomimi','Qanipalaat': 'char_466_qanik','Skyfire': 'char_166_skfire',
           'Pith': 'char_509_acast','Leizi': 'char_306_leizi','Astgenne': 'char_135_halo','Beeswax': 'char_344_beewax','Leonhardt': 'char_373_lionhd',
           'Santalla': 'char_341_sntlla','Mint': 'char_388_mint','Iris': 'char_338_iris','Harmonie': 'char_297_hamoni','Delphine': 'char_4110_delphn',
           'LavaAlter': 'char_1011_lava2','Corroserum': 'char_489_serum','Kjera': 'char_4013_kjera','Rockrock': 'char_4040_rockr','Minimalist': 'char_4054_malist',
           'Diamante': 'char_499_kaitou','Warmy': 'char_4081_warmy','Mayer': 'char_242_otter','Scene': 'char_336_folivo','Silence': 'char_108_silent',
           'Warfarin': 'char_171_bldsk','Folinic': 'char_345_folnic','Touch': 'char_510_amedic','Ceylon': 'char_348_ceylon','Whisperain': 'char_436_whispr',
           'Tuye': 'char_402_tuye','Mulberry': 'char_473_mberry','Honeyberry': 'char_449_glider','Harold': 'char_4114_harold','HibiscusAlter': 'char_1024_hbisc2',
           'Vendela': 'char_494_vendla','Paprika': 'char_4071_peper','Nearl': 'char_148_nearl','Hung': 'char_226_hmau','Bassline': 'char_4109_baslin',
           'ProjektRed': 'char_144_red','WaaiFu': 'char_243_waaifu','Kafka': 'char_214_kafka','MrNothing': 'char_455_nothin','Liskarm': 'char_107_liskam',
           'Croissant': 'char_201_moeshd','Bison': 'char_325_bison','Vulcan': 'char_163_hpsts','Asbestos': 'char_378_asbest','Shalem': 'char_512_aprot',
           'Czerny': 'char_4047_pianst','Blitz': 'char_457_blitz','Heavyrain': 'char_304_zebra','Ashlock': 'char_431_ashlok','Firewhistle': 'char_493_firwhl',
           'Aurora': 'char_422_aurora','Cement': 'char_464_cement','Provence': 'char_145_prove','Melanite': 'char_4006_melnte','Firewatch': 'char_158_milu',
           'Andreana': 'char_218_cuttle','Lunacub': 'char_4014_lunacu','Toddifons': 'char_363_toddi','Erato': 'char_4043_erato','GreyyAlter': 'char_1027_greyy2',
           'Coldshot': 'char_4104_coldst','Spuria': 'char_4015_spuria','Cliffheart': 'char_173_slchan','Snowsant': 'char_383_snsant','Almond': 'char_4105_almond',
           'Pramanix': 'char_174_slbell','Shamare': 'char_254_vodfox','Istina': 'char_195_glassb','Glaucus': 'char_326_glacus','Proviso': 'char_4032_provs',
           'Windflit': 'char_433_windft','Sora': 'char_101_sora','Heidi': 'char_4045_heidi','Tsukinogi': 'char_343_tknogi','NineColoredDeer': 'char_4019_ncdeer',
           'Quercus': 'char_492_quercu','Valarqvin': 'char_4102_threye','Manticore': 'char_215_mantic','Kirara': 'char_478_kirara','FEater': 'char_241_panda',
           'Enforcer': 'char_4036_forcer','Robin': 'char_451_robin','Frost': 'char_458_rfrost','Bena': 'char_369_bena','Kazemaru': 'char_4016_kazema',
           'Exusiai': 'char_103_angel','Archetto': 'char_332_archet','Ash': 'char_456_ash','Schwarz': 'char_340_shwaz','Pozemka': 'char_4055_bgsnow',
           'Fartooth': 'char_430_fartth','W': 'char_113_cqbw','Fiammetta': 'char_300_phenxi','Rosa': 'char_197_poca','Typhon': 'char_2012_typhon',
           'Rosmontis': 'char_391_rosmon','ChenAlter': 'char_1013_chen2','Ray': 'char_4117_ray','Siege': 'char_112_siege','Bagpipe': 'char_222_bpipe',
		   'Saga': 'char_362_saga','Saileach': 'char_479_sleach','Flametail': 'char_420_flamtl','Vigil': 'char_427_vigil','Muelsyse': 'char_249_mlyss',
		   'Ines': 'char_4087_ines','Ifrit': 'char_134_ifrit','Mostima': 'char_213_mostma','Eyjafjalla': 'char_180_amgoat','Ceobe': 'char_2013_cerber',
		   'Hoolheyak': 'char_4027_heyak','Dusk': 'char_2015_dusk','Passenger': 'char_472_pasngr','Carnelian': 'char_426_billro','Lin': 'char_4080_lin',
           'Goldenglow': 'char_377_gdglow','Ebenholz': 'char_4046_ebnhlz','Gnosis': 'char_206_gnosis','Angelina': 'char_291_aglina','Suzuran': 'char_358_lisa',
           'Magallan': 'char_248_mgllan','SkadiAlter': 'char_1012_skadi2','SilenceAlter': 'char_1031_slent2','Ling': 'char_2023_ling','Stainless': 'char_4072_ironmn',
           'Virtuosa': 'char_245_cello','Phantom': 'char_250_phatom','TexasAlter': 'char_1028_texas2','YatoAlter': 'char_1029_yato2','Lee': 'char_322_lmlee',
           'SwireAlter': 'char_1033_swire2','Weedy': 'char_400_weedy','Aak': 'char_225_haak','Gladiia': 'char_474_glady','Mizuki': 'char_437_mizuki',
           'SpecterAlter': 'char_1023_ghost2','Dorothy': 'char_4048_doroth','Shining': 'char_147_shining','Nightingale': 'char_179_cgbird','Kaltsit': 'char_003_kalts',
		   'Lumen': 'char_4042_lumen','EyjafjallaAlter': 'char_1016_agoat2','ReedAlter': 'char_1020_reed2','Hoshiguma': 'char_136_hsguma','Saria': 'char_202_demkni',
		   'Blemishine': 'char_423_blemsh','Nian': 'char_2014_nian','Mudrock': 'char_311_mudrok','Penance': 'char_4065_judge','Eunectes': 'char_416_zumama',
		   'Horn': 'char_4039_horn','JessicaAlter': 'char_1034_jesca2','Mountain': 'char_264_f12yin','Chongyue': 'char_2024_chyue','SilverAsh': 'char_172_svrash',
		   'Mlynar': 'char_4064_mlynar','Thorns': 'char_293_thorns','Qiubai': 'char_4082_qiubai','Hoederer': 'char_4088_hodrer','Chen': 'char_010_chen',
           'Irene': 'char_4009_irene','Degenbrecher': 'char_4116_blkkgt','Blaze': 'char_017_huang','GavialAlter': 'char_1026_gvial2','Surtr': 'char_350_surtr',
           'Viviana': 'char_4098_vvana','Hellagur': 'char_188_helage','Pallas': 'char_485_pallas','NearlAlter': 'char_1014_nearl2','Lessing': 'char_4011_lessng',
           'ExecutorAlter': 'char_1032_excu2','Savage': 'char_230_savage','Catapult': 'char_282_catap','Midnight': 'char_283_midn','Beehunter': 'char_137_brownb',
		   'Jackie': 'char_347_jaksel','Nightmare': 'char_164_nightm','Grani': 'char_220_grani','Skadi': 'char_263_skadi'}


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

def fileHelper():
	content = ""
	with open('character_table.json',encoding="utf8") as json_file:
		character_data = json.load(json_file)
	with open("dictionary.txt", 'w') as f:
		for key in character_data.keys():
			if str(key).startswith("char"):
				try:
					f.writelines(str(f"'{character_data[key]['name']}': '{key}',"))
				except:
					print(str(f"'{character_data[key]['name']}': '{key}',"))

class OperatorData:
	def __init__(self, current_key, promotion=2, level=90, module=1, module_lvl=3, skill=3, skill_lvl=10, pot=6, trust=100):
		self.atk = 0
		self.skill_data = [] #all the available skill scalings
		self.skill_cost = 50
		self.skill_duration = 30
		self.talent_data = [] #all the available talent scalings, affected by promotion and module.
		self.talent_data2 = []
		self.attack_speed = 100

		#rework
		self.rarity = 6
		self.atk_interval = 1.6
		self.available_modules = [] #1 for x, 2 for y, 3 for alpha/delta, the order matters to tell which is which. #TODO can be overwritten later

		self.atk_e0 = [0,0] #min/max, this format is somewhat needed for 1 and 3 stars
		self.atk_e1 = [0,0]
		self.atk_e2 = [0,0]
		self.atk_potential = [0,0] #required potential/value
		self.atk_module = [] #list( ? modules) of list( 3 module lvls) of values
		self.atk_trust = 0 #max value only

		self.aspd_potential = [0,0]
		self.aspd_trust = 0
		self.aspd_module = []

		self.skill_parameters = []
		self.skill_durations = []
		self.skill_costs = []

		#talents...
		self.has_second_talent = True
		self.talent1_parameters = []
		self.talent2_parameters = []
		self.talent1_defaults = []
		self.talent2_dafaults = []
		#idea 1: add conditions (promotion stage, level(e.g. orchid), potential stage, module stage)
		#problem 1: if the values are used in the dps calculations, then empty values cause crashes. so we need default values, those can however be 1 or 0,
		#   and we need to figure that one out as well. probably:
		# default value 0 keywords: atk, prob, duration, attack_speed, attack@prob, magic_resistance, sp_recovery_per_sec, base_attack_time
		# default value 1 keywords: atk_scale, atk_scale_2, damage_scale, heal_scale
		# note: aciddrop has atk scale below 1, where the default value should be 0.05 ...
		# note2: all this bs has to be included in the low/high-talent stuff too...



		
		#These files are like 7MB each, maybe not a good idea to load them each time. 
		with open('character_table.json',encoding="utf8") as json_file:
			character_data = json.load(json_file)
		with open('skill_table.json',encoding="utf8") as json_file:
			skill_data = json.load(json_file)
		with open('battle_equip_table.json',encoding="utf8") as json_file:
			module_data = json.load(json_file)
		
		"""
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
		if current_key == None: raise KeyError #"""
		weird_name =  current_key.split('_')[2]
		
		
		#get atk interval
		self.rarity = int(character_data[current_key]["rarity"][-1])
		self.atk_interval = character_data[current_key]["phases"][0]["attributesKeyFrames"][0]["data"]["baseAttackTime"]

		#read atk values:
		self.atk_e0[0] = character_data[current_key]["phases"][0]["attributesKeyFrames"][0]["data"]["atk"]
		self.atk_e0[1] = character_data[current_key]["phases"][0]["attributesKeyFrames"][1]["data"]["atk"]
		if self.rarity > 2:
			self.atk_e1[0] = character_data[current_key]["phases"][1]["attributesKeyFrames"][0]["data"]["atk"]
			self.atk_e1[1] = character_data[current_key]["phases"][1]["attributesKeyFrames"][1]["data"]["atk"]
		if self.rarity > 3:
			self.atk_e2[0] = character_data[current_key]["phases"][2]["attributesKeyFrames"][0]["data"]["atk"]
			self.atk_e2[1] = character_data[current_key]["phases"][2]["attributesKeyFrames"][1]["data"]["atk"]
		
		self.atk_trust = character_data[current_key]["favorKeyFrames"][1]["data"]["atk"]

		for i, potential in enumerate(character_data[current_key]["potentialRanks"]):
			if potential["type"] != "BUFF": continue
			if potential["buff"]["attributes"]["attributeModifiers"][0]["attributeType"] == "ATK":
				self.atk_potential = [i+2, potential["buff"]["attributes"]["attributeModifiers"][0]["value"]]
			
			#read aspd values
			if potential["buff"]["attributes"]["attributeModifiers"][0]["attributeType"] == "ATTACK_SPEED":
				self.aspd_potential = [i+2, potential["buff"]["attributes"]["attributeModifiers"][0]["value"]]
		
		self.aspd_trust = character_data[current_key]["favorKeyFrames"][1]["data"]["attackSpeed"]

		#read skill values
		skill_ids = [skill_entry["skillId"] for skill_entry in character_data[current_key]["skills"]]
		
		for skill_id in skill_ids:
			current_skill_params = []
			current_skill_durations = []
			current_skill_costs = []
			for skill_level in skill_data[skill_id]["levels"]:
				current_skill_durations.append(skill_level["duration"])
				current_skill_costs.append(skill_level["spData"]["spCost"])
				current_input = []
				for entry in skill_level["blackboard"]:
					current_input.append(entry["value"])
				current_skill_params.append(current_input)
			self.skill_parameters.append(current_skill_params)
			self.skill_durations.append(current_skill_durations)
			self.skill_costs.append(current_skill_costs)
		
		#TODO: read talents
		#TODO: read module atk and aspd
		#TODO: worst of all: read talent changes from module

		#read talents
		self.has_second_talent = len(character_data[current_key]["talents"]) > 1
		
		for candidate in character_data[current_key]["talents"][0]["candidates"]:
			req_promo = int(candidate["unlockCondition"]["phase"][-1])
			req_level = candidate["unlockCondition"]["level"]
			req_pot = candidate["requiredPotentialRank"]
			req_module = 0
			talent_data = [tal_data["value"] for tal_data in candidate["blackboard"]]
			self.talent1_parameters.append([req_promo,req_level,req_pot,req_module,talent_data])
		if self.has_second_talent:
			for candidate in character_data[current_key]["talents"][1]["candidates"]:
				req_promo = int(candidate["unlockCondition"]["phase"][-1])
				req_level = candidate["unlockCondition"]["level"]
				req_pot = candidate["requiredPotentialRank"]
				req_module = 0
				talent_data = [tal_data["value"] for tal_data in candidate["blackboard"]]
				self.talent2_parameters.append([req_promo,req_level,req_pot,req_module,talent_data])
		
		#set_defaults (this maybe needs to be changed for some characters, but it should be helpful most of the time)
		for data in character_data[current_key]["talents"][0]["candidates"][-1]["blackboard"]:
			if data["key"] in ["atk", "prob", "duration", "attack_speed", "attack@prob", "magic_resistance", "sp_recovery_per_sec", "base_attack_time"]:
				self.talent1_defaults.append(0)
			else:
				self.talent1_defaults.append(1)
		if self.has_second_talent:
			for data in character_data[current_key]["talents"][1]["candidates"][-1]["blackboard"]:
				if data["key"] in ["atk", "prob", "duration", "attack_speed", "attack@prob", "magic_resistance", "sp_recovery_per_sec", "base_attack_time"]:
					self.talent2_dafaults.append(0)
				else:
					self.talent2_dafaults.append(1)

		#figure out the module situation.
		has_module = self.rarity > 3
		has_second_module = self.rarity > 5
		try:
			module_key = "uniequip_002_" + weird_name
			self.available_modules.append(int(module_data[module_key]["phases"][1]["parts"][1]["resKey"][-6]))
			try:
				module_key = "uniequip_003_" + weird_name
				self.available_modules.append(int(module_data[module_key]["phases"][1]["parts"][1]["resKey"][-6]))
			except TypeError:
				if 1 in self.available_modules: self.available_modules.append(2)
				else: self.available_modules.append(1)
			except KeyError:
				has_second_module = False
		except TypeError:
			try:
				module_key = "uniequip_003_" + weird_name
				if int(module_data[module_key]["phases"][1]["parts"][1]["resKey"][-6]) == 1:
					self.available_modules = [2,1]
				else:
					self.available_modules = [1,2]
			except TypeError:
				self.available_modules = [1,2]
				print(f"operator {current_key} has 2 unlabeled modules, you should double check that")
			except KeyError:
				has_second_module = False
				self.available_modules.append(1)
		except KeyError:
			has_module = False
		


		#4.Get the module atk
		#f this. typically the resKey entry is weird_name + "_equip_2_1_p1" . 2 is the module(y), 1 is the module lvl and p1 is for different talent changes. (example: ashlock atk+ is p1. and atk++ when no ranged tiles around is p2)
		max_level = 90
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
		print(main_key)
		if promotion == 2 and level >= max_level - 30 and module > 0 and module_lvl > 1:
			for change_data in module_data[main_key]["phases"][module_lvl-1]["parts"]:
				if change_data["target"] == "TALENT" or change_data["target"] == "TALENT_DATA_ONLY":
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






operator_stats = OperatorData("char_1034_jesca2",promotion=2, level=90, module=0, module_lvl=3, skill=1, skill_lvl=1, pot=6, trust=100)

print(operator_stats.skill_costs, operator_stats.skill_durations)
print(operator_stats.talent1_parameters,operator_stats.talent2_parameters)






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





