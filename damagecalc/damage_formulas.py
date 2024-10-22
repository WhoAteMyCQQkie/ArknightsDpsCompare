import math  # fu Kjera
import dill

import numpy as np
import pylab as pl
from Database.JsonReader import OperatorData
from damagecalc.utils import PlotParameters

with open('Database/json_data.pkl', 'rb') as f:
	op_data_dict= dill.load(f)

class Operator:

	def __init__(self, name, params: PlotParameters, available_skills, module_overwrite = [], default_skill = 3, default_pot = 1, default_mod = 1):
		#needed data:
		max_levels = [[30,30,40,45,50,50],[0,0,55,60,70,80],[0,0,0,70,80,90]] #E0,E1,E2 -> rarity
		max_promotions = [0,0,1,2,2,2] #rarity
		max_skill_lvls = [4,7,10] #promotion level
		
		#reading the data from the json
		#TODO: use dictionary name -> op_data_dict key
		op_data: OperatorData = op_data_dict[name]
		rarity = op_data.rarity

		#Fixing illegal inputs and writing the name
		self.name = name

		self.atk_interval = op_data.atk_interval
		self.trait_dmg, self.talent_dmg, self.talent2_dmg, self.skill_dmg, self.module_dmg = params.conditionals
		self.targets = max(1,params.targets)
		self.sp_boost = params.sp_boost
		self.physical = op_data.physical
		
		elite = 2 if params.promotion < 0 else params.promotion
		elite = max(0,min(max_promotions[rarity-1],elite))
		if elite < max_promotions[rarity-1]:
			self.name += f" E{elite}"
		self.elite = elite
		
		level = params.level if params.level > 0 and params.level < max_levels[elite][rarity-1] else max_levels[elite][rarity-1]
		if level < max_levels[elite][rarity-1]:
			self.name += f" Lv{level}"
		
		pot =  params.pot
		if not params.pot in range(1,7):
			if default_pot in range(1,7): pot = default_pot
			else: pot = 1
		self.name += f" P{pot}"

		self.skill = 0
		if rarity > 2:
			skill = params.skill
			if not skill in available_skills:
				if default_skill in available_skills:
					skill = default_skill
				else:
					skill = available_skills[-1]
			if (elite == 1 or rarity < 6) and skill == 3:
				if 2 in available_skills:
					skill = 2
				elif 1 in available_skills:
					skill = 1
				else:
					skill = 0
			if elite == 0 and skill > 1:
				if 1 in available_skills:
					skill = 1
				else:
					skill = 0
			if skill > 0: 
				self.name += f" S{skill}"
			else:
				self.name += " NA"
			self.skill = skill

		skill_lvl = params.mastery if params.mastery > 0 and params.mastery < max_skill_lvls[elite] else max_skill_lvls[elite]
		if skill_lvl < max_skill_lvls[elite]:
			if skill_lvl == 9: self.name += "M2"
			elif skill_lvl == 8: self.name += "M1"
			else: self.name += f"Lv{skill_lvl}"

		trust = params.trust if params.trust >= 0 and params.trust < 100 else 100

		module_lvl = 0
		if elite == 2 and level >= max_levels[2][rarity-1]-30:
			available_modules = op_data.available_modules
			if module_overwrite != []: available_modules = module_overwrite
			module = default_mod
			if not default_mod in available_modules and default_mod != 0: raise ValueError("Default module is not part of the available modules")
			if op_data.atk_module == []: #no module data in the jsons
				available_modules = []
				module_lvl = 0
			if available_modules != []:
				if params.module == 0:
					module = 0
					self.name += " no Mod"
				else:
					if params.module in available_modules:
						module = params.module #else default mod
					module_lvl = params.module_lvl if params.module_lvl in [1,2,3] else 3
					if trust < 50:
						module_lvl = 1
					if trust < 100:
						module_lvl = min(2, module_lvl)
					mod_name = ["X","Y","$\\Delta$"]
					if name in ["Kaltsit","Phantom","Mon3tr"]:
						mod_name = ["X","Y","$\\alpha$"]
					self.name += " Mod" + mod_name[module-1] + f"{module_lvl}"
		
		
		if trust != 100:
			self.name += f" {trust}Trust"
		self.base_name = self.name

		########### Read all the parameters from the json
		self.attack_speed = 100
		self.atk = op_data.atk_e0[0] + (op_data.atk_e0[1]-op_data.atk_e0[0]) * (level-1) / (max_levels[elite][rarity-1]-1)
		if elite == 1: self.atk = op_data.atk_e1[0] + (op_data.atk_e1[1]-op_data.atk_e1[0]) * (level-1) / (max_levels[elite][rarity-1]-1)
		if elite == 2: self.atk = op_data.atk_e2[0] + (op_data.atk_e2[1]-op_data.atk_e2[0]) * (level-1) / (max_levels[elite][rarity-1]-1)

		if pot >= op_data.atk_potential[0]:
			self.atk += op_data.atk_potential[1]
		self.atk += op_data.atk_trust * trust / 100
		if pot >= op_data.aspd_potential[0]:
			self.attack_speed +=  op_data.aspd_potential[1]
		
		if elite == 2 and level >= max_levels[2][rarity-1]-30:
			if module in available_modules:
				if module == available_modules[0]:
					self.atk += op_data.atk_module[0][module_lvl-1]
					self.attack_speed += op_data.aspd_module[0][module_lvl-1]
				else: #maybe todo: 3rd module. especially with kaltsit and phantom now also having 3 mods.
					self.atk += op_data.atk_module[1][module_lvl-1]
					self.attack_speed += op_data.aspd_module[1][module_lvl-1]
		else:
			module = 0
		self.module = module

		if rarity > 2:
			self.skill_params = op_data.skill_parameters[skill-1][skill_lvl-1]
			self.skill_cost = op_data.skill_costs[skill-1][skill_lvl-1]
			self.skill_duration = op_data.skill_durations[skill-1][skill_lvl-1]

		#talent data format: [req_promo,req_level,req_module,req_mod_lvl,req_pot,talent_data]
		self.talent1_params = op_data.talent1_defaults
		if op_data.talent1_parameters != []:	
			current_promo = 0
			current_req_lvl = 0
			current_req_pot = 0
			current_req_module_lvl = 0
			for talent_data in op_data.talent1_parameters:
				if elite >= talent_data[0] and talent_data[0] >= current_promo:
					if level >= talent_data[1] and talent_data[1] >= current_req_lvl:
						if module == 0:
							if talent_data[2] == 0:
								if pot >= talent_data[4] and pot >= current_req_pot:
									self.talent1_params = talent_data[5]
									current_promo = talent_data[0]
									current_req_lvl = talent_data[1]
									current_req_pot = talent_data[4]
									current_req_module_lvl = talent_data[3]
						else:
							if talent_data[2] == 0:
								required_module = 0
							else:
								required_module = available_modules[0] if talent_data[2] == 1 else available_modules[1]
							if module == required_module or talent_data[2] == 0:
								if module_lvl >= talent_data[3] and module_lvl >= current_req_module_lvl:
									if pot >= talent_data[4] and pot >= current_req_pot:
										self.talent1_params = talent_data[5]
										current_promo = talent_data[0]
										current_req_lvl = talent_data[1]
										current_req_pot = talent_data[4]
										current_req_module_lvl = talent_data[3]
		self.module_lvl = module_lvl

		self.talent2_params = op_data.talent2_dafaults
		if op_data.talent2_parameters != []:	
			current_promo = 0
			current_req_lvl = 0
			current_req_pot = 0
			current_req_module_lvl = 0
			for talent_data in op_data.talent2_parameters:
				if elite >= talent_data[0] and talent_data[0] >= current_promo:
					if level >= talent_data[1] and talent_data[1] >= current_req_lvl:
						if module == 0:
							if talent_data[2] == 0:
								if pot >= talent_data[4] and pot >= current_req_pot:
									self.talent2_params = talent_data[5]
									current_promo = talent_data[0]
									current_req_lvl = talent_data[1]
									current_req_pot = talent_data[4]
									current_req_module_lvl = talent_data[3]
						else:
							if talent_data[2] == 0:
								required_module = 0
							else:
								required_module = available_modules[0] if talent_data[2] == 1 else available_modules[1]
							if module == required_module or talent_data[2] == 0:
								if module_lvl >= talent_data[3] and module_lvl >= current_req_module_lvl:
									if pot >= talent_data[4] and pot >= current_req_pot:
										self.talent2_params = talent_data[5]
										current_promo = talent_data[0]
										current_req_lvl = talent_data[1]
										current_req_pot = talent_data[4]
										current_req_module_lvl = talent_data[3]
		self.drone_atk = 0
		self.drone_atk_interval = 1
		if op_data.drone_atk_e0 != []:
			slot = skill - 1
			if len(op_data.drone_atk_e0) < 2: slot = 0
			self.drone_atk_interval = op_data.drone_atk_interval[slot]
			self.drone_atk = op_data.drone_atk_e0[slot][0] + (op_data.drone_atk_e0[slot][1]-op_data.drone_atk_e0[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)
			if elite == 1: self.drone_atk = op_data.drone_atk_e1[slot][0] + (op_data.drone_atk_e1[slot][1]-op_data.drone_atk_e1[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)
			if elite == 2: self.drone_atk = op_data.drone_atk_e2[slot][0] + (op_data.drone_atk_e2[slot][1]-op_data.drone_atk_e2[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)

		
		
		############### Buffs
		self.buff_name = "" #needed to put the conditionals before the buffs
		self.atk = self.atk * params.base_buffs[0] + params.base_buffs[1]
		if params.base_buffs[0] > 1: self.buff_name += f" bAtk+{int(100*(params.base_buffs[0]-1))}%"
		elif params.base_buffs[0] < 1: self.buff_name += f" bAtk{int(100*(params.base_buffs[0]-1))}%"
		if params.base_buffs[1] > 1: self.buff_name += f" bAtk+{params.base_buffs[1]}"
		elif params.base_buffs[1] < 1: self.buff_name += f" bAtk{params.base_buffs[1]}"

		self.buff_atk = params.buffs[0]
		if self.buff_atk > 0: self.buff_name += f" atk+{int(100*self.buff_atk)}%"
		elif self.buff_atk < 0: self.buff_name += f" atk{int(100*self.buff_atk)}%"
		
		self.attack_speed += params.buffs[2]
		if params.buffs[2] > 0: self.buff_name += f" aspd+{params.buffs[2]}"
		elif params.buffs[2] < 0: self.buff_name += f" aspd{params.buffs[2]}"

		self.buff_atk_flat = params.buffs[1]
		if self.buff_atk_flat > 0: self.buff_name += f" atk+{int(100*self.buff_atk_flat)}"
		elif self.buff_atk_flat < 0: self.buff_name += f" atk{int(100*self.buff_atk_flat)}"

		self.buff_fragile = params.buffs[3]
		if self.buff_fragile > 0: self.buff_name += f" dmg+{int(100*self.buff_fragile)}%"
		elif self.buff_fragile < 0: self.buff_name += f" dmg{int(100*self.buff_fragile)}%"

		#TODO
		#third module
		#muelsyse
		#skill = 0
		
		#TODO:remove this when all operators are changed to the new format. this is needed for base buffs
		self.base_atk = 0

	def normal_attack(self,defense,res, extra_buffs = [0,0,0], hits = 1, aoe = 1):
		final_atk = self.atk * (1 + extra_buffs[0] + self.buff_atk) + extra_buffs[1] + self.buff_atk_flat
		if not self.physical:
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		else:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hits * hitdmg / self.atk_interval * (self.attack_speed + extra_buffs[2])/100 * aoe
		return dps

	def try_kwargs(self, target, keywords, **kwargs):
		keyword_found = False
		for key in keywords:
			try:
				if key in kwargs.keys():
					keyword_found = True
					break
			except:
				pass
		if keyword_found:
			match target:
				case 1: self.trait_dmg = False
				case 2: self.talent_dmg = False
				case 3: self.talent2_dmg= False
				case 4: self.skill_dmg = False
				case 5: self.module_dmg = False
		
	def skill_dps(self, defense, res):
		print("The operator has not implemented the skill_dps method")
		return -100
	
	def total_dmg(self,defense,res):
		try:
			x = self.skill_duration
		except AttributeError: #aka the operator is not on the json system yet
			return (self.skill_dps(defense,res))
		if self.skill_duration < 1:
			return (self.skill_dps(defense,res))
		else:
			return (self.skill_dps(defense,res) * self.skill_duration)
	
	def avg_dps(self,defense,res):
		try:
			x = self.skill_duration
		except AttributeError: #aka the operator is not on the json system yet
			return (self.skill_dps(defense,res))
		if self.skill_duration < 1:
			return (self.skill_dps(defense,res))
		else:
			damage = (self.total_dmg(defense,res) + self.normal_attack(defense,res) * self.skill_cost/(1+self.sp_boost))/(self.skill_duration+self.skill_cost/(1+self.sp_boost))
			return damage
	
	def get_name(self):
		return self.name


class NewBlueprint(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("NewBlueprint",pp,[1,2,3],[2,1],3,1,1) #available skills, available modules, default skill, def pot, def mod

		if self.trait_dmg or self.talent_dmg or self.talent2_dmg: self.name += " withBonus"
		if self.skill == 3 and self.skill_dmg: self.name += " overcharged"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = 0
		aspd = 0
		atk_scale = 1

		atkbuff += self.talent1_params[0]
		aspd += self.talent2_params[0]
		if self.module == 1 and self.module_dmg: atk_scale = 1.1
		
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps


class twelveF(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("12F",pp,[],[],0,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if pp.pot > 2: self.atk += 12
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg= np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100 * self.targets
		return dps

class Aak(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Aak",pp,[1,3],[1],1,1,1)
	
	def skill_dps(self, defense, res):
		cdmg = max(self.talent1_params)
		crate = 0.25
		if self.module == 1 and self.module_lvl > 1:
			crate = 0.25 + 0.75 * 0.2 if self.module_lvl == 2 else 0.25 + 0.75 * 0.3

		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 3:
			aspd = self.skill_params[1]
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		print(aspd, final_atk)
		avghit = (1-crate)*hitdmg + crate * critdmg
		dps = avghit/self.atk_interval * (self.attack_speed + aspd)/100
		return dps

class Absinthe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Absinthe",pp,[1,2],[1],2,6,1)
		if self.skill == 2 and self.module == 1 and self.module_lvl > 1: self.talent_dmg = True
		if self.talent_dmg: self.name += " lowHpTarget"
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 1
		newres = np.fmax(0,res-10) if self.module == 1 else res
		if self.skill == 1:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05) * dmg_scale	
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			atk_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05) * dmg_scale	
			dps = 4 * hitdmgarts/self.atk_interval * self.attack_speed/100
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 1: return(self.skill_dps(defense,res))
		else:
			return(self.skill_dps(defense,res) * (27 + self.mastery))

class Aciddrop(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Aciddrop",pp,[1,2],[1],2,6,1)
		if self.talent_dmg and self.elite > 0: self.name += " directFront"

	def skill_dps(self, defense, res):
		if self.elite == 0:
			mindmg = 0.05
		elif self.talent_dmg:
			mindmg = self.talent1_params[1]
		else:
			mindmg = self.talent1_params[0]

		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * mindmg)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * mindmg)
			dps = 2 * hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Adnachiel(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Adnachiel",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0]
		final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps

class Amiya(Operator):
	def __init__(self, pp, *args,**kwargs):
		super().__init__("Amiya", pp, [1,2,3],[2],3,6,2)
		if self.elite == 2 and (pp.skill == 3 or pp.skill == -1):
			self.name = self.name.replace("S2","S3")
			self.skill = 3
			self.params = [0,1,1.1,1.2,1.3,1.4,1.5,1.6,1.8,2,2.3][pp.mastery]
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/((self.attack_speed +aspd)/100))
		if self.skill == 2:
			atk_scale = self.skill_params[0]
			hits = self.skill_params[1]		
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hits * hitdmgarts/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk + self.params) + self.buff_atk_flat
			dps = final_atk/(self.atk_interval/(self.attack_speed/100)) * np.fmax(1,-defense) #this defense part has to be included, because np array
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3: return(self.skill_dps(defense,res) * 30)
		else:
			return(self.skill_dps(defense,res))
	
class AmiyaGuard(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("AmiyaGuard",pp,[1,2],[],1,6,0)
		if self.skill == 2:
			if self.skill_dmg: self.name += " 3kills"
			else: self.name += " no kills"
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + 2 * self.talent1_params[0]) + self.buff_atk_flat
			nukedmg = final_atk * 9 * skill_scale * (1+self.buff_fragile)
			truedmg = final_atk * 2 * skill_scale * (1+self.buff_fragile)
			self.name += f"  Nuke:{int(nukedmg)}Arts+{int(truedmg)}True"
	
	def skill_dps(self, defense, res):
		atkbuff = 2 * self.talent1_params[0]
		
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05)
			dps = 2 * hitdmgarts/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			if self.skill_dmg:
				atkbuff += 3 * self.skill_params[3]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			dps = final_atk/self.atk_interval * self.attack_speed/100 * np.fmax(1,-defense) #this defense part has to be included
		return dps

class AmiyaMedic(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("AmiyaMedic",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2 and self.skill_dmg: self.name += " maxStacks"
		if self.skill == 2 and not self.skill_dmg: self.name += " noStacks"
		if self.skill == 2:
			extra_atk = 5 * self.skill_params[1] if self.skill_dmg else 0
			final_atk = self.atk * (1 + self.buff_atk + extra_atk) + self.buff_atk_flat
			damage = final_atk * self.skill_params[0]
			self.name += f" initialHit:{int(damage)}"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		if self.skill == 2:
			atkbuff = 5 * self.skill_params[1] if self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk)
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100 * min(self.targets,2)
		return dps

class Andreana(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Andreana",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " atMaxRange"
			
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + self.talent1_params[0])/100
		return dps

class Angelina(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Angelina", pp, [1,2,3], [2,1],3,1,1)
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0]
		if self.module == 1:
			if self.module_lvl == 2: aspd += 3
			if self.module_lvl == 3: aspd += 5

		####the actual skills
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/ 100
		if self.skill == 2:
			atk_interval = self.atk_interval * 0.15
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg / atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 3:
			targets = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/ 100 * min(self.targets, targets)
		return dps

class Aosta(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Aosta",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " distant"
		if self.elite > 0 and not self.talent_dmg: self.name += " blockedTarget"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = 1.5 if self.trait_dmg else 1
		if self.trait_dmg and self.module == 1: atk_scale = 1.6
		talent_scale = self.talent1_params[0] if self.elite > 0 and self.talent_dmg else 0
		talent_duration = self.talent1_params[1]
		if self.skill == 1:
			final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + self.skill_params[1]) / 100 * self.targets
		if self.skill == 2:
			self.atk_interval = 3.45
			final_atk = self.atk * (1 + self.skill_params[1] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100 * self.targets
			talent_scale *= 2
		active_ratio = min(1, talent_duration/ (self.atk_interval / self.attack_speed * 100))
		arts_dps = np.fmax(final_atk * talent_scale * (1-res/100), final_atk * talent_scale * 0.05) * active_ratio * self.targets
		dps += arts_dps
		return dps

class April(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("April", pp, [1,2],[2],2,1,2)
		if self.module_dmg and self.module == 2: self.name += " groundEnemies"		
	
	def skill_dps(self, defense, res):
		aspd = 8 if self.module == 2 and self.module_dmg else 0
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * self.skill_params[0] - defense, final_atk * self.skill_params[0] * 0.05)
			avgdmg = (self.skill_cost * hitdmg + skilldmg) / (self.skill_cost + 1)
			dps = avgdmg / self.atk_interval * (self.attack_speed+aspd)/100
		
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Archetto(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 517  #######including trust
		maxatk = 618
		self.atk_interval = 1.0  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Archetto Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Archetto P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 48
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 32
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 24
				elif self.module_lvl == 2: self.base_atk += 22
				else: self.base_atk += 17
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.module_lvl > 1 and self.talent1 and self.skill != 3: self.name += " +2ndSniper"
		
		if self.moduledmg and self.module == 1: self.name += " aerialTarget"
		if self.moduledmg and self.module == 2: self.name += " GroundEnemy"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 2:
			aspd += 1 + self.module_lvl
		if self.moduledmg:
			if self.module == 1: atk_scale = 1.1
			if self.module == 2: aspd += 8
			
		####the actual skills
		if self.skill == 1:
			recovery_interval = 2.5
			if self.module == 1:
				if self.module_lvl == 2: recovery_interval -= 0.5 if self.talent1 else 0.2
				if self.module_lvl == 3: recovery_interval -= 0.7 if self.talent1 else 0.3
			skill_scale = 2 + 0.1 * self.mastery
			skill_scale2= 1.5 + 0.1 * self.mastery
			sp_cost = 3 if self.mastery == 3 else 4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			aoedmg = np.fmax(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05)
			
			#figuring out the chance of the talent to activate during downtime
			base_cycle_time = (sp_cost+1)/(1+aspd/100)
			talents_per_base_cycle = base_cycle_time / recovery_interval
			failure_rate = 1.8 / (sp_cost + 1)  #1 over sp cost because thats the time the skill would technically be ready, the bonus is for sp lockout. (basis is a video where each attack had 14 frames, but it was 25 frames blocked)
			talents_per_base_cycle *= 1-failure_rate
			new_spcost = np.fmax(1,sp_cost - talents_per_base_cycle)
			hitdps = hitdmg/(self.atk_interval/(1+aspd/100)) * (new_spcost-1)/new_spcost
			skilldps = skilldmg/(self.atk_interval/(1+aspd/100)) /new_spcost
			aoedps = aoedmg/(self.atk_interval/(1+aspd/100)) /new_spcost *(min(self.targets,4)-1)
			dps = hitdps + skilldps + aoedps
				
		if self.skill == 2:
			recovery_interval = 2.5
			if self.module == 1:
				if self.module_lvl == 2: recovery_interval -= 0.5 if self.talent1 else 0.2
				if self.module_lvl == 3: recovery_interval -= 0.7 if self.talent1 else 0.3
			sprecovery = 1/recovery_interval + 1+aspd/100
			skill_scale = 1.4 if self.mastery == 3 else 1.2 + 0.05 * self.mastery
			sp_cost = 12 - self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			targets = min(5, self.targets)
			totalhits = [5,9,12,14,15]
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + sprecovery/sp_cost * skilldmg * totalhits[targets-1]
		
		if self.skill == 3:
			atkbuff += 0.15 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * 3
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 2)
		return dps

class Arene(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Arene",pp,[1,2],[2],2,6,2)
		if self.skill == 1 and self.talent_dmg:
			self.trait_dmg = False
		if not self.trait_dmg and self.skill == 1: self.name += " rangedAtk"
		if self.talent_dmg and self.elite > 0: self.name += " vsDrones"
		if self.module == 2 and self.targets == 1 and self.module_dmg: self.name += " +12aspd(mod)"
		if self.targets > 1: self.name += f" {self.targets}targets"
			
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg else 1
		aspd = 12 if self.module == 2 and (self.targets > 1 or self.module_dmg) else 0
		if not self.trait_dmg and self.skill != 2: atk_scale *= 0.8
			
		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1+ self.buff_atk) + self.buff_atk_flat
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			dps = 2 * hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			hitdmgarts = np.fmax(final_atk * skill_scale * atk_scale  * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100 * min(2,self.targets)
		return dps

class Asbestos(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Asbestos",pp,[1,2],[],2,1,0)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			self.atk_interval = 2.0
			final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Ascalon(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ascalon",pp,[1,2,3],[1],3,1,1)
		if not self.talent_dmg: self.name += " 1Stack"
		else: self.name += " 3Stacks"
		if self.elite == 2:
			if not self.talent2_dmg: self.name += " NoRangedTiles"
			else: self.name += " nextToRangedTile"
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		talentstacks = 3 if self.talent_dmg else 1
		talentscale = self.talent1_params[1]
		aspd = self.talent2_params[0]
		if self.elite == 2 and self.talent2_dmg: aspd += self.talent2_params[1]
		
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * 2
			sp_cost = self.skill_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed+ aspd)*100
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		if self.skill == 3:
			atk_interval = self.atk_interval + self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[1]) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/atk_interval * (self.attack_speed+aspd)/100 * self.targets
		
		dps += self.targets * final_atk * talentstacks * talentscale * np.fmax(1-res/100, 0.05)
		return dps

class Ash(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ash",pp,[1,2],[2,1],2,1,1)
		self.try_kwargs(4,["stun","nostun","stunned","vsstun","vsstunned"],**kwargs)
		if self.skill_dmg and self.skill == 2: self.name += " vsStunned"
		if self.module_dmg:
			if self.module == 1: self.name += " aerialTarget"
			if self.module == 2: self.name += " groundEnemy"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		aspd = 8 if self.module == 2 and self.module_dmg else 0

		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * 2
		if self.skill == 2:
			self.atk_interval = 0.2	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			if self.skill_dmg: atk_scale *= self.skill_params[1] 
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dmg_bonus = self.talent1_params[2] if self.module == 1 and self.module_lvl > 1 and self.skill_dmg else 1
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * dmg_bonus
		return dps

class Ashlock(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ashlock",pp,[1,2],[1],2,1,1)
		if not self.talent_dmg: self.name += " LowTalent"
		if self.module_dmg and self.module == 1: self.name += " blockedTarget"	
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe			
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.talent_dmg else self.talent1_params[0]
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
		atk_interval = self.atk_interval if self.skill != 2 else self.atk_interval * (1 + self.skill_params[1])
		dps = hitdmg / atk_interval * self.attack_speed/100 * self.targets
		return dps

class Astesia(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Astesia", pp, [1,2],[],2,1,0)
		if self.talent_dmg: self.name += " maxStacks"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0] * self.talent1_params[2] if self.talent_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2: dps *= min(self.targets, 2)
		return dps

class Astgenne(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Astgenne",pp,[1,2,],[2],2,6,2)
		if self.talent_dmg and self.elite > 0: self.name += " maxStacks"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0] * self.talent1_params[2] if self.talent_dmg and self.elite > 0 else 0
		targetscaling = [0,1,2,3,4] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3]
		if self.elite < 2: targetscaling = [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2]
		targets = min(4, self.targets)
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * targetscaling[targets]
			skill_targetscaling = [0,1,4,6,8] if self.module == 2 else [0, 1, 2 * 1.85, 2*(1.85+0.85**2), 2*(1.85+0.85**2+0.85**3)]
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * skill_targetscaling[targets]	
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[4] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval*(self.attack_speed+aspd)/100

		
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval*(self.attack_speed+aspd)/100
			if self.targets > 1:
				dps = hitdmg/self.atk_interval*(self.attack_speed+aspd)/100 * 2 * targetscaling[targets]
		return dps

class Aurora(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 802  #######including trust
		maxatk = 956
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [2] else 2###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Aurora Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Aurora P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.skilldmg = TrTaTaSkMo[3]

		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
  ##### keep the ones that apply
		if self.skilldmg: self.name += " 1/3vsFreeze"

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

			
		####the actual skills
		if self.skill == 2:
			self.atk_interval = 1.85
			atkbuff += 0.6 + 0.05 * self.mastery
			skill_scale = 3 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg =  np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgdmg = hitdmg
			if self.skilldmg: avgdmg = 2/3 * hitdmg + 1/3 * skilldmg
						
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps
		
class Bagpipe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Bagpipe",pp,[1,2,3],[1,2],3,1,1)
		if self.module_dmg and self.module == 2: self.name += " lowHpTarget"
		if self.targets > 1: self.name += f" {self.targets}targets"	
	
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		crate = self.talent1_params[1] if self.elite > 0 else 0
		cdmg = self.talent1_params[0] if self.elite > 0 else 1

		if self.skill == 1:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale *cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * (self.attack_speed + aspd)/100
		
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale *cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			skillhit = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			skillcrit = np.fmax(final_atk * atk_scale * skill_scale *cdmg - defense, final_atk * atk_scale * skill_scale * cdmg * 0.05)
			
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			avgskill = crate * skillcrit * min(2, self.targets) + (1-crate) * skillhit
			avgskill *= 2
			sp_cost = self.skill_cost / (1 + self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = avgskill
			
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avghit = (avgskill + (atks_per_skillactivation - 1) * avgdmg) / atks_per_skillactivation
				else:
					avghit = (avgskill + int(atks_per_skillactivation) * avgdmg) / (int(atks_per_skillactivation)+1)
			
			dps = avghit/self.atk_interval * self.attack_speed/100
		
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			self.atk_interval = 1.7
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale *cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			dps = 3 * avgdmg/self.atk_interval * self.attack_speed/100
		return dps
	
class Beehunter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 475  #######including trust
		maxatk = 573
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Beehunter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Beehunter P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " maxStacks"
		if self.module == 1:
			if self.moduledmg: self.name += " >50% hp"				
			else: self.name += " <50% hp"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg:
			aspd += 10
		
		atk = 0.06 if self.pot > 4 else 0.05
		if self.module == 1: atk += 0.01 * (self.module_lvl -1)
		atkbuff += 5 * atk if self.talent1 else atk
		
		
		####the actual skills
		if self.skill == 2:
			self.atk_interval = 0.351 if self.mastery == 0 else 0.312
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Bibeak(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Bibeak",pp,[1,2],[1],1,6,1)
		if self.elite > 0 and not self.talent_dmg: self.name += " w/o talent"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0] * self.talent1_params[1] if self.talent_dmg else 0
		atkbuff = 0.01 * (self.module_lvl-1) * self.talent1_params[1] if self.talent_dmg and self.module == 1 and self.module_lvl > 1 else 0
		dmg_multiplier = 1.1 if self.module == 1 else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * dmg_multiplier
			skillartsdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_multiplier
			sp_cost = self.skill_cost
			avg_phys = 2 * (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avg_arts = 0 if self.targets == 1 else skillartsdmg / (sp_cost +1)
			dps = (avg_phys+avg_arts)/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2:
			skill_scale = self.skill_params[2]
			skillartsdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_multiplier
			avg_hit = (2 * hitdmg * self.skill_cost + skillartsdmg * min(self.targets, self.skill_params[0])) / self.skill_cost
			dps = avg_hit/self.atk_interval * (self.attack_speed + aspd)/100
		return dps
	
class Blaze(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Blaze", pp, [1,2],[1],2,1,1)
		if self.elite == 2 and not self.talent2_dmg and not self.skill == 2: self.name += " w/o talent2"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		aspd = 0
		atk_scale = 1.1 if self.module_dmg and self.module == 1 else 1
		targets = 3 if self.elite == 2 else 2
		if (self.talent2_dmg or self.skill == 2) and self.module == 1 and self.module_lvl > 1: #talent buff is active when s2 gets activated
			atkbuff = self.talent2_params[0]
			aspd =  self.talent2_params[1]
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) * min(self.targets, targets)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * min(self.targets,targets)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Blemishine(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Blemishine",pp,[1,2,3],[2,1],3,1,1)
		if self.elite > 0:
			if self.talent2_dmg: self.name += " vsSleep"
			else: self.name += " w/o sleep"
		if self.skill == 1 and self.sp_boost > 0: self.name += f" +{self.sp_boost}SP/s"
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		atk_scale = self.talent2_params[0] if self.talent2_dmg else 1
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)					
			dps = avghit / self.atk_interval * self.attack_speed / 100
			
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			artsdmg = np.fmax(final_atk * atk_scale * self.skill_params[2] * (1-res/100), final_atk * atk_scale * self.skill_params[2] * 0.05)
			dps = (hitdmg + artsdmg) / self.atk_interval * self.attack_speed / 100
		return dps

class Blitz(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Blitz",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 1 and self.talent_dmg: self.name += " vsStun"
	
	def skill_dps(self, defense, res):
		atk_scale = 1 if self.skill == 1 and not self.talent_dmg else self.talent1_params[0]
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			atk_scale -= 1
			atk_scale *= self.skill_params[3]
			atk_scale += 1
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + 200) / 100
		return dps

class BluePoison(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("BluePoison", pp, [1,2], [2], 1 ,1 ,2)
		if self.module_dmg and self.module == 2: self.name += " GroundTargets"
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		aspd = 8 if self.module_dmg and self.module == 2 else 0
		artsdmg = self.talent1_params[1]
		artsdps = np.fmax(artsdmg * (1 - res/100), artsdmg * 0.05) if self.elite > 0 else 0
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg * min(2,self.targets)) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/((self.attack_speed + aspd)/100)) + artsdps * min(2,self.targets)
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = self.skill_params[1] * hitdmg/(self.atk_interval/((self.attack_speed+ aspd)/100)) + hitdmg/(self.atk_interval/((self.attack_speed+ aspd)/100)) * min(2,self.targets-1) + artsdps * min(3, self.targets)
		return dps
		
class Broca(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 659  #######including trust
		maxatk = 842
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Broca Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Broca P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 42
				else: self.base_atk += 30
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		##### keep the ones that apply
		if self.talent1: self.name += " blocking2+"
		if self.module == 1 and self.moduledmg: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.02
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.03
				if self.module_lvl == 3: atkbuff += 0.05

		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = np.fmax(final_atk *atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) *min(3, self.targets)
		
		if self.skill == 2:
			self.atk_interval = 1.98
			atkbuff += 1.4 + 0.2 * self.mastery
			if self.mastery > 1: atkbuff -= 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = np.fmax(final_atk * atk_scale *(1-res/100), final_atk* atk_scale * 0.05)
			
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(3,self.targets)
		return dps

class Bryophyta(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Bryophyta",pp,[1,2],[1],2,6,1)
		if not self.trait_dmg: self.name += " blocking" 

	def skill_dps(self, defense, res):
		atk_scale = 1
		if self.trait_dmg: 
			atk_scale = 1.3 if self.module == 1 else 1.2

		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Cantabile(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Cantabile",pp,[1,2],[],2,1,0)
		if self.elite > 0:
			if self.talent_dmg: self.name += " melee"
			else: self.name += " ranged"
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.talent_dmg else 0
		aspd = self.talent1_params[0] if not self.talent_dmg else 0
		final_atk = self.atk * (1 + atkbuff + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd + self.skill_params[1])/100
		return dps

class Caper(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 557  #######including trust
		maxatk = 665
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Caper Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Caper P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		

		
		if not self.trait: self.name += " maxRange"
		else: self.name += " minRange"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		crate = 0.25
		cdmg = 1.6 if self.pot > 4 else 1.5
			
		####the actual skills
		
		
		if self.skill == 1:
			skill_scale = 2 + 0.1 * self.mastery
			if self.mastery == 3: skill_scale += 0.05
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * cdmg* atk_scale - defense, final_atk * cdmg * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skillcritdmg = np.fmax(final_atk * cdmg* atk_scale *skill_scale - defense, final_atk* cdmg* atk_scale * skill_scale * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			skillhitdmg = skillcritdmg * crate + (1-crate) * skillhitdmg
			sp_cost = 3 if self.mastery == 3 else 4
			
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			
			interval = 20/13.6 if not self.trait else (self.atk_interval/(1+aspd/100))
			dps = avgphys/interval
		
		if self.skill == 2:
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			
			interval = 20/13.6 if not self.trait else (self.atk_interval/(1+aspd/100))
			dps = 2* hitdmg/interval
		return dps

class Carnelian(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 807  #######including trust
		maxatk = 926
		self.atk_interval = 2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Carnelian Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Carnelian P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 76
				else: self.base_atk += 66
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 95
				elif self.module_lvl == 2: self.base_atk += 85
				else: self.base_atk += 65
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skilldmg and self.skill != 1: self.name += " charged"
		if self.skill == 3: self.name += " (averaged)"
		
		if self.moduledmg and self.module == 2: self.name += " manyTargets"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 2 and self.moduledmg: atk_scale = 1.15
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			self.atk_interval = 0.9 if self.mastery == 3 else 1.2
			if self.skilldmg: atkbuff += 0.2 if self.mastery > 1 else 0.15

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			maxatkbuff = 2.8 if self.mastery == 3 else 2 + 0.2 * self.mastery
			duration = 21
			totalatks = 1 + int(duration / (self.atk_interval/(1+aspd/100))) # +1 because the first attack is already at 0
			totalduration = totalatks * (self.atk_interval/(1+aspd/100))
			damage = 0
			bonusscaling = 5 if self.skilldmg else 0
			for i in range(totalatks):
				final_atk = self.base_atk * (1+atkbuff + i * (self.atk_interval/(1+aspd/100)) /21 * maxatkbuff) + self.buffs[1]
				damage += np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05) * (1+ min(bonusscaling,i) * 0.2)
				
			dps = damage/totalduration * self.targets
		return dps

class Castle3(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Castle3",pp,[],[],0,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg: self.name += f" first{int(self.talent1_params[0])}s"
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.talent_dmg else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class Catapult(Operator):
	def __init__(self, pp, *args ,**kwargs):
		super().__init__("Catapult",pp,[1],[],1,6,0)
		if self.targets > 1: self.name += f" {self.targets}targets"
		
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Ceobe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ceobe",pp,[1,2,3],[1,2],2,1,1)
		if self.module == 1 and self.module_lvl > 1:
			if self.talent_dmg: self.name += " maxTalent1"
			else: self.name += " minTalent1"
		if not self.talent2_dmg and self.elite == 2: self.name += " adjacentAlly"	
		if self.module == 2 and self.skill == 1:
			if self.module_dmg: self.name += " vsElite"
	
	def skill_dps(self, defense, res):
		newres= np.fmax(0, res-10) if self.module == 1 else res
		bonus_arts_scaling = self.talent1_params[0] if self.elite > 0 else 0
		if self.module == 1 and self.module_lvl > 1 and self.talent_dmg: bonus_arts_scaling = self.talent1_params[2]
		atkbuff = self.talent2_params[0] if self.elite == 2 and self.talent2_dmg else 0
		aspd = self.talent2_params[1] if self.elite == 2 and self.talent2_dmg else 0

		if self.skill == 1:
			sp_cost = self.skill_cost
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * skill_scale *(1-newres/100), final_atk * skill_scale * 0.05)
			defbonusdmg = np.fmax(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed+aspd)*100
			if self.module == 2 and self.module_dmg:
				sp_cost = sp_cost / (1 + 1/atkcycle + self.sp_boost) + 1.2 #bonus sp recovery vs elite mobs + sp lockout
			else:
				sp_cost = sp_cost /(1 + self.sp_boost) + 1.2 #sp lockout
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmgarts + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation
				else:
					avghit = (skilldmgarts + int(atks_per_skillactivation) * hitdmgarts) / (int(atks_per_skillactivation)+1)
			dps = (avghit+defbonusdmg)/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atk_interval = self.atk_interval * self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			defbonusdmg = np.fmax(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			dps = (hitdmgarts + defbonusdmg)/atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			defbonusdmg = np.fmax(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			dps = (hitdmg + defbonusdmg)/self.atk_interval * (self.attack_speed+aspd)/100
		return dps
	
class Chen(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 519  #######including trust
		maxatk = 660
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Chen Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Chen P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 52
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if self.skill == 2: self.name += " DmgPerHit"
		if self.skill == 3: self.name += " totalDMG"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		dmg = 1.1 if self.module == 1 else 1
		atkbuff += 0.05 if self.pot < 5 else 0.06
		newdef = defense
		if self.module == 2:
			newdef = np.fmax(0, defense -70)
			if self.module_lvl == 2: atkbuff += 0.06
			if self.module_lvl == 3: atkbuff += 0.1
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4
			atk_scale = 1
			aspd += 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			skill_scale = 4.1 + 0.3 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * skill_scale -newdef, final_atk * skill_scale * 0.05) * dmg
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg
			dps = hitdmg + hitdmgarts
			
		if self.skill == 3:
			skill_scale = 2.6 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * skill_scale - newdef, final_atk *skill_scale * 0.05) * dmg
			dps = 10 * hitdmg
		return dps

class ChenAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ChenAlter",pp,[1,3],[1],3,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.skill_params[0]
		aspd = 8 if self.elite == 2 else 0 #im not going to include the water buff for now
		atk_scale = 1.6 if self.module == 1 else 1.5
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		if self.skill == 3:
			def_shred = self.skill_params[2] * (-1)
			if self.shreds[0] < 1 and self.shreds[0] > 0:
				defense = defense / self.shreds[0]
			newdefense = np.fmax(0, defense- def_shred)
			if self.shreds[0] < 1 and self.shreds[0] > 0:
				newdefense *= self.shreds[0]
			hitdmg = np.fmax(final_atk * atk_scale - newdefense, final_atk* atk_scale * 0.05)
			
			dps = 2 * hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		return dps
	
	def total_dmg(self, defense, res):
		ammo = 16
		saverate = 0.22 if self.pot > 4 else 0.2
		if self.module == 1:
			if self.module_lvl == 2: saverate += 0.03
			if self.module_lvl == 3: saverate += 0.05
		ammo = ammo / (1-saverate)
		dmg = self.skill_dps(defense,res) * ammo * (self.atk_interval/(1+self.buffs[2]/100))
		return dmg	

class Chongyue(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 537  #######including trust
		maxatk = 650
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Chongyue Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Chongyue P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)


		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 25
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.talent2: self.name += " 1KillPerSkill"
			
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		crate = 0.23
		cdmg = 1.65
		if self.pot > 4:
			crate = 0.25
			cdmg = 1.7
			
		#self.talent2 = False
		if self.skill == 3:
			atk_scale = 2.9 + 0.3 * self.mastery
			if self.mastery == 0 : atk_scale += 0.1

			normalhits = 4
			if self.talent2:
				if self.module == 1 and self.module_lvl > 1:
					normalhits = 2
				else:
					normalhits = 3
			
			#THIS ACTUALLY NEEDS A REWORK
			#but the crate is around 80% anyway, so im not motivated enough to change it, but talent 2 active should somewhat reduce the crit rate, since you get more skill hits
			#and skill hits cant activate the talent, but honestly. f this.
			skillcrate = 1-(1-crate)**6 if aspd < 26 else 1-(1-crate)**8
			normalcrate = (3*(1-(1-crate)**6)+ 1-(1-crate)**8)/4 if aspd < 26 else 1-(1-crate)**8
			if False:
				atk_cycle = self.atk_interval/(1+aspd/100)
				relevant_hits = int(2.5 / atk_cycle)
				
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			normalhit = np.fmax(final_atk-defense, final_atk*0.05)
			normalcrit = normalhit * cdmg
			skillhit = np.fmax(final_atk*atk_scale-defense, final_atk*atk_scale*0.05)
			skillcrit = skillhit * cdmg
			avgnormal = normalcrit*normalcrate+normalhit*(1-normalcrate)
			avgskill = (skillcrit*skillcrate+skillhit*(1-skillcrate)) * self.targets
			avgdmg = (2 * avgnormal * normalhits + 2 * avgskill)/(normalhits +1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class CivilightEterna(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("CivilightEterna",pp,[1,2],[1],2,6,1)
		if self.module == 1 and not self.module_dmg: self.name += " noModBonus"

	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		if self.skill == 2:
			skill_scale = self.skill_params[3]
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale)
			dps = hitdmg / 7 * 6
		else: dps = res * 0
		return dps

class Click(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 324  #######including trust
		maxatk = 375
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Click Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Click P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 18
				elif self.module_lvl == 2: self.base_atk += 15
				else: self.base_atk += 13
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.trait: self.name += " minDroneDmg"
		
		self.buffs = buffs		
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		if self.pot > 3: aspd +=6
		aspd += 12
		
		drone_dmg = 1.2 if self.module == 2 else 1.1
		
		if self.module == 2: 
			if self.module_lvl == 2:aspd += 3
			if self.module_lvl == 3:aspd += 6 

		if not self.trait:
			drone_dmg = 0.2
		
		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
		else:
			atkbuff += 0.58 + 0.04 * self.mastery

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		drone_atk = drone_dmg * final_atk
		
		dmgperinterval = final_atk + drone_atk
		
		hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps

class Coldshot(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 909  #######including trust
		maxatk = 1063
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Coldshot Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Coldshot P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 53
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait: self.name += " outOfAmmo"
		else: self.name += " w/o TalentBonus" 
		#if self.trait and self.talent1: self.name += " withTalentBonusDmg!"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		final_atk = 0
		#talent/module buffs
		if not self.trait:
			atk_scale = 1.3 if self.pot < 5 else 1.33
			if self.module == 1:
				if self.module_lvl == 2: atk_scale += 0.05
				if self.module_lvl == 3: atk_scale += 0.08
		atk_scale *= 1.2 #traitbonus
		atk_scale2 = 1.2
		
		####the actual skills
		if self.skill == 1:
			atkbuff += 1 if self.mastery == 3 else 0.6 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.trait:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))
			elif self.module == 1:
				hitdmg2 = np.fmax(final_atk * atk_scale2 - defense, final_atk * atk_scale2 * 0.05)
				dps = (hitdmg+hitdmg2)/(2*(self.atk_interval/(1+aspd/100))+1.6)
			else:
				dps = hitdmg/((self.atk_interval/(1+aspd/100))+1.6)
		
		if self.skill == 2:
			atkbuff += 1 + 0.15 * self.mastery
			if self.mastery > 1: atkbuff -= 0.05
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.trait:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))
			elif self.module == 1:
				hitdmg2 = np.fmax(final_atk * atk_scale2 - defense, final_atk * atk_scale2 * 0.05)
				dps = (hitdmg+hitdmg2)/(2*(self.atk_interval/(1+aspd/100))+1.6)
			else:
				dps = hitdmg/((self.atk_interval/(1+aspd/100))+2.4)
		return dps

class Conviction(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 793  #######including trust
		maxatk = 951
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Conviction Lv{level} S{self.skill}" #####set op name
		else: self.name = f"Conviction S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " vsBlocked"
		if self.skill == 2 and self.skilldmg: self.name += " SkillSuccess"
		if self.skill == 2 and not self.skilldmg: self.name += " selfstun"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1:
			if self.moduledmg: atk_scale = 1.15
			aspd += 3 if self.module_lvl == 1 else 4
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.7 + 0.1 * self.mastery
			skill_scale2 = 6.8 + 0.4 * self.mastery
			sp_cost = 4 if self.mastery == 3 else 5
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg1 = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skilldmg2 = np.fmax(final_atk * atk_scale * skill_scale2 - defense, final_atk* atk_scale * skill_scale2 * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg1 * 0.95 + skilldmg2 * 0.05
			if atks_per_skillactivation > 1:
				avghit = (0.95 * skilldmg1 + 0.05 * skilldmg2 + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
				
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			skill_scale = 2.6 + 0.3 * self.mastery
			sp_cost = 12 if self.mastery == 3 else 17 - self.mastery
			sp_cost += 1.2 #sp lockout
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05) * self.targets
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.skilldmg: 
				dps += skilldmg / sp_cost
			else:
				dps *= (sp_cost -5)/sp_cost
		return dps

class Dagda(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 504  #######including trust
		maxatk = 614
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 4: self.base_atk += 24
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Dagda Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Dagda P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " maxStacks"
		else: self.name += " noStacks"
		if self.moduledmg and self.module == 1: self.name += " >50%hp"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		crate = 0.3
		cdmg = 1.5
		if self.module == 1: 
			cdmg += 0.06 * (self.module_lvl -1)
			if self.moduledmg: aspd += 10
		if self.talent1: cdmg = 2.4
			
		####the actual skills
		if self.skill == 2:

			crate = 0.6 if self.mastery else 0.5 + 0.03 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Degenbrecher(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 545  #######including trust
		maxatk = 685
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Degenbrecher Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Degenbrecher P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 44
				else: self.base_atk += 35
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 3: self.name += " totalDMG"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		newdef = defense * 0.7 if self.pot > 4 else defense * 0.75
		dmg = 1.1 if self.module == 1 else 1
		atk_scale = 1.6
		if self.pot > 2: atk_scale += 0.05
		if self.module == 1:
			atk_scale += 0.05 * (self.module_lvl -1)
			
		####the actual skills
		if self.skill == 3:
			skill_scale = 2.35 if self.mastery == 3 else 2 + 0.1 * self.mastery
			last_scale = 3 + 0.1 * self.mastery 
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg1 = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05) * dmg
			hitdmg2 = np.fmax(final_atk * atk_scale * last_scale - newdef, final_atk * atk_scale * last_scale * 0.05) * dmg
			
			dps = (10 * hitdmg1 + hitdmg2) * min(self.targets,6)
		return dps

class Diamante(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Diamante",pp,[1,2],[],2,1,0) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2:
			if self.talent_dmg and self.skill_dmg: self.name += " vsFallout(800dpsNotIncluded)"
			else: self.name += " noNecrosis"
			if self.targets > 1: self.name += f" {self.targets}targets"
		else:
			if not self.trait_dmg: self.name += " noNecrosis"
			elif not self.talent_dmg and not self.skill_dmg: self.name += " avgNecrosis(vsBoss)"
			elif self.talent_dmg ^ self.skill_dmg: self.name += " avgNecrosis(nonBoss)"
			else: self.name += " vsFallout(800dpsNotIncluded)"
	
	def skill_dps(self, defense, res):
		if self.skill == 2:
			atkbuff = self.talent1_params[0] if self.talent_dmg and self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			skill_scale = self.skill_params[1] if self.talent_dmg and self.skill_dmg else 0
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			eledmg =  np.fmax(final_atk * 0 * (1-res/100), final_atk * skill_scale)
			dps = (hitdmg+eledmg) / self.atk_interval * (self.attack_speed + self.skill_params[0]) / 100 * min(self.targets,2)
		
		if self.skill == 1:
			atkbuff = self.skill_params[0]
			ele_application = self.skill_params[1]
			skill_scale = self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			atkbuff += self.talent1_params[0]
			final_atk_necro = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			elemental_health = 2000 if not self.talent_dmg and not self.skill_dmg else 1000
			time_to_apply_necrosis = elemental_health / (final_atk * ele_application / self.atk_interval * (self.attack_speed) / 100)
			fallout_dps = 12000 / (time_to_apply_necrosis + 15)

			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmg_necro = np.fmax(final_atk_necro * (1-res/100), final_atk_necro * 0.05)
			eledmg_necro =  np.fmax(final_atk_necro * 0 * (1-res/100), final_atk_necro * skill_scale)
			avg_hitdmg = hitdmg * time_to_apply_necrosis / (time_to_apply_necrosis + 15) + hitdmg_necro * 15 / (time_to_apply_necrosis + 15)
			avg_eledmg = eledmg_necro * 15 / (time_to_apply_necrosis + 15)

			if not self.trait_dmg: dps = (hitdmg) / self.atk_interval * (self.attack_speed) / 100
			elif not self.talent_dmg and not self.skill_dmg: dps = fallout_dps + (avg_hitdmg + avg_eledmg) / self.atk_interval * (self.attack_speed) / 100
			elif self.talent_dmg ^ self.skill_dmg: dps = fallout_dps + (avg_hitdmg + avg_eledmg) / self.atk_interval * (self.attack_speed) / 100
			else: dps = (hitdmg_necro + eledmg_necro) / self.atk_interval * (self.attack_speed) / 100

		return dps

class Dobermann(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Dobermann",pp,[1,2],[2],2,6,2)
		if not self.trait_dmg: self.name += " blocking"
		if self.module == 2 and self.module_lvl > 1 and self.talent_dmg: self.name += " +3star"
			
	def skill_dps(self, defense, res):
		aspd = 0
		if self.module == 2 and self.talent_dmg and self.module_lvl > 1: aspd = 5 * self.module_lvl
		atk_scale = 1.2 if self.trait_dmg else 1

		if self.skill == 1:
			skill_scale = self.skill_params[0]			
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Doc(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Doc",pp,[1],[2],1,1,2)
		if not self.trait_dmg: self.name += " blocking"

	def skill_dps(self, defense, res):
		atk_scale = 1.2 if self.trait_dmg else 1
		newdef = np.fmax(0, defense-self.talent1_params[1])
		atk_interval = self.atk_interval + self.skill_params[3]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
		dps = hitdmg/atk_interval * self.attack_speed/100
		return dps

class Dorothy(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 556  #######including trust
		maxatk = 661
		self.atk_interval = 0.85   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Dorothy Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Dorothy P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3] and self.trait
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 57
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 42
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait: self.name += " noMines"   ##### keep the ones that apply
		else:
			if not self.talent1: self.name += " 1MinePerSPcost"
			else: self.name += " 1MinePer5s"
			if self.skill == 1 and self.skilldmg: " withDefshredNormalAtks"
		
		if self.talent2: self.name += " maxTalent2"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 0.2 if self.pot < 5 else 0.24
			if self.module == 2:
				if self.module_lvl == 2: atkbuff += 0.1 if self.pot < 5 else 0.12
				if self.module_lvl == 3: atkbuff += 0.2 if self.pot < 5 else 0.24
		cdmg = 1.2 if self.module == 2 else 1
		sp_cost = 12 if self.mastery == 3 else 16 - self.mastery
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
		####the actual skills
		if self.skill == 1:
			
			mine_scale = 3.7 if self.mastery == 0 else 3.6 + 0.3 * self.mastery
			defshred = 0.3 + 0.02 * self.mastery
			if self.mastery > 1: defshred -= 0.01
			defshred = 1 - defshred
			hitdmgmine = np.fmax(final_atk * mine_scale - defense * defshred, final_atk * mine_scale * 0.05) * cdmg
			minedps = 0
			if self.trait: 
				minedps = hitdmgmine/5 if self.talent1 else hitdmgmine/sp_cost
				
			if not self.trait:
				defshred = 1
			elif not self.skilldmg:
				defshred = 1
			elif not self.talent1:
				defshred = 1- defshred
				defshred *= 5 / sp_cost  #include uptime of the debuff for auto attacks
				defshred = 1- defshred
			hitdmg = np.fmax(final_atk - defense * defshred, final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		
		
		if self.skill == 2:
			mine_scale = 3 if self.mastery == 3 else 2.6 + 0.1 * self.mastery
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgmine = np.fmax(final_atk * mine_scale - defense, final_atk * mine_scale * 0.05) * cdmg
			minedps = 0
			if self.trait: minedps = hitdmgmine/5 if self.talent1 else hitdmgmine/sp_cost
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		if self.skill == 3:
			mine_scale = 3.5 if self.mastery == 3 else 2.8 + 0.2 * self.mastery
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgmine = np.fmax(final_atk * mine_scale * (1-res/100), final_atk * mine_scale * 0.05) * cdmg
			minedps = 0
			if self.trait: minedps = hitdmgmine/5 if self.talent1 else hitdmgmine/sp_cost
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		return dps

class Durin(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Durin",pp,[],[],0,6,0)
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Durnar(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Durnar",pp,[1,2],[],2,6,0)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk + self.talent1_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2: dps *= min(self.targets,3)
		return dps

class Dusk(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 881  #######including trust
		maxatk = 1028
		self.atk_interval = 2.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Dusk Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Dusk P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 55
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 82
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 51
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		stacks = 18 if self.pot > 4 else 15
		if self.module == 1:
			if self.module_lvl == 2: stacks += 5
			if self.module_lvl == 3: stacks += 6
		if self.talent1: self.name += f" {stacks}stacks"
		self.stacks = stacks
		if self.talent2: self.name += " +Freeling"
		if self.skill == 2 and self.skilldmg: self.name += " vsLowHp"		
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		freeling_atk = 398
		freeling_interval = 1.9
		#talent/module buffs
		
		if self.module == 2:
			if self.module_lvl == 2: freeling_atk += 15
			if self.module_lvl == 3: freeling_atk += 25
		
		freedps = 0
		if self.talent2:
			final_freeling = freeling_atk * (1+atkbuff) + self.buffs[1]
			freehit = np.fmax(final_freeling - defense, final_freeling * 0.05)
			freedps = freehit/(freeling_interval/(1+aspd/100))
		
		if self.module == 2: aspd += 4 + self.module_lvl
		
		if self.talent1:
			atkbuff += 0.02 * self.stacks
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.1 if self.mastery == 0 else 2.05 + 0.15 * self.mastery
			sp_cost = 5 if self.mastery == 3 else 6
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
								
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			atkbuff += 0.4 + 0.05 * self.mastery
			if self.skilldmg: atk_scale = 1.25 if self.mastery == 0 else 1.3
			aspd += 40 + 5 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			self.atk_interval = 2.9 * 1.4
			atkbuff += 1 if self.mastery == 0 else 1.05 + 0.05* self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		
		return dps+freedps

class Ebenholz(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1284  #######including trust
		maxatk = 1550
		self.atk_interval = 3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 52
		
		self.skill = skill if skill in [1,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ebenholz Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ebenholz P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2,3] else 3 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 58
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 135
				elif self.module_lvl == 2: self.base_atk += 112
				else: self.base_atk += 88
				self.name += f" ModY{self.module_lvl}"
			elif self.module == 3:
				if self.module_lvl == 3: self.base_atk += 124
				elif self.module_lvl == 2: self.base_atk += 102
				else: self.base_atk += 76
				self.name += f" Mod$\\Delta${self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1 and self.module == 2: self.moduledmg = False
		
		if self.talent1: self.name += " +Talent1Dmg"
		
		if self.module == 3 and self.talent2: self.name += " vsFallout"

		if self.moduledmg and self.module == 2: self.name += " +30aspd(mod,somehow)"
		if not self.moduledmg and self.module == 3: self.name += " vsBoss"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs	
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1:
			aspd += 2 + self.module_lvl
		
		if self.moduledmg and self.module == 2: aspd += 30
		
		if self.talent1:
			atk_scale = 1.35
			if self.module == 1:
				if self.module_lvl == 2: atk_scale += 0.05
				elif self.module_lvl == 3: atk_scale += 0.08
		
		bonus_scale = 0
		eledmg = 0
		if self.targets == 1: bonus_scale = 0.17 if self.pot > 4 else 0.15
		
		if self.module == 2 and self.module_lvl > 1:
			if self.targets == 1:
				if self.module_lvl == 2: bonus_scale += 0.03
				elif self.module_lvl == 3: bonus_scale += 0.05
			else:
				bonus_scale =  0.25 if self.module_lvl == 2 else 0.36
		
		if self.module == 3 and self.module_lvl > 1:
			if self.targets == 1:
				bonus_scale = 0.24 if self.module_lvl == 2 else 0.3
				if self.pot > 4: bonus_scale += 0.02
			if self.talent2:
				eledmg = 0.2
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 0.5 if self.mastery == 3 else 0.4 + 0.03 * self.mastery
			self.atk_interval = 3 * 0.2 if self.mastery == 0 else 3 * 0.17 
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.module == 3:
				ele_gauge = 1000 if self.moduledmg else 2000
				eledps = hitdmg * 0.08 /(self.atk_interval/(1+aspd/100))
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)
				dps += eledmg * final_atk /(self.atk_interval/(1+aspd/100))
			if self.targets == 1:
				dps += bonusdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1 and self.module == 2:
				dps += bonusdmg/(self.atk_interval/(1+aspd/100)) * (self.targets -1)
			
		if self.skill == 3:
			atkbuff += 0.5 + 0.05 * self.mastery
			if self.talent1:
				atk_scale *= 1.4 if self.mastery == 3 else 1.3 + 0.03 * self.mastery
			aspd += 60 + 10 * self.mastery
			if self.mastery > 1: aspd -= 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.module == 3:
				ele_gauge = 1000 if self.moduledmg else 2000
				eledps = hitdmg * 0.08 /(self.atk_interval/(1+aspd/100))
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)
				dps += eledmg * final_atk /(self.atk_interval/(1+aspd/100))
			if self.targets == 1:
				dps += bonusdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1 and self.module == 2:
				dps += bonusdmg/(self.atk_interval/(1+aspd/100)) * (self.targets -1)
		return dps

class Ela(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ela",pp,[1,2,3],[3],3,1,3)
		self.try_kwargs(3,["mine","minedebuff","debuff","grzmod","nomines","nomine","mines"],**kwargs)
		if self.talent2_dmg: self.name += " MineDebuff"
		else: self.name += " w/o mines"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
			
	def skill_dps(self, defense, res):
		if self.talent2_params[0]>1:
			cdmg = self.talent2_params[0]
			crate = self.talent2_params[1]
		else:
			cdmg = self.talent2_params[1]
			crate = self.talent2_params[0]
		if self.talent2_dmg:
			crate = 1.0
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * self.attack_speed/100
			
		if self.skill == 2:
			defshred = self.skill_params[3]
			newdef = np.fmax(0, defense - defshred)
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - newdef, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * self.attack_speed/100
			
		if self.skill == 3:
			self.atk_interval = 0.5
			fragile = self.skill_params[3]
			if not self.talent2_dmg: fragile = 0
			fragile = max(fragile, self.buff_fragile)
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[5]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1+fragile)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * (1+fragile)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * self.attack_speed/100 /(1+self.buff_fragile)
			
		return dps
	
class Estelle(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Estelle",pp,[1,2],[2],2,6,2)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		block = 3 if self.elite == 2 else 2
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,block)
		return dps

class Ethan(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ethan",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(self.skill_params[0] * (1-res/100), self.skill_params[0] * 0.05)
			active_ratio = min(1, self.skill_params[1]/ (self.atk_interval / self.attack_speed * 100))
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100 * self.targets + hitdmgarts * active_ratio * self.targets
		if self.skill == 2:
			final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100 * self.targets
		return dps

class Eunectes(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Eunectes",pp,[1,2,3],[1,2],3,1,1)
		if not self.talent_dmg and self.elite > 0: self.name += " <50%hp"
		if self.module_dmg and self.module == 2: self.name += " WhileBlocking"

	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[2] if self.talent_dmg and self.elite > 0 else 1
		atkbuff = 0.15 if self.module_dmg and self.module == 2 else 0
		final_atk = self.atk *(1+ self.buff_atk + atkbuff + self.skill_params[0]) + self.buff_atk_flat
		if self.skill == 2: self.atk_interval = 2
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class ExecutorAlter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 656  #######including trust
		maxatk = 777
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"ExecutorAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"ExecutorAlt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.ammo = 4 + 4 * self.skill
		if self.talent2: self.ammo += 4

		if not self.talent1:
			self.name += " NoAmmoUsed"
			self.ammo = 1
		else:
			self.name += f" {self.ammo}AmmoUsed"
		if self.skill == 3: self.name += f" {self.ammo}stacks"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		
		#talent/module buffs
		crate = 0.2
		critdefignore = 0
		if self.pot > 4: crate += 0.03
		if self.module == 1:
			if self.module_lvl == 2:
				crate += 0.1
				critdefignore = 150
			if self.module_lvl == 3:
				crate += 0.15
				critdefignore = 300
		
		crate += 0.05 * self.ammo
		crate = min(crate, 1)


			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.3 if self.mastery == 0 else 0.35 + 0.05 * self.mastery
			defignore = 280 + 40 * self.mastery
			newdef = np.fmax(0, defense - defignore)
			critdef =np.fmax(0, defense - defignore - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - newdef, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			atkbuff += 0.6 if self.mastery == 0 else 0.65 + 0.05 * self.mastery
			critdef = np.fmax(0, defense - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - defense, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 3:
			self.atk_interval = 1.8
			atkbuff += 1.5 + 0.1 * self.mastery
			scaling = 0.06 if self.mastery == 3 else 0.05
			atkbuff += self.ammo * scaling 
			
			critdef = np.fmax(0, defense - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - defense, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		return dps
	
class Exusiai(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Exusiai",pp,[1,2,3],[],3,1,1)
		if self.module_dmg and self.module == 1: self.name += " aerial target"	
	
	def skill_dps(self, defense, res):
		atkbuff = min(self.talent2_params) #they changed the order in the module ffs
		aspd = self.talent1_params[0]
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1+atkbuff+self.buff_atk) + self.buff_atk_flat
		skill_scale = self.skill_params[0]
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			avgphys = (self.skill_cost * hitdmg + 3 * skillhitdmg) / (self.skill_cost + 1)
			dps = avgphys/(self.atk_interval/((self.attack_speed+aspd)/100))
		elif self.skill == 2:
			hitdmg = np.fmax(final_atk *atk_scale * skill_scale - defense, final_atk* atk_scale* skill_scale * 0.05)
			dps = 4*hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		elif self.skill == 3:
			atk_interval = self.atk_interval + 2 * self.skill_params[2]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale* skill_scale * 0.05)
			dps = 5*hitdmg/(atk_interval/((self.attack_speed+aspd)/100))
		return dps
		
class Eyjafjalla(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Eyjafjalla",pp,[1,2,3],[1],3,1,1)
		if self.skill_dmg:
			if self.skill == 1: self.name += " 2ndSkilluse"
			if self.skill == 2: self.name += " permaResshred"
		if not self.skill_dmg and self.skill == 2: self.name += " minResshred"
		if self.targets > 1 and self.skill > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.elite > 0 else 0
		resignore = 10 if self.module == 1 else 0
		newres = np.fmax(0, res - resignore)

		if self.skill == 1:
			aspd = self.skill_params[0]
			if self.skill_dmg: atkbuff += self.skill_params[2]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_scale = self.skill_params[2]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			newres2 = np.fmax(0, res*(1+self.skill_params[5])-resignore)
			hitdmg = np.fmax(final_atk  * (1-newres2/100), final_atk * 0.05)
			if not self.skill_dmg: hitdmg = np.fmax(final_atk  * (1-newres/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * (1-newres2/100), final_atk* atk_scale * 0.05)
			aoeskilldmg = np.fmax(0.5 * final_atk * atk_scale * (1-newres/100), 0.5 * final_atk* atk_scale * 0.05)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg + (self.targets - 1) * aoeskilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[3] > 1:
					avghit = (skilldmg + (self.targets - 1) * aoeskilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + (self.targets - 1) * aoeskilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)								
			dps = avghit/self.atk_interval * self.attack_speed/100
			
		if self.skill == 3:
			self.atk_interval = 0.5
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			maxtargets = self.skill_params[2]
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100 * min(self.targets, maxtargets)
			 
		return dps

class FangAlter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 548  #######including trust
		maxatk = 640
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"FangAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"FangAlt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f" ModX{self.module_lvl}"
		else: self.module = 0

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1

		if self.module == 1:
			aspd += 2 + self.module_lvl
		####the actual skills
		if self.skill == 1:
			sp_cost = 5
			skill_scale = 1.5 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			
			skillhit = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)

			skillhit *= 2
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
		
			avghit = skillhit
			if atks_per_skillactivation > 1:
				avghit = (skillhit + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.95 if self.mastery == 0 else 0.9 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class Fartooth(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Fartooth",pp, [1,2,3],[1,2],3,1,1)
		if not self.talent_dmg: self.name += " w/o talent"
		if self.skill_dmg and self.skill == 3: 
			self.name += " farAway"
			self.module_dmg = True
		if self.module_dmg and self.module == 1: self.name += " maxModuleBonus"
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		aspd = 0
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1	
		#talent/module buffs
		atkbuff += self.talent1_params[0]
		try:
			aspd += self.talent1_params[2]
		except:
			pass
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			aspd += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		if self.skill == 2:
			aspd += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			dmgscale = 1
			if self.skill_dmg:
				dmgscale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)*dmgscale
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		return dps

class Fiammetta(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Fiammetta",pp, [1,3],[2,1],3,1,1)
		if not self.talent_dmg: self.name += " w/o vigor"
		elif not self.talent2_dmg: self.name += " half vigor"
		if self.skill_dmg and self.skill == 3: self.name += " central hit"
		elif self.skill == 3: self.name += " outer aoe"
		if self.module_dmg and self.module == 1: self.name += " blockedTarget"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		aspd = 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		def_shred = 100 if self.module == 2 else 0
		newdef = np.fmax(0, defense - def_shred)
		
		if self.module == 2:
			if self.module_lvl == 2: aspd += 5
			if self.module_lvl == 3: aspd += 10
		if self.talent_dmg and self.talent2_dmg:
			atkbuff += self.talent1_params[-2]
		elif self.talent_dmg:
			atkbuff += self.talent1_params[-4] #lets hope this works lol

		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * self.targets
		if self.skill == 3:
			skill_scale = self.skill_params[3]
			if self.skill_dmg:
				skill_scale = self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * self.targets
		return dps
	
class Firewhistle(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 782  #######including trust
		maxatk = 932
		self.atk_interval = 2.8   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Firewhistle Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Firewhistle P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 58
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 42
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " meelee"
		if self.moduledmg and self.module == 1: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1

		if self.talent1:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.02
			if self.module == 1:
				atkbuff += 0.04 * (self.module_lvl - 1)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.5 + 0.1 * self.mastery
			if self.mastery > 1: skill_scale += 0.05
			fire_scale = 0.5 if self.mastery == 3 else 0.4
			fire_scale *= 4
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgskill = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * fire_scale * (1-res/100), final_atk * 0.05)
			avgdmg = 3/4 * self.targets * hitdmg + 1/4 * hitdmgskill * self.targets + hitdmgarts / 4
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			skill_scale = 0.65 if self.mastery == 0 else 0.7 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgarts
			dps = dps * self.targets
		return dps

class Flamebringer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Flamebringer",pp,[1,2],[2],2,6,2)
		if self.module_dmg and self.module == 2: self.name += " afterRevive"

	def skill_dps(self, defense, res):
		aspd = 30 if self.module == 2 and self.module_dmg else 0
		if self.skill == 1:
			skill_scale = self.skill_params[0]	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			aspd += self.skill_params[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Flametail(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 516  #######including trust
		maxatk = 611
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Flametail Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Flametail P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 58
				else: self.base_atk += 44
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 35
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " blocking"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		self.atk_interval = 0.7*1.05
		#talent/module buffs
		if self.moduledmg and self.module == 1: atkbuff += 0.08
		cdmg = 1
		if self.module == 1 and self.module_lvl > 1: cdmg = 1.2 if self.module_lvl == 3 else 1.15
		critrate = 0
		if self.hits > 0:
			dodgerate = 0.8 * self.hits
			atkrate = (self.atk_interval/(1+aspd/100))
			critrate = min(1, dodgerate*atkrate)
			
		####the actual skills
		if self.skill == 3:
			atkbuff += 0.6 + 0.1 * self.mastery
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * 2 * min(3, self.targets)
			avghit = critrate * critdmg + (1 - critrate) * hitdmg
			dps = avghit/(self.atk_interval/(1+aspd/100)) 
		return dps

class Flint(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Flint",pp,[1,2],[1],2,1,1)
		if self.skill == 1 and not self.talent_dmg: self.name += " blocking"
		if self.module == 1 and self.module_dmg: self.name += " >50%Hp"

	def skill_dps(self, defense, res):
		dmgscale = 1 if self.skill == 1 and not self.talent_dmg else self.talent1_params[0]
		aspd = 10 if self.module == 1 and self.module_dmg else 0
		
		if self.skill == 1:
			skill_scale = self.skill_params[0]	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			aspd += self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps*dmgscale

class Folinic(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Folinic",pp,[2],[2],2,6,2)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.elite < 1: return 0 * defense
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Franka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Franka",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module_dmg and self.module == 1 else 1
		crate = self.talent1_params[0] if self.elite > 0 else 0
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		aspd = self.skill_params[1] if self.skill == 1 else 0
		crate *= 2.5 if self.skill == 2 else 1
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk *atk_scale * 0.05)
		critdmg = final_atk *atk_scale
		avghit = crate * critdmg + (1-crate) * hitdmg	
		dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Frost(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Frost",pp,[1,2],[2],2,1,2)
		if not self.trait_dmg: self.name += " noMines"   ##### keep the ones that apply
		else:
			if not self.talent_dmg: self.name += " 1MinePerSPcost"
			else: self.name += " 1MinePer5s"
			if self.skill == 2 and self.skill_dmg: self.name += " MineInRange"
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		newdef = np.fmax(0, defense - 40 * self.module_lvl) if self.module == 2 and self.module_lvl > 1 else defense
		hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.trait_dmg:
			critdmg = 1.2 if self.module == 2 else 1
			mine_scale = self.skill_params[1] if self.skill == 1 else self.skill_params[4]
			hitdmg_mine = np.fmax(final_atk * mine_scale - newdef, final_atk * mine_scale * 0.05) * critdmg
			if self.skill == 2 and self.skill_dmg:
				hitdmg_mine += np.fmax(final_atk * self.skill_params[1] - newdef, final_atk * self.skill_params[1] * 0.05) * 3
			hitrate = 5 if self.talent_dmg else max(5, self.skill_cost/(1+self.sp_boost))
			dps += hitdmg_mine/hitrate
		return dps

class Fuze(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Fuze",pp,[1,2],[2],1,6,2)
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.skill == 2:
			explosion_dmg =  (self.atk * (1 + self.buff_atk) + self.buff_atk_flat) * self.skill_params[0] * (1 + self.buff_fragile)
			self.name += f" Explosion:5x{int(explosion_dmg)}"

	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[1] if self.skill == 1 else 0
		aspd = self.skill_params[2] if self.skill == 1 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		max_targets = 3 if self.elite == 2 else 2
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,max_targets)
		return dps

class GavialAlter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 632  #######including trust
		maxatk = 816
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Gavialter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Gavialter P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 73
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 45
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		block = 5 if self.skill == 3 else 3
		if self.talent1: self.name += f""" {min(block,self.targets)}talentStack{"s" if self.targets > 1 else ""}"""
		if self.module == 1 and self.moduledmg: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		block = 5 if self.skill == 3 else 3
		atkbuff += 0.12 if self.pot > 2 else 0.1
		if self.module == 1 and self.module_lvl > 1: atkbuff += 0.03
		if self.talent1:
			bonusatk = 0.05 if self.pot > 2 else 0.04
			if self.module == 1 and self.module_lvl == 3: bonusatk += 0.01
			atkbuff += bonusatk * min(self.targets, block)
		
		if self.module == 1 and self.moduledmg: atk_scale = 1.1

		if self.module == 1:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.02
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.8 if self.mastery == 3 else 0.6 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
		
		if self.skill == 2:
			atkbuff += 1.4 if self.mastery == 0 else 1.35 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
		if self.skill == 3:
			atkbuff += 1.4 if self.mastery == 3 else 1.0 + 0.1 * self.mastery
			aspd += 100 if self.mastery == 3 else 80
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
			
		return dps

class Gladiia(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 690  #######including trust
		maxatk = 851
		self.atk_interval = 1.8   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Gladiia Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Gladiia P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 59
				else: self.base_atk += 45
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if not self.talent2: self.name += " vsHeavy"
		else: self.name += " vsLight"
		
		
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2:
			atk_scale = 1.36 if self.pot > 4 else 1.3
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.8 + 0.1 * self.mastery
			sp_cost = 4 if self.mastery == 3 else 5
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			self.atk_interval = 2.7
			skill_scale = 1.5 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:

			skill_scale = 1 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/1.5 * self.targets
		return dps

class Gnosis(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 457  #######including trust
		maxatk = 535
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 33
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Gnosis Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Gnosis P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 25
				elif self.module_lvl == 2: self.base_atk += 20
				else: self.base_atk += 15
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 3:
			if self.skilldmg: self.name += " vsFrozen"
			else: self.name += " vsNonFrozen"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		coldfragile = 0.27 if self.pot > 4 else 0.25
		if self.module == 1:
			if self.module_lvl == 2: coldfragile += 0.03
			if self.module_lvl == 3: coldfragile += 0.05
		frozenfragile = 2 * coldfragile
		
		coldfragile = max(coldfragile, self.buffs[3])
		frozenfragile = max(frozenfragile, self.buffs[3])
		frozenres = np.fmax(0, res - 20)
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.7 if self.mastery == 3 else 1.5 + 0.05 * self.mastery
			sp_cost = 4 + 1.2 #sp lockout
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			aspd += 130 if self.mastery == 3 else 122 + 2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			if self.skilldmg: hitdmg = np.fmax(final_atk * (1-frozenres/100), final_atk * 0.05)*(1+frozenfragile)/(1+self.buffs[3])
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(2, self.targets)
			
		return dps
		
	def get_name(self):
		if self.skill == 3:
			skillscale = 6 if self.mastery == 3 else 4 + 0.5 * self.mastery
			coldfragile = 0.27 if self.pot > 4 else 0.25
			if self.module == 1:
				if self.module_lvl == 2: coldfragile += 0.03
				if self.module_lvl == 3: coldfragile += 0.05
			fragile = 2 * coldfragile
			fragile = max(fragile, self.buffs[3])
			final_atk = self.base_atk * (1+self.buffs[0]) + self.buffs[1]
			nukedmg = final_atk * skillscale * (1+fragile)
			self.name += f" Nuke:{int(nukedmg)}"
			
		return self.name

class Goldenglow(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Goldenglow",pp,[1,2,3],[],3,1,1)
		if self.trait_dmg: self.name += " maxDroneDmg"
		else: self.name += " minDroneDmg"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		newres = np.fmax(res-self.talent2_params[0],0)
		drone_dmg = 1.1
		drone_explosion = self.talent1_params[1] if self.elite > 0 else 0
		explosion_prob = 0.1 if self.elite > 0 else 0
		aspd = 0
		drones = 2
		if not self.trait_dmg:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		
		atkbuff = self.skill_params[0]
		if self.skill == 1:
			aspd += self.skill_params[1]
		if self.skill == 3:
			drones = 3
		final_atk = self.atk * (1+atkbuff+self.buff_atk) + self.buff_atk_flat
		drone_atk = drone_dmg * final_atk
		drone_explosion = final_atk * drone_explosion * self.targets
		dmgperinterval = final_atk*(3-drones) + drones * drone_atk * (1-explosion_prob) + drones * drone_explosion * explosion_prob
		hitdmgarts = np.fmax(dmgperinterval *(1-newres/100), dmgperinterval * 0.05)
		dps = hitdmgarts/self.atk_interval*(self.attack_speed+aspd)/100
		return dps

class Grani(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 463  #######including trust
		maxatk = 552
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Grani Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Grani P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.targets = max(1,targets)
		self.buffs = buffs
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		atkbuff += 0.8 if self.mastery == 3 else 0.6 + 0.06 * self.mastery
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class GreyThroat(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 495  #######including trust
		maxatk = 588
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"GreyThroat Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"GreyThroat P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 33
				elif self.module_lvl == 2: self.base_atk += 29
				else: self.base_atk += 24
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if self.moduledmg and self.module == 2: self.name += " GroundTargets"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		aspd += 6
		if self.module == 2 and self.moduledmg:
			aspd += 8
		
		cdmg = 1.5
		crate = 0.15
		if self.module == 2: crate += 0.03 * (self.module_lvl - 1)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.25 + 0.05 * self.mastery
			sp_cost = 5 if self.mastery == 0 else 4
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * 2
			skillcrit = np.fmax(final_atk * atk_scale * skill_scale * cdmg - defense, final_atk* atk_scale * skill_scale * cdmg * 0.05) * 2
			avgnorm = crate * critdmg + (1-crate) * hitdmg
			avgskill = crate * skillcrit + (1-crate) * skilldmg
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = avgskill
			if atks_per_skillactivation > 1:
				avghit = (avgskill + (atks_per_skillactivation - 1) * avgnorm) / atks_per_skillactivation						
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.4 if self.mastery == 3 else 0.2 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			avgnorm = crate * critdmg + (1-crate) * hitdmg
			dps = 3 * avgnorm/(self.atk_interval/(1+aspd/100))
		return dps

class Haze(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Haze",pp,[1,2],[1],2,6,1)
	
	def skill_dps(self, defense, res):
		resignore = 10 if self.module == 1 else 0
		newres = np.fmax(0, res-resignore) * (1 + self.talent1_params[1])
		atkbuff = self.skill_params[0] if self.skill == 1 else self.skill_params[1]
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		return dps
	
class Hellagur(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 702  #######including trust
		maxatk = 832
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Hellagur Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Hellagur P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " lowHP"
		else: self.name += " fullHP"
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			aspd += 100
			if self.module == 1 and self.module_lvl > 1:
				aspd += 10 * self.module_lvl
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.45 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * 2
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * 2
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
		return dps

class Hibiscus(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 468 #######including trust
		maxatk = 571
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 22
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Hibiscus Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Hibiscus P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		dmg = 1.14 if self.pot > 4 else 1.12
		if self.module == 1:
			if self.module_lvl == 3: dmg += 0.08
			elif self.module_lvl == 2: dmg += 0.05
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 1 if self.mastery == 3 else 0.6 + 0.15* self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			scale = 1.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * scale * (1-res/100), final_atk * scale * 0.05) * dmg
			dps = hitdmg * min(self.targets,2 )
		return dps

class Highmore(Operator):
	def __init__(self, pp, *args,**kwargs):
		super().__init__("Highmore",pp,[1,2],[1],1,6,1)
		if self.talent_dmg: self.name += " in IS3"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		aspd = self.talent2_params[0] if self.talent_dmg else 0

		if self.skill == 1:
			skill_scale = self.skill_params[0]			
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		return dps

class Hoederer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Hoederer",pp,[1,2,3],[1],3,1,1)
		if self.skill == 2 and self.skill_dmg: self.talent_dmg = True
		if self.talent_dmg and self.elite > 0: self.name += " vsStun/Bind"
		elif self.skill == 3 and self.skill_dmg: self.name += " vsSelfAppliedStun"
		if self.skill == 2 and not self.skill_dmg: " defaultState"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atk_scale = 1
		if self.elite > 0:
			atk_scale = max(self.talent1_params) if self.talent_dmg else min(self.talent1_params)
		dmg_bonus = 1
		if self.module == 1:
			if self.module_lvl == 2: dmg_bonus = 1.06
			if self.module_lvl == 3: dmg_bonus = 1.1
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100 * min(self.targets,2) * dmg_bonus
		if self.skill == 2:
			maxtargets = 3 if self.skill_dmg else 2
			if self.skill_dmg: self.atk_interval = 3 
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,maxtargets) * dmg_bonus
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if not self.talent_dmg and self.skill_dmg:
				stun_duration = self.skill_params[4]
				atk_cycle = self.atk_interval / self.attack_speed * 100
				counting_hits = int(stun_duration/atk_cycle) + 1
				chance_to_attack_stunned = 1 - 0.75 ** counting_hits
				atk_scale = max(self.talent1_params)
				hitdmg2 = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
				hitdmg = chance_to_attack_stunned * hitdmg2 + (1-chance_to_attack_stunned)*hitdmg
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * dmg_bonus  + 200
			dps = dps * min(2, self.targets)
		return dps
	
class Hoolheyak(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 615  #######including trust
		maxatk = 723
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ho'olheyak Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ho'olheyak P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 32
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " vsAerial"
		if self.skill == 3:
			if self.skilldmg: self.name += " maxRange"
			else: self.name += " minRange"
		if self.module == 2 and self.module_lvl > 1 and self.talent2: self.name += " vsLowHp"
		
		if self.targets > 1 and not self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atk_scale = 1.2 if self.pot < 5 else 1.23
			if self.module == 1:
				if self.module_lvl > 1: atk_scale += 0.05 * self.module_lvl
		newres = np.fmax(res-10,0) if self.module == 1 else res
		dmg_scale = 1
		if self.module == 2 and self.talent2:
			dmg_scale += 0.1 * (self.module_lvl -1)
			
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.4 + 0.2 * self.mastery
			sp_cost = 8 if self.mastery == 0 else 7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = np.fmax(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05) * dmg_scale
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale

			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg * min(2, self.targets)
			if atks_per_skillactivation > 1:
				avghit = (skilldmg * min(2, self.targets) + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			skill_scale = 0.45 if self.mastery == 3 else 0.35 + 0.03 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = 9 * hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			self.atk_interval = 3
			skill_scale = 3.8 if self.mastery == 0 else 3.9 + 0.1 * self.mastery
			if not self.skilldmg: skill_scale *= 2/3	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
		return dps
	
class Horn(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Horn",pp,[1,2,3],[1,2],3,1,1)
		self.try_kwargs(3,["afterrevive","revive","after","norevive"],**kwargs)
		self.try_kwargs(4,["overdrive","nooverdrive"],**kwargs)
		self.try_kwargs(5,["blocked","unblocked"],**kwargs)
		if self.talent2_dmg and self.elite == 2: self.name += " afterRevive"
		if self.skill_dmg and not self.skill == 1: self.name += " overdrive"
		elif not self.skill == 1: self.name += " no overdrive"
		if self.module_dmg and self.module == 1: self.name += " blockedTarget"
		if self.module_dmg and self.module == 2: self.name += " rangedAtk"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.skill == 1 and self.sp_boost > 0: self.name += f" +{self.sp_boost}SP/s"
			
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent1_params[0]
		aspd = self.talent2_params[2] if self.talent2_dmg else 0
		if self.module == 2 and self.module_dmg: aspd += 10
		if self.module == 2 and self.module_lvl > 1:
			if self.module_lvl == 2: aspd += 5
			if self.module_lvl == 3: aspd += 8

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[3] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval*(self.attack_speed+aspd)/100 * self.targets
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			arts_scale = 0
			if self.skill_dmg:
				arts_scale = self.skill_params[1]
			final_atk = final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			artsdmg = np.fmax(final_atk * atk_scale * arts_scale * (1-res/100), final_atk * atk_scale * arts_scale * 0.05)
			dps = (hitdmg+artsdmg)/self.atk_interval*(self.attack_speed+aspd)/100 * self.targets
		if self.skill == 3:
			atk_interval = self.atk_interval + self.skill_params[1]
			atkbuff += self.skill_params[0]
			if self.skill_dmg: atkbuff += self.skill_params[0]
			final_atk = final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) 			
			dps = hitdmg/atk_interval*(self.attack_speed+aspd)/100 * self.targets
		return dps

class Hoshiguma(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 416  #######including trust
		maxatk = 490
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 100
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Hoshiguma Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Hoshiguma P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]

		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0 and self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
				
		if self.skill == 2:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.hits > 0:
				skill_scale = 1 if self.mastery == 3 else 0.8 + 0.05 * self.mastery
				reflectdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
				dps += reflectdmg * self.hits	
		if self.skill == 3:
			atkbuff += 0.95 + 0.15 * self.mastery		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps

class Humus(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Humus",pp,[1,2],[1],2,6,1)
		if self.skill == 2:
			if self.skill_dmg: self.name += " >80%Hp"
			else: self.name += " <50%Hp"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1+self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) 
			dps = avgphys/self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 2:
			atkbuff = self.skill_params[2] if self.skill_dmg else 0
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Iana(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 630  #######including trust
		maxatk = 758
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Iana Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Iana P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
	
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		fragile = 0.22 if self.pot > 4 else 0.2
		if self.module == 1:
			atkbuff += 0.15  #from module change, since she only deals damage as doll
			if self.module_lvl == 2: fragile += 0.05
			if self.module_lvl == 3: fragile += 0.08

			
		####the actual skills
		if self.skill == 2:
			aspd += 300 if self.mastery == 3 else 260 + 10 * self.mastery
			
			fragile = max(fragile, self.buffs[3])

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1+fragile)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) /(1+self.buffs[3])
		return dps

class Ifrit(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 832  #######including trust
		maxatk = 980
		self.atk_interval = 2.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ifrit Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ifrit P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 72
				elif self.module_lvl == 2: self.base_atk += 64
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg and self.module == 1: self.name += " maxRange"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1:
			aspd += 4 + self.module_lvl
			if self.moduledmg:
				atk_scale = 1.1

		resshred = 0.4
		if self.pot > 2:
			resshred += 0.04
		
		recovery_interval = 5.5 if self.pot == 6 else 6
		sp_recovered = 2
		if self.module == 1:
			if self.module_lvl == 2: sp_recovered = 3
			if self.module_lvl == 3: sp_recovered = 2 + 0.3 * 5
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.2
			aspd += 70
			if self.mastery == 0: aspd -= 3
			elif self.mastery > 1: aspd += 5 * (self.mastery - 1)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			newres = res * (1-resshred)
			hitdmgarts = np.fmax(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			sp_cost = 8 if self.mastery == 0 else 7
			skill_scale = 1.9 + 0.25 * self.mastery
			if self.mastery > 1: skill_scale -= 0.15
			burn_scale = 0.99
			newres = res * (1-resshred)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			skilldmgarts = np.fmax(final_atk *atk_scale *skill_scale *(1-newres/100), final_atk * atk_scale * skill_scale * 0.05)
			burndmg = np.fmax(final_atk *burn_scale *(1-newres/100), final_atk * burn_scale * 0.05)
			
			sp_cost = sp_cost / (1+sp_recovered/recovery_interval) + 1.2 #talent bonus recovery + sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts + burndmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmgarts + burndmg + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation	
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
				
		if self.skill == 3:
			atk_scale *= 1.1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			flatshred = 20 if self.mastery == 3 else 10 + 3 * self.mastery
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				res = res / self.shreds[0]
			newres = np.fmax(0, res-flatshred)
			newres = newres * (1-resshred)
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				newres *= self.shreds[2]
			hitdmgarts = np.fmax(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
		return dps

class Indra(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Indra",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " >50% HP"

	def skill_dps(self, defense, res):
		aspd = 10 if self.module_dmg and self.module == 1 else 0
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			newdef = defense * (1 - self.skill_params[1]) 
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skilldmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			dps = 0.2*(4*hitdmg + skilldmg)/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Ines(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ines",pp,[1,2,3],[],2,1,0)
		self.try_kwargs(4,["steal","nosteal"],**kwargs)
		if self.skill == 2:
			if self.skill_dmg: self.name += " maxSteal"
			else: self.name += " noSteal"
		if self.skill == 3:
			skillbuff = self.skill_params[1]
			steal = 0 if self.elite < 1 else self.talent1_params[0]
			final_atk = self.atk * (1 + self.buff_atk + skillbuff) + self.buff_atk_flat + steal
			nukedmg = final_atk * self.skill_params[2] * (1+self.buff_fragile)
			self.name += f" ShadowDmg:{int(nukedmg)}"

	def skill_dps(self, defense, res):
		stolen_atk = 0 if self.elite < 1 else self.talent1_params[0]

		if self.skill == 1:
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat + stolen_atk
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale * (1 - res/100), final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			dps = hitdmg/self.atk_interval * self.attack_speed/100 + skillhitdmg * min(1, 3 / ((sp_cost+1) * self.atk_interval/self.attack_speed*100)) 
		if self.skill == 2:
			atkbuff = self.skill_params[1]
			aspd = self.skill_params[3] if self.skill_dmg else self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat + stolen_atk
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat + stolen_atk
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Insider(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Insider",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.module == 1 and self.module_dmg: self.name += " vsAerial"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  * atk_scale - defense, final_atk  * atk_scale * 0.05)
			dps = hitdmg / 0.7 * (self.attack_speed) / 100
		return dps

class Irene(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Irene",pp,[1,3],[2,1],3,1,2)
		if not self.talent_dmg: self.name += " vsLevitateImmune"
		self.try_kwargs(3,["seaborn","vs","vsseaborn","noseaborn"],**kwargs)
		if self.module == 2 and self.module_lvl > 1 and self.talent2_dmg: self.name += " vsSeaborn"
		if self.skill == 3 and not self.skill_dmg and self.talent_dmg: self.name += " vsHeavy"
		if self.skill == 3: self.name += " totalDMG"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		aspd = self.talent2_params[0]
		atkbuff = self.talent2_params[1] if self.module == 2 and self.module_lvl > 1 else 0
		if self.talent2_dmg:
			atkbuff *= 2
			aspd *= 2
		skill_dmg = 1.1 if self.module == 1 else 1
		newdef1 = defense if self.module != 2 else np.fmax(0, defense -70)
		defshred = 0
		if self.elite > 0:
			defshred = self.talent1_params[0]
		newdef2 = newdef1 * (1-defshred)

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg1 = np.fmax(final_atk - newdef1, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk - newdef2, final_atk * 0.05)
			skill_dmg = np.fmax(final_atk * skill_scale - newdef2, final_atk * skill_scale * 0.05) * skill_dmg
			sp_cost = self.skill_cost
			avgdmg = ((hitdmg1+hitdmg2) * sp_cost + 2 * skill_dmg)/(sp_cost + 1)
			dps = avgdmg / self.atk_interval * (self.attack_speed+aspd)/100
			
		if self.skill == 3:
			skill_scale1 = self.skill_params[0]
			hits = self.skill_params[3]
			skill_scale = self.skill_params[2]
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			initialhit1 = np.fmax(final_atk * skill_scale1 - newdef1, final_atk *skill_scale1 * 0.05)*skill_dmg
			initialhit2 = np.fmax(final_atk * skill_scale1 - newdef2, final_atk * skill_scale1 * 0.05)*skill_dmg
			hitdmg1 = np.fmax(final_atk * skill_scale - newdef1, final_atk *skill_scale * 0.05)*skill_dmg
			hitdmg2 = np.fmax(final_atk * skill_scale - newdef2, final_atk *skill_scale * 0.05)*skill_dmg
			dps = 0.5*initialhit1 + 0.5* initialhit2
			levduration = self.skill_params[1]
			if not self.talent_dmg: return (dps + hits * (0.5*hitdmg1+0.5*hitdmg2))
			else:
				if not self.skill_dmg:
					levduration = levduration /2
			flyinghits = min(hits, int(levduration / 0.3))
			dps += flyinghits * hitdmg2 + (hits-flyinghits) * (0.5*hitdmg1+0.5*hitdmg2)
			dps *= self.targets
		return dps

class Jackie(Operator):
	def __init__(self, plot_parameters, *args, **kwargs):
		super().__init__("Jackie",plot_parameters,[1],[],1,6,1)
		if self.talent_dmg: self.name += " afterDodge"
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[1] if self.talent_dmg else 0
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * self.skill_params[0] - defense, final_atk * self.skill_params[0] * 0.05)
			avgdmg = (hitdmg * self.skill_cost + skilldmg) / (self.skill_cost+1)
			dps = avgdmg/self.atk_interval*(self.attack_speed+aspd)/100
		return dps

class Jaye(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Jaye",pp,[1,2],[1],2,6,1)
		self.try_kwargs(2,["infected","vsInfected","notinfected","noinfected"],**kwargs)
		if self.talent_dmg: self.name += " vsInfected"
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Jessica(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Jessica",pp ,[1,2],[2],1,6,2)
		if self.module == 2 and self.module_dmg: self.name += " groundEnemies"
		
	def skill_dps(self, defense, res):
		aspd = max(self.talent1_params)
		aspd += 8 if self.module == 2 and self.module_dmg else 1
		atkbuff = (self.module_lvl-1) * 0.03 if self.module == 2 and self.module_lvl > 1 else 0
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg_skill = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avghit = (hitdmg * self.skill_cost + hitdmg_skill)/(self.skill_cost + 1)
			dps = avghit / self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + atkbuff + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class JessicaAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("JessicaAlter",pp ,[1,2,3],[1],3,1,1)
		if self.skill == 3:
			skillbuff = self.skill_params[0]
			final_atk = self.atk * (1+ self.buff_atk + skillbuff) + self.buff_atk_flat
			nukedmg = final_atk * 2.5 * (1+self.buff_fragile)
			self.name += f" GrenadeDmg:{int(nukedmg)}"

	def skill_dps(self, defense, res):
		if self.skill == 1:
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[1]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			self.atk_interval = 0.3
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			self.atk_interval = 1.8
			final_atk = final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class JusticeKnight(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("JusticeKnight",pp,[],[],0,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg: self.name += f" first{int(self.talent1_params[0])}s vsDrone"
	
	def skill_dps(self, defense, res):
		fragile = self.talent1_params[1] - 1
		if not self.talent2_dmg: fragile = 0
		fragile = max(fragile, self.buff_fragile)
		final_atk = self.atk * (1  + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1 + fragile)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 /(1+self.buff_fragile)
		return dps

class Kafka(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 409  #######including trust
		maxatk = 525
		self.atk_interval = 0.93   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Kafka Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Kafka P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"


		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 54
				else: self.base_atk += 45
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg and self.module == 2: self.name += " alone"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.moduledmg and self.module == 2:
			atkbuff += 0.1
		
		atkbuff += 0.15
		if self.pot > 4: atkbuff += 0.03
		
		if self.module == 2:
			if self.module_lvl == 2: atkbuff += 0.07
			if self.module_lvl == 3: atkbuff += 0.1
			
		####the actual skills
		if self.skill == 2:

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

	def get_name(self):
		if self.skill == 2:
			talent = 0.18 if self.pot > 4 else 0.15
			
			if self.module == 2:
				if self.module_lvl == 2: talent += 0.07
				if self.module_lvl == 3: talent += 0.1
			skill_scale = 4 if self.mastery == 3 else 3 + 0.3 * self.mastery
			final_atk = self.base_atk * (1+self.buffs[0] + talent) + self.buffs[1]
			nukedmg = final_atk * skill_scale * (1+self.buffs[3])
			self.name += f" InitialHit:{int(nukedmg)}"
		return self.name

class Kazemaru(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kazemaru",pp,[1,2],[1],2,1,1)
		if self.skill == 2 and not self.skill_dmg: self.name += " w/o doll"
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat	
			damage = final_atk * self.talent1_params[0]* (1+self.buff_fragile)
			self.name += f" SummoningAoe:{int(damage)}"

	def skill_dps(self, defense, res):
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat	
			final_atk2 = self.drone_atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk2 - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.skill_dmg: dps += hitdmg2/self.drone_atk_interval * self.attack_speed/100
		return dps

class Kirara(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kirara",pp,[1,2],[1],2,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale * (1 - res/100), final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avghit = ((sp_cost+1) * hitdmg + skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * skill_scale * (1- res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg * self.targets
		return dps

class Kjera(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 306  #######including trust
		maxatk = 354
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Kjera Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Kjera P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 28
				elif self.module_lvl == 2: self.base_atk += 23
				else: self.base_atk += 18
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.talent: self.name += " noGroundTiles"
		if not self.trait: self.name += " minDroneDmg"
		
		self.buffs = buffs
		
		self.freezeRate = 0 #ill just assume the freezing hit already benefits from the resshred
		if self.skill == 2:
			baseChance = 0.2 if self.mastery == 0 else 0.22
			hitchances = [0,0,0]
			atkInterval = 1.3 / (1 + self.buffs[2] / 100)
			countingCycles = int(2.5 / atkInterval)
			for j in range(3):
				totalHits = 3 * countingCycles + j + 1
				for successes in range (2,totalHits+1):
					hitchances[j] += (1-baseChance)**(totalHits-successes) * baseChance**successes * math.comb(totalHits, successes)
			self.freezeRate = sum(hitchances)/3
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		drone_dmg = 1.2 if self.module == 2 else 1.1
				
		atkbuff += 0.13 if self.pot > 4 else 0.1
		if self.talent: atkbuff += 0.06
		if self.module == 2:
			if self.module_lvl == 2: atkbuff += 0.05
			if self.module_lvl == 3: atkbuff += 0.08
		
		if not self.trait:
			drone_dmg = 0.2
		
		if self.skill == 1:
			atkbuff += 1 if self.mastery == 3 else 0.6 + 0.15 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			drone_atk = drone_dmg * final_atk
			dmgperinterval = final_atk + drone_atk
			hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.4 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			drone_atk = drone_dmg * final_atk
			dmgperinterval = final_atk + 2 * drone_atk
			res2 = np.fmax(0,res-15)
			hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			hitdmgfreeze = np.fmax(dmgperinterval *(1-res2/100), dmgperinterval * 0.05)
			damage = hitdmgfreeze * self.freezeRate + hitdmgarts * (1 - self.freezeRate)
			dps = damage/(self.atk_interval/(1+aspd/100))
			
		return dps
	
class Kroos(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kroos",pp,[1],[],1,6,0)
	
	def skill_dps(self, defense, res):
		crate = 0 if self.elite == 0 else self.talent1_params[0]
		cdmg = self.talent1_params[1]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skill_scale = self.skill_params[0]
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		hitcrit = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * 2
		skillcrit =  np.fmax(final_atk * skill_scale * cdmg - defense, final_atk * skill_scale * cdmg * 0.05) * 2
		avghit = crate * hitcrit + (1-crate) * hitdmg
		avgskill = crate * skillcrit + (1-crate) * skilldmg
		avgdmg = (avghit * self.skill_cost + avgskill) / (self.skill_cost+1)
		dps = avgdmg/self.atk_interval * self.attack_speed/100
		return dps

class KroosAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("KroosAlter",pp,[1,2],[1],2,6,1)
		if self.skill == 2:
			if self.skill_dmg: self.name += " 4hits"
			else: self.name += " 2hits"
		if self.module_dmg and self.module == 1: self.name += " aerial target"
			
	def skill_dps(self, defense, res):
		crate = 0 if self.elite == 0 else self.talent1_params[0]
		cdmg = self.talent1_params[1]
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		atk_interval = self.atk_interval * (1 + self.skill_params[0]) if self.skill == 2 else self.atk_interval
		hits = 4 if self.skill == 2 and self.skill_dmg else 2
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale -defense, final_atk * atk_scale * 0.05)
		critdmg = np.fmax(final_atk * atk_scale * cdmg -defense, final_atk * atk_scale * cdmg * 0.05)
		avgdmg = critdmg * crate + hitdmg * (1-crate)
		dps = hits * avgdmg/atk_interval * self.attack_speed/100
		return dps

class Laios(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Laios",pp,[1,2],[2],1,1,2) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 1 and not self.skill_dmg:
			self.name += f" below {int(100*self.skill_params[0])}%hp"
		if self.talent_dmg and self.elite > 0: self.name += " TalentUp"
		if self.module == 2 and self.module_dmg: self.name += " ModRevive"
		if self.skill == 2:
			self.name += " avgDmg"
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skilldmg = final_atk * self.skill_params[0]
			self.name += f" Hit:{int(skilldmg)}"
	
	def skill_dps(self, defense, res):
		aspd = 30 if self.module == 2 and self.module_dmg else 0
		new_defense = defense * (1-self.talent1_params[0]) if self.talent_dmg and self.elite > 0 else defense
		
		if self.skill == 1:
			atkbuff = self.skill_params[1] if self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - new_defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - new_defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk *skill_scale - new_defense, final_atk * skill_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
			sp_cost = self.skill_cost / (1+self.sp_boost)
			dps = (dps * sp_cost + skilldmg) / (sp_cost + self.skill_params[1])

		return dps

class LaPluma(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LaPluma",pp,[1,2],[1],1,1,1)
		if self.talent_dmg: self.name += " maxStacks"
		else: self.name += " noStacks"
		if self.skill_dmg and self.skill == 2: self.name += " lowHpTarget"
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		aspd = self.talent1_params[0] * self.talent1_params[1] if self.talent_dmg else 0
		if self.talent_dmg and self.module == 1 and self.module_lvl > 1: atkbuff = self.talent1_params[2]

		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_interval = self.atk_interval * (1 + self.skill_params[3])
			atkbuff += self.skill_params[0]
			if self.skill_dmg:
				atkbuff += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/atk_interval * (self.attack_speed+aspd)/100
			
		return dps
	
class Lappland(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lappland",pp,[1,2],[1],2,1,1)
		if not self.trait_dmg and self.skill == 1: self.name += " rangedAtk"   ##### keep the ones that apply
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = 0.8 if not self.trait_dmg and self.skill == 1 else 1
		bonus = 0.1 if self.module == 1 else 0
		fragile = 0.04 * (self.module_lvl-1) if self.module == 1 and self.module_lvl > 1 else 0
		fragile = max(fragile, self.buff_fragile)
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		####the actual skills
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg) / self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg) / self.atk_interval * self.attack_speed/100 * min(2,self.targets)
		return dps*(1+fragile)/(1+self.buff_fragile)

class Lava3star(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lava",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + self.skill_params[0]) / 100 * self.targets
		return dps

class Lavaalt(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LavaAlter",pp,[1,2],[1],2,6,1)
		if self.skill_dmg and self.skill==2: self.name += " overlap"
		if self.skill_dmg and self.skill==1 and self.targets > 1: self.name += " overlap"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100 * self.targets
			if self.skill_dmg and self.targets > 1:
				dps *= 2
		if self.skill == 2:
			atk_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
			if self.skill_dmg:
				dps *= 2	
		return dps

class Lee(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 709  #######including trust
		maxatk = 844
		self.atk_interval = 1  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lee Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lee P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 74
				elif self.module_lvl == 2: self.base_atk += 67
				else: self.base_atk += 55
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 76
				elif self.module_lvl == 2: self.base_atk += 69
				else: self.base_atk += 57
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1:
			if self.targets == 1: self.name += " blocking(doubled)"
			else: self.name += " blocking"
		
		if self.module == 2 and self.moduledmg: self.name += " 5moduleStacks"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			moreAspd = 15 if self.pot > 4 else 14
			if self.module == 2: moreAspd += 3 * (self.module_lvl - 1)
			if self.targets == 1: moreAspd *= 2
			aspd += moreAspd
		
		if self.module == 2 and self.moduledmg:
			atkbuff += 0.2
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			aspd += 30 if self.mastery == 3 else 20
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 3:
			atkbuff += 0.37 if self.mastery == 0 else 0.35 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))	
		return dps
	
	def get_name(self):
		if self.skill == 2:
			skillscale = 3 if self.mastery == 3 else 2.6 + 0.1 * self.mastery
			maxscale = 6 if self.mastery == 3 else 0.15 * 25
			atk = 0.2 if self.module == 2 and self.moduledmg else 0
				
			final_atk = self.base_atk * (1 + self.buffs[0] + atk) + self.buffs[1]
			nukedmg = final_atk * skillscale * (1+self.buffs[3])
			maxdmg = final_atk * (skillscale + maxscale) * (1+self.buffs[3])
			self.name += f" NukeDmg:{int(nukedmg)}-{int(maxdmg)}"
		return self.name

class Lessing(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lessing",pp,[1,2,3],[1],2,6,1)

		if self.skill == 3 and self.module == 1:
			self.skill_dmg = self.skill_dmg and self.module_dmg
			self.module_dmg = self.skill_dmg
		if not self.talent2_dmg and self.elite == 2: self.name += " w/o talent2"
		if self.module_dmg and self.module == 1 and not self.skill == 3: self.name += " vsBlocked"
		elif self.skill == 3 and self.skill_dmg: self.name += " vsBlocked"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent2_params[0] if self.talent2_dmg else 0

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)	
			dps = avgphys/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + atkbuff + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = 2 * hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			if self.skill_dmg: atk_scale *= self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps =  hitdmg/self.atk_interval * self.attack_speed/100
		return dps
	
class Leto(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 590  #######including trust
		maxatk = 720
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Leto Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Leto P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 59
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 40
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
	
		if not self.trait and not self.skill == 2: self.name += " rangedAtk"   ##### keep the ones that apply
		if self.module == 2 and self.targets == 1 and self.moduledmg: self.name += " +12aspd(mod)"

		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.skill == 1 and not self.trait:
			atk_scale = 0.8
		
		if self.module == 2 and (self.targets > 1 or self.moduledmg): aspd += 12
		
		aspd += 21
		if self.module == 2:
			if self.module_lvl == 2: aspd += 6
			if self.module_lvl == 3: aspd += 11
		if self.pot > 4: aspd += 3
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			aspd += 35
			if self.mastery == 3:
				aspd += 10
				atkbuff += 0.02
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(2, self.targets)
		
		return dps

class Lin(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lin",pp,[1,2,3],[1],3,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		if self.skill == 2:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		else:
			if self.skill == 1: self.atk_interval = 3
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Ling(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ling",pp,[1,2,3],[2],3,1,2)
		if self.module == 2 and self.module_lvl ==3:
			if self.skill == 3: self.drone_atk += 60
			if self.skill == 2: self.drone_atk += 35
			if self.skill == 1: self.drone_atk += 45
		if not self.trait_dmg: self.name += " noDragons"  
		elif not self.talent_dmg: self.name += " 1Dragon"
		else: self.name += " 2Dragons"
		if self.skill == 3 and self.trait_dmg:
			if self.skill_dmg: self.name += "(Chonker)"
			else: self.name += "(small)"			
		if not self.talent2_dmg and self.elite == 2: self.name += " noTalent2Stacks"
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" 
			
	
	def skill_dps(self, defense, res):
		talentbuff = self.talent2_params[0] * self.talent2_params[2] if self.talent2_dmg else 0
		dragons = 2 if self.talent_dmg else 1
		if not self.trait_dmg: dragons = 0

		####the actual skills
		if self.skill == 1:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1]
			
			final_atk = self.atk * (1+atkbuff + talentbuff + self.buff_atk) + self.buff_atk_flat
			final_dragon = self.drone_atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrag = np.fmax(final_dragon * (1-res/100), final_dragon * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) + hitdmgdrag/(self.drone_atk_interval/((self.attack_speed + aspd)/100)) * dragons
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + talentbuff + self.buff_atk) + self.buff_atk_flat
			final_dragon = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrag = np.fmax(final_dragon * (1-res/100), final_dragon * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			skilldmgdrag = np.fmax(final_dragon * skill_scale * (1-res/100), final_dragon * skill_scale * 0.05)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			dpsskill = (skilldmg + dragons * skilldmgdrag) * min(self.targets,2) / sp_cost			
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) + hitdmgdrag/(self.drone_atk_interval/(self.attack_speed/100)) * dragons + dpsskill
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + talentbuff + self.buff_atk) + self.buff_atk_flat
			chonkerbuff = 0.8 if self.skill_dmg else 0
			final_dragon = self.drone_atk * (1+atkbuff + self.buff_atk + chonkerbuff) + self.buff_atk_flat
			dragoninterval = self.drone_atk_interval if not self.skill_dmg else 2.3
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			block = 4 if self.skill_dmg else 2
			hitdmgdrag = np.fmax(final_dragon - defense, final_dragon * 0.05) * min(self.targets, block)
			skilldmg = hitdmg * 0.2
			
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) + hitdmgdrag/(dragoninterval/(self.attack_speed/100)) * dragons + skilldmg * 2 * dragons * self.targets
		return dps

class Logos(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 600  #######including trust
		maxatk = 761
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Logos Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Logos P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,3] else 3 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 3:
				if self.module_lvl == 3: self.base_atk += 67
				elif self.module_lvl == 2: self.base_atk += 54
				else: self.base_atk += 36
				self.name += f" Mod$\\Delta${self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 2 and self.skilldmg: self.name += " after5sec"
		if self.module == 3 and self.talent1: self.name += " withAvgNecrosis"
		elif self.module == 3: self.name += " noNecrosis"
		if self.module == 3 and self.talent1 and not self.moduledmg: self.name += " vsBoss"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		bonuschance = 0.4
		bonusdmg = 0.65 if self.pot > 4 else 0.6
		if self.module == 3:
			if self.module_lvl == 2: bonuschance += 0.1
			if self.module_lvl == 3: bonuschance += 0.2
		falloutdmg = 0.6 if self.module_lvl == 3 else 0.4
		newres = np.fmax(0,res-10)
		shreddmg = 165 if self.pot > 2 else 150	
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
			#if self.targets == 1: bonusdmg = 0
			dps = (hitdmg+bonusdmg)/(self.atk_interval/(1+aspd/100))
			if self.module == 3 and self.talent1:
				ele_gauge = 1000 if self.moduledmg else 2000
				eledps = dps * 0.08
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg /(self.atk_interval/(1+aspd/100)) * bonuschance * 15 / (fallouttime + 15)
		
		if self.skill == 2:
			scaling = 0.5 if self.mastery == 0 else 0.45 + 0.1 * self.mastery
			if self.skilldmg: scaling *= 3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * scaling * (1-newres/100), final_atk * scaling * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
			#if self.targets == 1: bonusdmg = 0
			dps = (hitdmg+bonusdmg) * 2
			if self.module == 3 and self.talent1:
				ele_gauge = 1000 if self.moduledmg else 2000
				eledps = dps * 0.08 
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg * 2 * bonuschance * 15 / (fallouttime + 15)
			
		if self.skill == 3:
			atkbuff += 3 if self.mastery == 3 else 2.2 + 0.3 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
			#if self.targets == 1: bonusdmg = 0
			dps = (hitdmg+bonusdmg)/(self.atk_interval/(1+aspd/100)) * min(self.targets,4)
			if self.module == 3 and self.talent1:
				ele_gauge = 1000 if self.moduledmg else 2000
				eledps = dps * 0.08 / min(self.targets,4)
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15) * min(self.targets,4)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,4) * bonuschance * 15 / (fallouttime + 15)
		return dps

	def get_name(self):
		if self.skill == 1:
			final_atk = self.base_atk * (1+self.buffs[0] + 0.7 + 0.1 * self.mastery) + self.buffs[1]
			limit = final_atk * (1.2 + 0.1 * self.mastery)
			self.name += f" Death@{int(limit)}HP"
		return self.name

class Lunacub(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lunacub",pp,[1,2],[2],2,1,2)
	
	def skill_dps(self, defense, res):
		atk_shorter = 0.15 if self.elite == 2 else 0
		if self.module == 2:
			atk_shorter += 0.05 * (self.module_lvl - 1)
		atk_interval = self.atk_interval * (1-atk_shorter)
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/atk_interval * (self.attack_speed+aspd)/100
		return dps

class LuoXiaohei(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LuoXiaohei",pp,[1,2],[2],2,6,2)
		self.below50 = False
		if self.skill == 2 and self.skill_dmg:
			self.below50 = True
		if self.module == 2 and self.module_lvl > 1: 
			if self.talent_dmg: self.below50 = True
			else: self.below50 = False
		if (self.module == 2 and self.module_lvl > 1) or self.skill == 2:
			if self.below50: self.name += " <50%Hp"
			else: self.name += " >50%Hp"
		if self.module == 2 and self.targets == 1 and self.module_dmg: self.name += " +12aspd(mod)"
	
	def skill_dps(self, defense, res):
		dmg_scale = 1 + 0.04 * self.module_lvl if self.below50 else 1
		aspd = 12 if self.module == 2 and (self.module_dmg or self.targets > 1) else 0
		
		if self.skill == 1:
			aspd += self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg_scale
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * min(self.targets,2) 
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg_scale
			newdef = np.fmax(defense - self.skill_params[2], 0)
			hitdmg2 = np.fmax(final_atk - newdef, final_atk * 0.05) * dmg_scale
			if self.below50:
				hitdmg += hitdmg2
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd)/ 100 * min(self.targets,2)
		return dps

class Lutonada(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lutonada",pp,[1,2],[1],2,6,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1:
			skill_scale = self.skill_params[0]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[3]
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg / 2 * self.targets
		return dps
	
class Magallan(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 443  #######including trust
		maxatk = 509
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Magallan Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Magallan P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		#Dragonstats:
		dronelvl1 = 593
		dronelvl90 = 753
		self.droneinterval = 2.3
		if self.skill == 2:
			dronelvl1 = 408
			dronelvl90 = 509
			self.droneinterval = 1.0
		self.drone_atk = dronelvl1 + (dronelvl90-dronelvl1) * (level-1) / (maxlvl-1)
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 34
				else: self.base_atk += 25
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 2 and self.module_lvl ==3:
			if self.skill == 3: self.drone_atk += 50
			if self.skill == 2: self.drone_atk += 40
		
		if not self.trait: self.name += " noDrones"   ##### keep the ones that apply
		elif not self.talent1: self.name += " 1Drone"
		else: self.name += " 2Drones"
		
		if self.targets > 1 and self.trait: self.name += f" {self.targets}targets" ######when op has aoe
		
		
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		drones = 2 if self.talent1 else 1
		if not self.trait: drones = 0
		bonusaspd = 3 if self.module == 2 and self.module_lvl == 3 else 0

		####the actual skills
		if self.skill == 2:
			aspd += 150 if self.mastery == 3 else 100 + 15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_drone = self.drone_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = np.fmax(final_drone * (1-res/100), final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+(aspd+bonusaspd)/100)) * drones * self.targets
		if self.skill == 3:
			atkbuff += 1.5 if self.mastery == 3 else 1 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_drone = self.drone_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = np.fmax(final_drone - defense, final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+(aspd+bonusaspd)/100)) * drones * self.targets
		return dps

class Manticore(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Manticore",pp,[1,2],[1],2,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		if self.skill == 2: self.atk_interval = 5.2
		atkbuff_talent = self.talent1_params[1] if self.elite > 0 else 0
		if self.module == 1 and self.module_lvl > 1: atkbuff_talent += 0.05 * (self.module_lvl -1)
		if self.elite > 0:
			if self.atk_interval/self.attack_speed*100 < self.talent1_params[0]: atkbuff_talent = 0
		atkbuff = self.skill_params[1] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + atkbuff_talent + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Marcille(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Marcille",pp,[1,2,3],[2],2,1,2)
		if self.skill == 3:
			self.talent_dmg = True
			self.name += " FullCast"
		if not self.talent_dmg: self.name += " noMana"
		self.try_kwargs(3,["squad","full","fullsquad"],**kwargs)
		if self.talent2_dmg and self.elite == 2 and self.skill != 3: self.name += " FullSquad"
		if self.skill == 2 and self.skill_dmg: self.name += " 2ndActivation"
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.talent1_params[5] if self.talent_dmg else 0
		aspd = self.talent2_params[1] if self.talent2_dmg else 0

		if self.skill == 1:
			atkbuff += self.skill_params[3]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * self.targets
		if self.skill == 2:
			atkbuff += self.skill_params[3]
			aspd += self.skill_params[5] if self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * self.targets
		if self.skill == 3:
			skill_scale = self.skill_params[6]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale *  0.05)
			dps = hitdmg * self.targets
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3: self.skill_duration = 10
		return super().total_dmg(defense, res)

class Matoimaru(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 760  #######including trust
		maxatk = 916
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Matoimaru Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Matoimaru P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 2: self.name += " afterRevive"

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 2 and self.moduledmg: aspd += 30

		if self.skill == 2:
			atkbuff += 1.05 + 0.15 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class May(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("May",pp,[1,2],[1],1,6,1)
		if self.module == 1 and self.module_dmg: self.name += " vsAerial"
		
	def skill_dps(self, defense, res):
		atkbuff = min(self.talent1_params)
		aspd = max(self.talent1_params)
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmg_skill = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			avghit = (hitdmg * self.skill_cost + hitdmg_skill)/(self.skill_cost + 1)
			dps = avghit / self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			self.atk_interval = 1.5
			final_atk = self.atk * (1 + self.buff_atk + atkbuff + self.skill_params[1]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Melantha(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Melantha",pp,[1],[],1,6,0)
		
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk + self.talent1_params[0] + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Meteor(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Meteor",pp,[1],[1],1,6,1)
		if self.module == 1: self.talent_dmg = self.talent_dmg and self.module_dmg
		if self.talent_dmg and self.elite > 0: self.name += " vsAerial"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.talent_dmg else 1
		talentscale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
			
		if self.skill == 1:
			sp_cost = self.skill_cost 
			skill_scale = self.skill_params[0]
			defshred = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmglow = np.fmax(final_atk * atk_scale * talentscale - defense, final_atk * atk_scale * talentscale * 0.05)
			hitdmg = np.fmax(final_atk * atk_scale * talentscale - defense * (1+defshred), final_atk * atk_scale * talentscale * 0.05)
			reapply_duration = (self.skill_cost+1) * self.atk_interval / self.attack_speed * 100
			avghitdmg = hitdmg * min(1, 5/reapply_duration) + hitdmglow * (1- min(1, 5/reapply_duration))
			skilldmg = np.fmax(final_atk * atk_scale * talentscale * skill_scale - defense * (1+defshred), final_atk * atk_scale * talentscale * skill_scale * 0.05)
			avgdmg = (sp_cost * avghitdmg + skilldmg) / (sp_cost + 1)
			dps = avgdmg/self.atk_interval * self.attack_speed/100
		
		return dps

class Meteorite(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 759  #######including trust
		maxatk = 950
		self.atk_interval = 2.8  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Meteorite Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Meteorite P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 37
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		cdmg = 1.6
		crate = 0.3
		newdef = defense
		if self.module == 2:
			newdef = np.fmax(0, defense - 100)
			crate += 0.1 * (self.module_lvl - 1)

		skill_scale = 1.7 + 0.15 * self.mastery
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
		hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
		hitcrit = np.fmax(final_atk * cdmg - newdef, final_atk * cdmg * 0.05)
		skillhitdmg = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05)
		skillcritdmg = np.fmax(final_atk * cdmg *skill_scale - newdef, final_atk * cdmg * skill_scale * 0.05)
		sp_cost = 3 if self.mastery == 3 else 4
		avghit = crate * hitcrit + (1-crate) * hitdmg
		avgskill = crate * skillcritdmg + (1-crate) * skillhitdmg
		avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1) * self.targets	
		dps = avgphys/(self.atk_interval/(1+aspd/100))
		return dps

class Midnight(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Midnight",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " rangedAtk"
	
	def skill_dps(self, defense, res):
		atk_scale = 1 if self.trait_dmg else 0.8
		crate = self.talent1_params[0] if self.elite > 0 else 0
		cdmg = self.talent1_params[1]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
		critdmg = np.fmax(final_atk * cdmg * atk_scale * (1-res/100), final_atk * cdmg * atk_scale * 0.05)
		avghit = crate * critdmg + (1-crate) * hitdmg
		dps = avghit / self.atk_interval * self.attack_speed / 100
		return dps

class Mizuki(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 802  #######including trust
		maxatk = 975
		self.atk_interval = 3.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mizuki Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Mizuki P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent2: self.name += " vsLowHp"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.module == 2:
			aspd += 4 + self.module_lvl
		
		bonusdmg = 0.5
		bonustargets = 1
		if self.module == 1 and self.module_lvl > 1:
			bonusdmg += 0.05 * (self.module_lvl - 1)
			bonustargets = 2
		
		if self.talent2:
			atkbuff += 0.1
			if self.pot > 4: atkbuff += 0.02
			if self.module == 2 and self.module_lvl > 1:
				atkbuff += 0.05 * (self.module_lvl -1)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 3 if self.mastery == 3 else 2.3 + 0.2 * self.mastery
			sp_cost = 8 if self.mastery < 2 else 7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitbonus = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skillbonus = np.fmax(final_atk * bonusdmg * skill_scale * (1-res/100), final_atk * bonusdmg * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			
			avghit = skilldmg
			avgarts = skillbonus
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				avgarts = (skillbonus + (atks_per_skillactivation -1) * hitbonus) / atks_per_skillactivation				
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets + avgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, bonustargets)
			
		if self.skill == 2:
			atkbuff += 0.3 if self.mastery == 3 else 0.2 + 0.03 * self.mastery
			self.atk_interval = 2 if self.mastery == 3 else 2.3
			bonustargets += 1
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets + hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, bonustargets)
		
		if self.skill == 3:
			atkbuff += 1.05 + 0.15 * self.mastery
			bonustargets += 2
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets + hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, bonustargets)
		
		return dps

class Mlynar(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mlynar",pp,[1,2,3],[],3,1,0)
		if not self.trait_dmg: self.name += " -10stacks"
		if self.elite > 0 and self.talent_dmg and self.targets < 3: self.name += " 3+Nearby"
		if self.targets > 1: self.name += f" {self.targets}targets"
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		atk_scale = 1
		if self.elite > 0: atk_scale = self.talent1_params[2] if self.talent_dmg or self.targets > 2 else self.talent1_params[0]
		stacks = 40
		if not self.trait_dmg: stacks -= 10
		atkbuff += stacks * 0.05
		
		if self.skill == 1:
			atk_scale *= self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			finaldmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = finaldmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			self.atk_interval = 1.5
			atk_scale *= self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			finaldmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * 2
			dps = finaldmg/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			atkbuff += stacks * 0.05
			atk_scale *= self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			truedmg = final_atk * self.skill_params[1] * np.fmax(1,-defense) #this defense part has to be included
			finaldmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = (finaldmg + truedmg)/self.atk_interval * self.attack_speed/100
			dps = dps * min(self.targets, 5)
		if self.hits > 0 and self.elite == 2:
			truescaling = self.talent2_params[1]
			dps += final_atk * truescaling * self.hits * np.fmax(1,-defense) #this defense part has to be included
		
		return dps

class Mon3tr(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mon3tr",pp,[1,2,3],[1,2,3],3,1,3)
		if not self.talent_dmg and self.module == 2 and self.module_lvl > 1: self.name += " NotInKalRange"
		if self.skill == 3:
			if self.skill_dmg:
				self.name += " skillStart"
			else:
				self.name += " skillEnd"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
		if self.module in [2,3]:
			self.attack_speed -= 4 + self.module_lvl #because we want mon3trs attack speed

	def skill_dps(self, defense, res):
		aspd = 0
		if self.module == 2 and self.talent_dmg:
			if self.module_lvl == 2: aspd = 12
			if self.module_lvl == 3: aspd = 20
		atkbuff = 0.25 * (self.module_lvl - 1) if self.module == 3 else 0
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.drone_atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.drone_atk_interval * (self.attack_speed+aspd)/100
		
		if self.skill == 2:
			final_atk = self.drone_atk * (1 + self.buff_atk + self.skill_params[1] + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.drone_atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,3)
		
		if self.skill == 3:
			final_atk = self.drone_atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			final_atk_start = self.drone_atk * (1 + self.buff_atk + self.skill_params[0] + atkbuff) + self.buff_atk_flat
			dps_max = final_atk_start/self.drone_atk_interval * (self.attack_speed+aspd)/100 * np.fmax(-defense, 1)
			dps_min = final_atk/self.drone_atk_interval * (self.attack_speed+aspd)/100 * np.fmax(-defense, 1)
			dps = dps_max if self.skill_dmg else dps_min
		return dps

class Morgan(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Morgan",pp,[1,2],[1],2,6,1)
		if self.elite > 0:
			if self.talent_dmg: self.name += " lowHp"
			else: self.name += " fullHp"
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 0
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		skill_scale = max(self.skill_params[:2])
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(skill_scale * final_atk * atk_scale - defense, skill_scale * final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Mostima(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mostima", pp, [1,2,3], [2,1], 3, 1, 2)
		if self.targets > 1: self.name += f" {self.targets}targets"
			
	def skill_dps(self, defense, res):
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			dps = np.fmax(final_atk  * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
		if self.skill != 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps * self.targets

class Mountain(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mountain",pp, [1,2,3],[1],2,1,1)
		if self.module == 1:
			if self.module_dmg: self.name += " >50% hp"				
			else: self.name += " <50% hp"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		crate = self.talent1_params[1]
		cdmg = self.talent1_params[0]
		aspd = 10 if self.module == 1 and self.module_dmg else 0

		if self.skill == 1:
			atk_scale = self.skill_params[0]
			hits = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			normalhitdmg = np.fmax(final_atk - defense, final_atk*0.05)
			crithitdmg = np.fmax(final_atk * cdmg-defense, final_atk*cdmg*0.05)
			avghit = crate * crithitdmg + (1-crate) * normalhitdmg
			normalskilldmg = np.fmax(final_atk * atk_scale -defense, final_atk*0.05)
			critskilldmg = np.fmax(final_atk * atk_scale * cdmg - defense, final_atk * cdmg * atk_scale * 0.05)
			avgskill = crate * critskilldmg + (1-crate) * normalskilldmg
			avgskill = avgskill * min(self.targets,2)
			avgdmg = (hits * avghit + avgskill) / (hits + 1)
			dps = avgdmg/(self.atk_interval/((self.attack_speed + aspd)/100))
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			normalhitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			crithitdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = normalhitdmg * (1-crate) + crithitdmg * crate
			dps = avgdmg/(self.atk_interval/((self.attack_speed + aspd)/100)) * min(self.targets , 2)
		if self.skill == 3:
			atk_interval = self.atk_interval * 1.7
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[1]) + self.buff_atk_flat
			normalhitdmg = np.fmax(final_atk-defense, final_atk*0.05)
			crithitdmg = np.fmax(final_atk*cdmg-defense, final_atk*cdmg*0.05)
			crate = self.skill_params[2]
			targets = self.skill_params[4]
			avgdmg = normalhitdmg * (1-crate) + crithitdmg * crate
			dps = 2 * avgdmg/(atk_interval/((self.attack_speed + aspd)/100)) * min(self.targets,targets)
		return dps

class Mousse(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mousse", pp, [1,2],[],1,6,0)
	
	def skill_dps(self, defense, res):
		crate = self.talent1_params[0]
		atkbuff = self.skill_params[0]
		####the actual skills
		if self.skill == 1:
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			final_atk2 = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg2 = np.fmax(final_atk2 * (1-res/100), final_atk2 * 0.05)
			avgdmg = (hitdmg * sp_cost + hitdmg2) / (sp_cost + 1)
			dps = avgdmg/(self.atk_interval/(self.attack_speed/100)) * (1+crate)
		
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * (1+crate)
		return dps

class MrNothing(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 641  #######including trust
		maxatk = 765
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"MrNothing Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"MrNothing P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skilldmg and self.skill == 2: self.name += " Apsd+Skill"
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1

		if self.skill == 2:
			atkbuff += 0.4 if self.mastery == 0 else 0.45 + 0.05 * self.mastery
			if self.skilldmg:
				aspd += 28 if self.mastery > 1 else 25
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
		
class Mudrock(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 687  #######including trust
		maxatk = 882
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mudrock Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Mudrock P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(3,max(1,targets))
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 55
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.buffs = buffs
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0 and self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.skill == 2:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)	
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
			if self.hits > 0:
				atk_scale = 2.1 + 0.2 * self.mastery
				skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)	
				spcost = 5 if self.mastery == 0 else 4
				skillcycle = spcost / self.hits + 1.2
				dps += skilldmg / skillcycle * self.targets
				
		if self.skill == 3:
			self.atk_interval = 0.7*1.6
			atkbuff += 1 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		return dps
	
class Muelsyse(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 447  #######including trust
		maxatk = 537
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.arts = False
		self.ranged = True
		self.summon_atk = 50
		self.summon_interval = 0.85
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Muelsyse Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Muelsyse P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 25
				elif self.module_lvl == 2: self.base_atk += 20
				else: self.base_atk += 15
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " No Mod"
		else: self.module = 0
		
		if not self.skill == 3: self.trait = self.trait and self.talent1
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1.5 if self.trait else 1
		
		#talent/module buffs
		summonatk = self.summon_atk * 0.9 if self.module == 0 or self.module_lvl == 1 else self.summon_atk
		
		atkbuff += 0.35 + 0.05 * self.mastery
		####the actual skills
		if self.skill == 1:
			aspd += 35 + 5 * self.mastery
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		main = 1 if self.talent1 else 0
		final_summonatk = summonatk * (1+atkbuff) + self.buffs[1]
		if not self.ranged and self.talent2: final_summonatk += 250
		summondamage = np.fmax(final_summonatk * (1-res/100), final_summonatk * 0.05) if self.arts else np.fmax(final_summonatk - defense, final_summonatk * 0.05)
		extra_summons = 0
		extra_summons_skill = 0
		if self.ranged and self.talent1: 
			extra_summons += min(4,2.5/(self.summon_interval/(1+aspd/100)))
			if self.skill != 3: extra_summons_skill =  min(4,2.5/(self.summon_interval/(1+aspd/100)) * 2) if self.skill == 2 else min(4,2.5/(self.summon_interval/(1+(aspd-35-5*self.mastery)/100)))
			extra_summons = (50 * extra_summons + 15 * extra_summons_skill) / 65
			
		if self.skill == 3 and self.ranged:
			extra_summons = 4 if self.skilldmg else 2
			dps += (main+extra_summons) * summondamage/(self.summon_interval/(1+aspd/100))
		elif not self.skilldmg:
			extra_summons = 0
		if self.skill == 2 and self.ranged:
			dps += (main+extra_summons) * summondamage/(self.summon_interval/(1+aspd/100)) * 2
		elif self.skill != 3 or (self.skill == 3 and not self.ranged):
			dps += (main+extra_summons) * summondamage/(self.summon_interval/(1+aspd/100))
		return dps

def name_addition(S123,ranged,TrTaTaSkMo):
	name = ""
	trait,talent1,talent2,skill,module = TrTaTaSkMo
	if not ranged:
		if not talent1: name+= " no clone"
		else:
			if trait: name += " blocked"
			if talent2: name+= " maxSteal"
	elif S123 == 3:
		clones = 5
		if not talent1: clones -= 1
		if not skill: clones -= 2
		name += f" {clones}clones"
		if trait: name += " blocking"
	elif talent1:
		if skill: name += " averagedClonecount"
		else: name += " 1clone"
	else: name+= " no clones"
	return name
	
class MumuDorothy(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Dorothy(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Dorothy)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuEbenholz(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pp,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Ebenholz(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Ebenholz)" + self.name[8:]
		self.ranged = True
		self.arts = True
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuCeobe(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Ceobe(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Ceobe)" + self.name[8:]
		self.ranged = True
		self.arts = True
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)
		
class MumuMudrock(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Mudrock(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Mudrock)" + self.name[8:]
		self.ranged = False
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuRosa(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Rosa(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Rosa)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuSkadi(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Skadi(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Skadi)" + self.name[8:]
		self.ranged = False
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuSchwarz(Muelsyse):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Schwarz(pp,lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Schwarz)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class Narantuya(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 636  #######including trust
		maxatk = 765
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Narantuya Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Narantuya P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		

		if not self.trait: self.name += " maxRange"
		else: self.name += " minRange"
		if self.talent1: self.name += " maxSteal"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		stealbuff = 0
		if self.talent1: stealbuff = 270 if self.pot > 4 else 250

			
		####the actual skills
		
		
		
		if self.skill == 3:
			skill_scale = 1.6 + 0.05 * self.mastery
			aoe_scale = 1.6 if self.mastery == 3 else 1.4 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1] + stealbuff
			
		
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			aoedmg = np.fmax(final_atk * aoe_scale - defense, final_atk * aoe_scale * 0.05)
			if not self.trait: aoedmg = 0
			
			interval = 20/13.6 if not self.trait else (self.atk_interval/(1+aspd/100))
			dps = 3 * hitdmg/interval + min(self.targets,3) * aoedmg/interval
		return dps

class NearlAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("NearlAlter",pp,[1,2,3],[1,2],3,1,1)
		if self.module_dmg: 
			if self.module == 1: self.name += " blockedTarget"
			if self.module == 2: self.name += " afterRevive"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		aspd = 30 if self.module == 2 and self.module_dmg else 0
		def_shred = self.talent2_params[0] if self.elite == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		if self.skill == 1: aspd += self.skill_params[1]
		hitdmg = np.fmax(final_atk * atk_scale - defense * (1 - def_shred), final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Nian(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 513  #######including trust
		maxatk = 619
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 2: self.base_atk += 24
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Nian Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Nian P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.moduledmg = TrTaTaSkMo[4] and TrTaTaSkMo[2]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 35
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 35
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.module_lvl > 1 and self.moduledmg: self.name += " 3shieldsBroken"
		
		self.buffs = buffs
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg and self.module_lvl > 1:
			atkbuff += 3 * 0.05 if self.module_lvl == 2 else 3 * 0.07
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.3 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atk_scale = 0.7 if self.mastery == 0 else 0.6 + 0.1 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps += hitdmg * self.hits
		
		if self.skill == 3:
			atkbuff += 1.2 if self.mastery == 3 else 0.8 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Nymph(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 640  #######including trust
		maxatk = 745
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Nymph Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Nymph P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		stacks = 12 if self.pot > 4 else 10
		if self.talent2: self.name += f" {stacks}stacks"
	
		if self.trait and self.talent1: self.name += " vsFallout(not inlcuding 800FalloutDps)"

		
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		final_atk = 0
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 0.24 if self.pot > 4 else 0.2

			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.8 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			eledmg = 0
			if self.trait and self.talent1:
				eledmg = final_atk * 0.5 if self.mastery == 3 else final_atk * 0.4
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			sp_cost = 14 - self.mastery
			if self.mastery > 1: sp_cost += 1
			
			atk_scale = 3 if self.mastery == 0 else 3.4 + 0.2 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05) * self.targets
			
			sp_cost = sp_cost+ 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skill = int(sp_cost/atkcycle)
			avghit = (hitdmg * atks_per_skill + skilldmg) / (atks_per_skill + 1)	
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		
		if self.skill == 3:
			atkbuff += 1.7 if self.mastery == 0 else 1.75 + 0.15 * self.mastery
			aspd += 60 if self.mastery > 1 else 45
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			if self.trait and self.talent1:
				hitdmg = final_atk * np.fmax(1,-res)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		
		extra_dmg = 0
		if self.talent1 and self.trait:
			dmg_rate = 0.4
			if self.skill == 2:
				dmg_rate = 0.85 + 0.05 * self.mastery
			extra_dmg = final_atk * dmg_rate
		
		return dps + extra_dmg


class Odda(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 1057  #######including trust
		maxatk = 1260
		self.atk_interval = 1.8   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Odda Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Odda P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.talent1 = TrTaTaSkMo[1]	
		
		if self.talent1: self.name += " after30Hits"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.15
			if self.pot > 4: atkbuff += 0.03
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.8 + 0.2 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
				
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			splashhitdmg = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			splashskillhitdmg = np.fmax(0.5 * final_atk * atk_scale * skill_scale - defense, 0.5 * final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avgsplash = (sp_cost * splashhitdmg + splashskillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps += avgsplash/(self.atk_interval/(1+aspd/100)) * (self.targets - 1)
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
	
class Pallas(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pallas",pp,[1,2,3],[1,2],1,1,1)
		if not self.trait_dmg: self.name += " w/o trait"
		if self.elite > 0 and not self.talent_dmg: self.name += " w/o vigor"
		if self.skill == 3 and not self.talent_dmg: self.skill_dmg = False
		if self.skill == 3 and self.skill_dmg: self.name += " selfbuffS3"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = 1
		atkbuff = min(self.talent1_params) if self.talent_dmg and self.elite > 0 else 0
		if self.trait_dmg: 
			atk_scale = 1.3 if self.module == 1 else 1.2
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100
			
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100	
		
		if self.skill == 3:
			if self.skill_dmg:
				atkbuff = max(atkbuff, self.skill_params[2]) #vigor doesnt stack
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100	 * min(self.targets, 3)
				
		return dps

class Passenger(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 656  #######including trust
		maxatk = 774
		self.atk_interval = 2.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Passenger Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Passenger P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]

		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 80
				else: self.base_atk += 65
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 100
				elif self.module_lvl == 2: self.base_atk += 85
				else: self.base_atk += 70
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " vsHighHp"
		if self.talent2: self.name += " NoClosebyEnemy"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1: aspd += 5
		targetscaling = [0,1,2,3,4,5] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3, 1.85+0.85**2+0.85**3+0.85**4]
		if self.module == 1: targetscaling = [0, 1, 1.9, 1.9+0.9**2, 1.9+0.9**2+0.9**3, 1.9+0.9**2+0.9**3+0.9**4]
		targets = min(5, self.targets) if self.skill == 2 else min(4, self.targets)
		
		dmg_scale = 1
		if self.talent1:
			dmg_scale = 1.25 if self.pot == 6 else 1.2
			if self.module == 2:
				if self.module_lvl == 2: dmg_scale += 0.05
				if self.module_lvl == 3: dmg_scale += 0.08
		
		sp_boost = 0
		if self.talent2:
			atkbuff += 0.1 if self.pot > 2 else 0.08
			if self.module == 1 and self.module_lvl > 1:
				sp_boost = 0.05 + 0.1 * self.module_lvl
		
		####the actual skills
		if self.skill == 1:
			sp_cost = 5 if self.mastery == 3 else 6
			
			atk_scale = 2.5 if self.mastery == 3 else 2.1 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			
			sp_cost = sp_cost/(1+sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skill = int(sp_cost/atkcycle)
			avghit = (hitdmg * atks_per_skill + skilldmg) / (atks_per_skill + 1)	
			dps = avghit/(self.atk_interval/(1+aspd/100)) * targetscaling[targets]

		
		if self.skill == 2:
			atkbuff += 0.3 if self.mastery == 3 else 0.2 + 0.05 * self.mastery
			self.atk_interval = 2.3 * 0.5 if self.mastery == 3 else 2.3 * 0.6
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * targetscaling[targets]
		
		if self.skill == 3:
			skill_scale = 1.5 if self.mastery == 3 else 1.3 + 0.05 * self.mastery
			sp_cost = 30 if self.mastery == 3 else 34 - self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skillhit = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * targetscaling[targets]
			dps += 8 * skillhit / (sp_cost/(1+sp_boost)+1.2)

		return dps*dmg_scale

	def total_dmg(self, defense, res):
		if self.skill == 3:
			atkbuff = self.buffs[0]
			dmg_scale = 1
			if self.talent1:
				dmg_scale = 1.25 if self.pot == 6 else 1.2
				if self.module == 2:
					if self.module_lvl == 2: dmg_scale += 0.05
					if self.module_lvl == 3: dmg_scale += 0.08
			if self.talent2:
				atkbuff += 0.1 if self.pot > 2 else 0.08
				if self.module == 1 and self.module_lvl > 1:
					sp_boost = 0.05 + 0.1 * self.module_lvl
				skill_scale = 1.5 if self.mastery == 3 else 1.3 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhit = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dmg = 8 * skillhit * dmg_scale
			return(dmg)
		else:
			return(self.skill_dps(defense,res))

class Penance(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Penance", pp, [1,2,3], [1,2],3,1,1)
		if self.module == 2 and self.module_dmg: self.name += " alone"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.elite < 2: self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 2 and self.module_dmg else 0

		if self.skill == 1:
			atk_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk  * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + atks_per_skillactivation * hitdmg) / atks_per_skillactivation
			dps = avghit / self.atk_interval * self.attack_speed/100
		
		if self.skill == 2:
			atk_scale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
		if self.skill == 3:
			atk_interval = 2.5
			atkbuff += self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(atk_interval/(self.attack_speed/100))
		
		if self.hits > 0:
			arts_scale = self.talent2_params[0]
			artsdmg = np.fmax(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05)
			dps += artsdmg * self.hits	
		
		return dps

class Pepe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pepe",pp,[1,2,3],[],3,1,0)
		self.try_kwargs(4,["stacks","maxstacks","max","nostacks"],**kwargs)
		if self.skill_dmg and not self.skill == 1: self.name += " maxStacks"
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.skill == 1 and self.sp_boost > 0: self.name += f" +{self.sp_boost}SP/s"		
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent2_params[0]

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) + np.fmax(0.5 * final_atk - defense, 0.5 *final_atk * 0.05) * (self.targets-1)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) + np.fmax(0.5 * skill_scale * final_atk - defense, 0.5 * skill_scale * final_atk * 0.05) * (self.targets-1)
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[0] > 2.4: #a bit of a redneck way, but the json data doesnt seem to include the skill charge count...
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/(self.atk_interval/(self.attack_speed/100))

		if self.skill == 2:
			atkbuff += self.skill_params[0]
			aspd = self.skill_params[1]
			if self.skill_dmg:
				aspd += 2 * self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgaoe = np.fmax(0.5 * final_atk - defense, 0.5 * final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) + hitdmgaoe/(self.atk_interval/((self.attack_speed+aspd)/100))*(self.targets - 1)
		
		if self.skill == 3:
			self.atk_interval = 2
			atkbuff += self.skill_params[0]
			if self.skill_dmg:
				atkbuff += 4 * self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgaoe = np.fmax(0.5 * final_atk - defense, 0.5 * final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) + hitdmgaoe/(self.atk_interval/(self.attack_speed/100))*(self.targets - 1)
		return dps

class Phantom(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 525  #######including trust
		maxatk = 648
		lvl1clone = 429
		maxclone = 548
		self.atk_interval = 0.93   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.clone_atk = lvl1clone + (maxclone-lvl1clone) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 2: self.base_atk += 22
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Phantom Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Phantom P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 73
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: 
					self.base_atk += 75
					self.clone_atk += 60
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 40
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.mastery == 3: self.name += " 10hitAvg"
		else: self.name += " 9hitAvg"
		if not self.talent: self.name += " w/o clone"   ##### keep the ones that apply
		if not self.moduledmg and self.module == 2: self.name += " adjacentAllies"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		selfhit = 0
		clonehit = 0
		mainbuff = 0.1 if self.module == 2 and self.moduledmg else 0
		if self.module == 2:
			if self.module_lvl > 1 and self.talent: atkbuff += 0.1
		
		rate = 0.2 if self.mastery == 3 else 0.16 + 0.01 * self.mastery
		count = 10 if self.mastery == 3 else 9
		for i in range(count):
			atkbuff += rate
			final_atk = self.base_atk * (1+atkbuff + mainbuff) + self.buffs[1]
			final_clone = self.clone_atk * (1+atkbuff) + self.buffs[1]
			selfhit += np.fmax(final_atk - defense, final_atk * 0.05)
			clonehit += np.fmax(final_clone - defense, final_clone * 0.05)
						
		dps = selfhit /(self.atk_interval/(1+aspd/100)) / count
		if self.talent:
			dps += clonehit /(self.atk_interval/(1+aspd/100)) / count
		return dps

class Pinecone(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pinecone", pp, [1,2],[1],1,6,1)
		if self.skill == 1 and not self.trait_dmg: self.name += " maxRange"   
		if self.skill == 1 and self.talent_dmg: self.name += " withSPboost"
		if self.skill == 2:
			if self.skill_dmg: self.name += " 4thActivation"
			else: self.name += " 1stActivation"
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atk_scale = 1
		if self.trait_dmg or self.skill == 2: atk_scale = 1.6 if self.module == 1 else 1.5
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			defignore = self.skill_params[1]
			newdef = np.fmax(0, defense - defignore)
			sp_cost = self.skill_cost +1.2 #sp_lockout
			final_atk = self.atk * (1+ self.buff_atk) + self.buff_atk_flat
			if self.talent_dmg: sp_cost = sp_cost / (1+ self.talent1_params[0])
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * self.targets + skilldmg / sp_cost * self.targets
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			if self.skill_dmg: atkbuff += 0.6
			final_atk = self.atk * (1+ atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * self.targets
		return dps

class Pith(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pith",pp,[1],[],1,1,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		newres = np.fmax(0, res - self.talent1_params[0])
		atkbuff = self.skill_params[0]
		aspd = self.skill_params[1]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps*self.targets

class Platinum(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Platinum",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " aerial target"
		
	def skill_dps(self, defense, res):
		aspd = -20 if self.skill == 2 else 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + max(self.skill_params) + self.buff_atk) + self.buff_atk_flat
		if self.elite > 0:
			extra_scale = self.talent1_params[3] - 1
			atk_cycle = self.atk_interval /(self.attack_speed + aspd) * 100
			charge_time = max(atk_cycle - 1, 0)
			weight = min(1, charge_time / 1.5)
			atk_scale *= 1 + weight * extra_scale
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		return dps

class Plume(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Plume",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + self.skill_params[1]) / 100
		return dps

class Popukar(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Popukar",pp,[1],[],1,6,0)
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100 * min(self.targets,2)
		return dps

class Pozemka(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 744  #######including trust
		maxatk = 946
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.typewriter_atk = 666 + 200 * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Pozemka Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Pozemka P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3:
					self.base_atk += 75
					self.typewriter_atk += 70				
				elif self.module_lvl == 2:
					self.base_atk += 65
					self.typewriter_atk += 50
				else: self.base_atk += 55
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if not self.talent1:
			self.name += " w/o Typewriter"
			self.talent2 = False
		elif not self.talent2: self.name += " TW separate"
		else: self.name += " AdjacentTW"
		
		if self.skill == 3:
			self.moduledmg = self.moduledmg and self.skilldmg
		if self.module == 2 and self.moduledmg: self.name += " DirectFront"
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		defshred = 0
		if self.talent1:
			if self.talent2:
				defshred = 0.25 if self.pot > 4 else 0.23
			else:
				defshred = 0.2 if self.pot > 4 else 0.18
		newdef = defense * (1-defshred)
		if self.moduledmg and self.module == 2:
			atk_scale = 1.05
			
		if self.skill == 3:
			self.atk_interval = 1
			skill_scale = 1.7 + 0.1 * self.mastery
			skill_scale2 = 2.1 + 0.15 * self.mastery
			if self.mastery < 2: skill_scale2 += 0.05

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			if self.moduledmg or self.skilldmg:
				hitdmg = np.fmax(final_atk * atk_scale * skill_scale2 - newdef, final_atk * atk_scale * skill_scale2 * 0.05)	
			
			hitdmgTW = 0
			if self.talent1:
				hitdmgTW = np.fmax(self.typewriter_atk * skill_scale2 - newdef, self.typewriter_atk * skill_scale2 * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgTW

		return dps

class ProjektRed(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ProjektRed", pp,[1],[2],1,1,2)
		if self.module_dmg and self.module == 2: self.name += " alone"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.1 if self.module_dmg and self.module == 2 else 0
		mindmg = 0.05 if self.elite == 0 else self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * mindmg)
		dps = hitdmg / self.atk_interval * self.attack_speed/100
		return dps

class Provence(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 691  #######including trust
		maxatk = 871
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Provence Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Provence P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent: self.name += " directFront"
		if self.skill == 1:
			if self.skilldmg: self.name += " vs<20%Hp"
			else: self.name += " vsFullHp"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		crate = 0.5
		cdmg = 1.9 if self.pot > 4 else 1.8
		if self.module == 1:
			crate += 0.05 * (self.module_lvl - 1)
			cdmg += 0.05 * (self.module_lvl - 1)
		if not self.talent: crate = 0.2
					
		####the actual skills
		if self.skill == 1:
			if self.skilldmg: atkbuff += 4 * (0.16 + 0.03 * self.mastery)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avghit =  crate * critdmg + (1-crate) * hitdmg
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 1.6 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avghit =  crate * critdmg + (1-crate) * hitdmg
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		return dps

class Pudding(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 519  #######including trust
		maxatk = 612
		self.atk_interval = 2.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 4: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Pudding Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Pudding P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 0.1
		if self.module == 2:
			aspd += 4
			if self.module_lvl > 1: aspd += 1
			atkbuff += 0.03 * (self.module_lvl -1)
		
		targetscaling = [0,1,2,3,4] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3]
		targets = min(4, self.targets)
		####the actual skills
		if self.skill == 1:
			aspd += 45 + 10 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = hitdmg/(self.atk_interval/(1+aspd/100)) * targetscaling[targets]
		
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))  * targetscaling[targets]
		return dps

class Qiubai(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 631 #######including trust
		maxatk = 768
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Qiubai Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Qiubai P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 48
				else: self.base_atk += 35
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		#if not self.trait: self.name += "w/o trait"   ##### keep the ones that apply
		if self.talent1:
			if self.module == 1 and self.moduledmg and self.module_lvl > 1:
				self.name += " vsBindANDslow"
			else: self.name += " vsBind/Slow"
		#if not self.talent2: self.name += " w/o talent2"
		if self.skill ==3:
			if self.skilldmg: self.name += " maxStacks"
			else: self.name += " noStacks"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.module == 1: aspd += 4 + self.module_lvl
		
		bonus = 0.1 if self.module == 1 else 0
		extrascale = 0
		#talent/module buffs
		if self.talent1:
			extrascale = 0.4 if self.pot < 5 else 0.43
			if self.module == 1 and self.module_lvl > 1: extrascale += 0.05
			if self.module == 1 and self.moduledmg and self.module_lvl > 1:
				atk_scale = 1.2 if self.module_lvl == 3 else 1.1
			
		####the actual skills
		if self.skill == 3:
			atkbuff += 0.4 + 0.05 * self.mastery
			maxstacks = 6 if self.mastery == 0 else 5 + self.mastery
			if not self.skilldmg: maxstacks = 0
			aspd += maxstacks * 13
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = np.fmax(final_atk * atk_scale *  (1+extrascale) * (1-res/100), final_atk* atk_scale * (1+extrascale) * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmgarts+bonusdmg)/(self.atk_interval/(1+aspd/100)) * min(3, self.targets)
		return dps
	
class Quartz(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Quartz",pp,[1,2],[1],1,6,1)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1]
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			aspd = self.skill_params[1]
			skill_scale = self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps * min(self.targets,2)

class Rangers(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Rangers",pp,[],[],0,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg and self.talent1_params[0] > 1: self.name += " vsAerial"
		if pp.pot > 2: self.attack_speed += 6
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg else 1
		final_atk = self.atk * (1  + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Ray(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1020  #######including trust
		maxatk = 1192
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 37
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ray Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ray P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		 ##### keep the ones that apply
		if self.talent1: self.name += " with pet"
		if self.talent2: self.name += " After3Hits"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1.2
		dmg_scale = 1
		
		if self.talent1:
			dmg_scale = 1.15
			if self.module == 1:
				if self.module_lvl == 2: dmg_scale += 0.03
				if self.module_lvl == 3: dmg_scale += 0.05
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 3 * 0.08
			if self.pot > 4:
				atkbuff += 3 * 0.01
			
		####the actual skills
		if self.skill == 2:
			atkbuff += 0.9 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atk_scale *= 2.7 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			dps = hitdmg/(self.atk_interval/(1+aspd/100))  
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * 8 * (self.atk_interval/(1+self.buffs[2]/100)))
		else:
			return(self.skill_dps(defense,res))
	
class ReedAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ReedAlter",pp,[1,2,3],[1],2,1,1)
		self.try_kwargs(4,["sandwich","sandwiched","nosandwich","notsandwiched","notsandwich","nosandwiched"],**kwargs)
		if not self.talent_dmg and not self.skill == 3 and self.elite > 0: self.name += " w/o cinder"
		elif not self.skill == 3 and self.elite > 0: self.name += " withCinder"
		if self.skill_dmg and self.skill == 2: self.name += " Sandwiched"
		if self.targets > 1 and self.skill > 1: self.name += f" {self.targets}targets"
		if self.skill == 3:
			final_atk = self.atk * (1 + self.skill_params[1] + self.buff_atk) + self.buff_atk_flat
			nukedmg = final_atk * self.skill_params[3] * (1+self.buff_fragile)
			self.name += f" ExplosionDmg:{int(nukedmg)}"
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent1_params[2] if (self.talent_dmg and self.elite > 1) or self.skill == 3 else 1
		
		if self.skill == 1:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_scale = self.skill_params[1]
			multiplier = 2 if self.skill_dmg else 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(1-res/100,  0.05) * final_atk * atk_scale * dmg_scale * multiplier
			dps = hitdmgarts/0.8 * self.targets  #/1.5 * 3 (or /0.5) is technically the limit, the /0.8 come from the balls taking 2.4 for a rotation 
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			atk_scale = self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			directhits = np.fmax(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale
			atkdps = directhits/self.atk_interval * self.attack_speed/100 * min(self.targets,2)
			skillhits = np.fmax(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale * atk_scale
			skilldps = self.targets * skillhits
			dps = atkdps + skilldps
		return dps
	
class Rockrock(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 328  #######including trust
		maxatk = 380
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Rockrock Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Rockrock P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 18
				elif self.module_lvl == 2: self.base_atk += 15
				else: self.base_atk += 13
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.talent: self.name += " w/o talent"
		if self.skilldmg and self.skill == 2: self.name += " overdrive"
		elif self.skill == 2: self.name += " w/o overdrive"
		if not self.trait: self.name += " minDroneDmg"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		drone_dmg = 1.1
				
		if self.talent:
			atkbuff +=  0.16
			if self.pot > 4:
				atkbuff += 0.04
			if self.module == 1 and self.module_lvl == 3: aspd += 5
		
		if not self.trait:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		
		if self.skill == 1:
			aspd += 60 + 10 * self.mastery
		else:
			aspd += 60 + 5 * self.mastery
			if self.mastery == 3: aspd += 5
			if self.skilldmg:
				atkbuff += 0.5
				if self.trait:
					drone_dmg *= 1.7 + 0.1 * self.mastery

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		drone_atk = drone_dmg * final_atk
		
		dmgperinterval = final_atk + drone_atk
		
		hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps

class Rosa(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Rosa",pp,[1,2,3],[1],2,1,1)
		self.try_kwargs(2,["heavy","vsheavy","light","vslight","vs"],**kwargs)
		if self.module == 1: self.talent_dmg = self.talent_dmg and self.module_dmg
		if self.elite > 0:
			if not self.talent_dmg: self.name += " vsLight"
			else: self.name += " vsHeavy"
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent2_params[0]
		atk_scale = 1
		additional_scale = 0
		defshred = 0
		if self.talent_dmg: #aka: if heavy
			if self.elite > 0: defshred = 0.2 + 0.2 * self.elite
			if self.module == 1:
				atk_scale = 1.15
				if self.module_lvl == 2: additional_scale = 0.4
				if self.module_lvl == 3: additional_scale = 0.6
		newdef = defense * (1-defshred)

		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = np.fmax(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg)/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = np.fmax(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg)/self.atk_interval * self.attack_speed/100 * min(self.targets,2)
		if self.skill == 3:
			atkbuff += self.skill_params[2]
			maxtargets = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = np.fmax(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg) * min(self.targets,maxtargets)
		return dps

class Rosmontis(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Rosmontis",pp,[1,2,3],[1],3,1,1)
		self.try_kwargs(4,["pillar","pillarshred","pillardefshred","nopillardefshred","nopillarshred","nopillar"],**kwargs)
		if self.skill == 3 and self.skill_dmg: self.name += " withPillarDefshred"
		if self.skill == 3 and self.targets > 1: self.name += " TargetsOverlap"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
	
	def skill_dps(self, defense, res):
		bonushits = 2 if self.module == 1 else 1
		defshred = self.talent1_params[0] if self.elite > 0 else 0
		newdef = np.fmax(0, defense - defshred)
	
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + self.talent2_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk  * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - newdef, final_atk * 0.5 * 0.05) * bonushits
			skillhitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avghit = ((sp_cost + 1) * (hitdmg + bonushitdmg) + skillhitdmg) / (sp_cost + 1)
			dps = avghit/self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 2:
			self.atk_interval = 3.15
			bonushits += 2
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[1] + self.talent2_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - newdef, final_atk * 0.5 * 0.05) * bonushits
			dps = (hitdmg+ bonushitdmg)/self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 3:
			self.atk_interval = 1.05
			if self.skill_dmg:
				if self.shreds[0] < 1 and self.shreds[0] > 0:
					defense = defense / self.shreds[0]
				newdef= np.fmax(0, defense - 160)
				if self.shreds[0] < 1 and self.shreds[0] > 0:
					newdef *= self.shreds[0]
				newdef = np.fmax(0,newdef - defshred)
			else:
				newdef = np.fmax(0, defense- defshred)
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[1] + self.talent2_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - newdef, final_atk * 0.5 * 0.05) * bonushits
			dps = (hitdmg+ bonushitdmg)/self.atk_interval * self.attack_speed/100 * self.targets * min(self.targets,2)
		return dps
	
class Saga(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 519  #######including trust
		maxatk = 615
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Saga Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Saga P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 45
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " blocking"
		if self.module == 1 and self.module_lvl > 1 and self.talent: self.name += " vsLowHp"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		dmg = 0
		if self.module == 1:
			if self.moduledmg: atkbuff += 0.08
			if self.talent:
				if self.module_lvl == 2: dmg = 0.1
				if self.module_lvl == 3: dmg = 0.15
			
		####the actual skills
		if self.skill == 2:
			skill_scale = 4 if self.mastery == 3 else 3.2 + 0.2 * self.mastery
			if self.mastery == 2: skill_scale += 0.1
			sp_cost = 16 - self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * min(self.targets,6)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			self.atk_interval = 1.55
			atkbuff += 1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps * (1+dmg)

class Scavenger(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Scavenger",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 0 and not self.talent_dmg: self.name += " adjacentAlly"
		if self.module == 1 and self.module_dmg: self.name += " blocking"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		atkbuff += self.talent1_params[0] if self.talent_dmg else 0
		atkbuff += self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class Scene(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Scene",pp,[1,2],[1],2,6,1)
		if not self.trait_dmg: self.name += " noDrones" 
		elif not self.talent_dmg: self.name += " 1Drone"
		else: self.name += " 2Drones"
	
	def skill_dps(self, defense, res):
		drones = 2 if self.talent_dmg else 1
		if not self.trait_dmg: drones = 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps =  hitdmg/self.atk_interval * self.attack_speed/100
		final_atk_drone = self.drone_atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		hitdmgdrone = np.fmax(final_atk_drone - defense , final_atk_drone * 0.05)
		dps += hitdmgdrone/self.drone_atk_interval * self.attack_speed/100 * drones
		return dps
	
class Schwarz(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Schwarz", pp, [1,2,3],[1,2],3,1,1)
		if self.skill == 3:
			if self.module == 2: self.module_dmg = True
			self.talent_dmg == True
		
		if not self.talent_dmg and not self.skill == 3 and self.elite > 0: self.name += " minDefshred"
		if self.elite == 2 and not self.talent2_dmg: self.name += " w/o2ndSniper"
		if self.module_dmg and self.module == 2 and not self.skill == 3: self.name += " directFront"
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2_dmg:
			atkbuff += self.talent2_params[0]

		crate = 0.2
		cdmg = 1.6
		defshred = 0.1 * self.elite
		if self.module == 2:
			cdmg += 0.05 * (self.module_lvl -1)
			if self.module_lvl > 1: defshred = 0.25
		
		newdef = defense * (1-defshred)
		if self.module == 2 and self.module_dmg:
			atk_scale = 1.05

		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			crate2 = self.skill_params[1]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat		
			if self.talent_dmg: hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			else: hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			if self.talent_dmg: skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			else: skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			skillcrit = np.fmax(final_atk * atk_scale * cdmg * skill_scale - newdef, final_atk * atk_scale * cdmg* skill_scale * 0.05)
			avghit = crate * critdmg + (1-crate) * hitdmg
			avgskill = crate2 * skillcrit + (1-crate2) * skilldmg
			
			sp_cost = self.skill_cost
			avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 2:
			crate = self.skill_params[1]
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			if self.talent_dmg: hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			else: hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			avghit = crate * critdmg + (1-crate) * hitdmg
			dps = avghit/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 3:
			atk_interval = self.atk_interval + 0.4
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			critdmg = np.fmax(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			dps = critdmg/(atk_interval/(self.attack_speed/100))	
		
		return dps

class Shalem(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 618  #######including trust
		maxatk = 729
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Shalem Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Shalem P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		
		if self.talent1: self.name += " (in IS2)"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.talent1:
			atkbuff += 0.15
			aspd += 30
		newres = res * 0.75
		crate = 0.25 if self.pot > 4 else 0.2

		####the actual skills
		if self.skill == 1:
			self.atk_interval = 1.6 * 0.55 if self.mastery == 3 else 1.6 * 0.65
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			countinghits = int(3 /(self.atk_interval/(1+aspd/100))) + 1
			nocrit = (1-crate)**countinghits
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			shreddmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit) 
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		
		if self.skill == 2:
			hits = 6
			atk_scale = 0.65 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			countinghits =  (6 * int(3 /(self.atk_interval/(1+aspd/100))) + 3)/self.targets + 1
			nocrit = (1-crate)**countinghits
			
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			shreddmg = np.fmax(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit)
			dps = 6 * avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Sharp(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Sharp",pp,[1],[],1,1,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk + self.talent1_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * self.skill_params[1] - defense, final_atk * self.skill_params[1] * 0.05)
		dps =  hitdmg / self.atk_interval * (self.attack_speed) / 100
		return dps

class Siege(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 482  #######including trust
		maxatk = 575
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Siege Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Siege P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 60
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 82
				elif self.module_lvl == 2: self.base_atk += 74
				else: self.base_atk += 65
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " blocking"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs

		atkbuff += 0.1 if self.pot > 4 else 0.08
		if self.module == 1:
			if self.moduledmg: atkbuff += 0.08
			if self.module_lvl == 2: atkbuff += 0.06
			if self.module_lvl == 3: atkbuff += 0.08
			
		####the actual skills
		
		if self.skill == 2:
			skill_scale = 2.8 + 0.2 * self.mastery
			sp_cost = 11 if self.mastery == 0 else 10
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * self.targets
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			self.atk_interval = 2.05
			atk_scale = 3.2 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class SilverAsh(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SilverAsh",pp ,[1,2,3],[1],3,1,1)
		self.try_kwargs(5,["vselite","elite","vs"],**kwargs)
		if not self.trait_dmg and not self.skill == 3: self.name += " rangedAtk"   ##### keep the ones that apply
		if self.module == 1 and self.module_dmg and self.talent_dmg: self.name += " vsElite"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		atk_scale = 1
		if not self.trait_dmg and self.skill != 3: 
			atk_scale = 0.8
		atkbuff = self.talent1_params[0]
		
		if self.module == 1:
			if self.module_lvl == 2:
				if self.talent_dmg and self.module_dmg: atk_scale *= 1.1
			if self.module_lvl == 3:
				if self.talent_dmg and self.module_dmg: atk_scale *= 1.15
		
		bonus = 0.1 if self.module == 1 else 0
		
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat		
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2* skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(self.attack_speed/100)) + bonusdmg/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 2:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) + bonusdmg/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 3:
			atkbuff += self.skill_params[1]
			targets = self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * min(self.targets, targets) + bonusdmg/(self.atk_interval/(self.attack_speed/100)) * min(self.targets,targets)	
		return dps
	
class Skadi(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Skadi",pp,[1,2,3],[2,1],2,1,1)
		if self.module_dmg: 
			if self.module == 1: self.name += " vsBlocked"
			if self.module == 2: self.name += " afterRevive"
		if self.skill == 2: self.skill_duration = self.skill_params[1]	
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] + self.skill_params[0]
		aspd = 0 if self.skill != 1 else self.skill_params[1]
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		if self.module == 2 and self.module_dmg: aspd += 30
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
		dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		return dps

class Skalter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 355  #######including trust
		maxatk = 418
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Skalter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Skalter P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		if self.talent1: self.name += " +Seaborn"
		if self.talent2: self.name += " AllyInRange(add+9%forAH)"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs

		if self.talent2:
			atkbuff += 0.09 if self.pot > 4 else 0.06
			
		####the actual skills
		if self.skill == 3:
			skill_scale = 0.55 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			skilldmg = final_atk * skill_scale * np.fmax(1,-defense) #this defense part has to be included
			if self.talent1: skilldmg *= 2
			dps = skilldmg * self.targets
		return dps

class Specter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Specter",pp,[1,2],[1],2,1,1)		
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module_dmg and self.module == 1 else 1
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		dmgbuff = 1 if self.module_lvl < 2 else 1.03
		if self.module_lvl == 3: dmgbuff = 1.05
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)*(dmgbuff)
		targets = 3 if self.elite == 2 else 2
		dps = hitdmg / self.atk_interval * self.attack_speed/100 * min(self.targets, targets)
		return dps

class SpecterAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SpecterAlter", pp, [1,2,3], [1,2],3,1,1)
		if not self.trait_dmg:
			self.name += "(doll only)"
		if self.skill == 3 and self.trait_dmg:
			if self.skill_dmg: self.name += " vsHigherHP"
			else: self.name += " vsLowerHP"
		if self.targets > 1 and (self.skill == 3 or not self.trait_dmg): self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.trait_dmg else 0
		if not self.trait_dmg and self.module == 1: atkbuff += 0.15
		
		if not self.trait_dmg:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			doll_scale = self.talent1_params[1]
			hitdmg = np.fmax(final_atk * doll_scale * (1-res/100), final_atk * doll_scale * 0.05)
			return hitdmg
			
		if self.skill == 1:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+self.skill_params[1])/100
		if self.skill == 3:
			self.atk_interval = 2.2
			dmgbonus = 1 + self.skill_params[2]
			if not self.skill_dmg: dmgbonus = 1
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  - defense, final_atk * 0.05) * dmgbonus
			dps = dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,2)
		return dps

class Stainless(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 532  #######including trust
		maxatk = 633
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Stainless Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Stainless P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 25
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 3 and not self.skilldmg: self.name += " TurretOnly"
		
		if self.skill != 1 and self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill == 3: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1: aspd += 5
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 1.6 if self.mastery == 3 else 1.4 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:
			atkbuff += 0.4 + 0.05 * self.mastery
			aspd += 40 + 5 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if not self.skilldmg: dps = 0
			turret_scale = 2.6 if self.mastery == 0 else 2.55 + 0.15 * self.mastery
			turret_aoe = 1.2 + 0.1 * self.mastery
			turrethitdmg = np.fmax(final_atk * turret_scale - defense, final_atk * turret_scale * 0.05)
			turretaoedmg = np.fmax(final_atk * turret_aoe - defense, final_atk * turret_aoe * 0.05)
			totalturret = turrethitdmg + turretaoedmg * (self.targets - 1)
			dps += totalturret * self.hits / 5
			
		return dps

class Steward(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Steward",pp,[1],[],1,6,0)

	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.talent1_params[0] + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		hitdmg_skill = np.fmax(final_atk * self.skill_params[0] * (1-res/100), final_atk * self.skill_params[0] * 0.05)
		avghit = (hitdmg * self.skill_cost + hitdmg_skill) / (self.skill_cost + 1)
		dps = avghit / self.atk_interval * self.attack_speed/100
		return dps

class Stormeye(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Stormeye",pp,[1],[],1,1,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		critchance = self.talent1_params[1]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		critdmg = np.fmax(2 * final_atk - defense, 2 * final_atk * 0.05)
		avgdmg = critchance * critdmg + (1-critchance) * hitdmg
		dps = 2 * avgdmg / self.atk_interval * (self.attack_speed) / 100
		return dps * min(2, self.targets)

class Surtr(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Surtr", pp, [1,2,3],[],3,1,0)
		if self.skill == 1:
			if self.skill_dmg: self.name += " KillingHitsOnly"
			else: self.name += " noKills"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		resignore = self.talent1_params[0]
		newres = np.fmax(0, res - resignore)
			
		if self.skill == 1:
			atk_scale = self.skill_params[0]
			hits = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			avghit = (hits * hitdmgarts + skilldmgarts)/(hits + 1)
			if self.skill_dmg:
				avghit = skilldmgarts	
			dps = avghit/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			atk_scale = self.skill_params[3]
			one_target_dmg = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			two_target_dmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			dps = one_target_dmg/(self.atk_interval/(self.attack_speed/100))
			if self.targets > 1:
				dps = 2 * two_target_dmg/(self.atk_interval/(self.attack_speed/100))
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			maxtargets = self.skill_params[6]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(self.attack_speed/100)) * min(self.targets,maxtargets)
		return dps

class Suzuran(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Suzuran", pp, [1,2],[1,2],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0]
		try: atkbuff += self.talent1_params[1]
		except: pass
		aspd = self.skill_params[1] if self.skill == 1 else 0
		fragile = self.talent2_params[0] - 1	
		fragile = max(fragile, self.buff_fragile)
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2 and self.targets > 1: dps *= min(self.targets, self.skill_params[1])
			
		return dps*(1+fragile)/(1+self.buff_fragile)

class SwireAlt(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 727 #######including trust
		maxatk = 865
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"SwireAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"SwireAlt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 25
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 81
				elif self.module_lvl == 2: self.base_atk += 71
				else: self.base_atk += 57
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		  ##### keep the ones that apply
		self.stacks = 9 if self.pot > 4 else 8
		
		if not self.talent1:
			self.name += " noStacks"
			self.stacks = 0
		else: self.name += f" {self.stacks}Stacks"
		
		if self.skilldmg and self.skill == 2: self.name += " 2HitBottles"
		if not self.skilldmg and self.skill == 1: self.name += " heals>attacks"
		if self.module == 2 and self.talent1: self.name += " maxModStacks"
		 ######when op has aoe
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atkbuff += self.stacks * 0.04
			if self.module == 1 and self.module_lvl > 1: atkbuff += self.stacks * 0.01
			if self.module == 2: atkbuff += 0.2
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			atkcycle= (self.atk_interval/(1+aspd/100))
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if not self.skilldmg: dps = dps * (3/atkcycle-1) /(3/atkcycle)
		
		if self.skill == 2:
			skill_scale = 1.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			if self.skilldmg: skilldmg *= 2
			
			atkcycle= (self.atk_interval/(1+aspd/100))
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			dps = dps * (3/atkcycle-1) /(3/atkcycle) + skilldmg / 3
		
		if self.skill == 3:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * 2
		return dps

	def get_name(self):
		if self.skill == 3:

			atk = self.stacks * 0.04
			if self.module == 1 and self.module_lvl > 1: atk += self.stacks * 0.01
			if self.module == 2: atk += 0.2
			
			skill_scale = 1.2 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+self.buffs[0] + atk) + self.buffs[1]
			nukedmg = final_atk * 10 * skill_scale * (1+self.buffs[3])
			self.name += f" 10Coins:{int(nukedmg)}"
		return self.name

class Tachanka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tachanka",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 1 and not self.skill_dmg: " outsideBurnZone"
		if self.skill == 1 and self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		dmg_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill == 1:
			skill_scale = self.skill_params[1]
			newdef = np.fmax(0,defense - self.skill_params[2]) if self.skill_dmg else defense
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_scale 
			dps = 2 * hitdmg / self.atk_interval * self.attack_speed/100 + hitdmgarts * self.targets
		if self.skill == 2:
			atk_interval = self.atk_interval * 0.15
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * self.skill_params[2] - defense, final_atk * self.skill_params[2] * 0.05)
			avghit  = critdmg * self.skill_params[1] + hitdmg * (1 -self.skill_params[1])
			dps = 2 * avghit / atk_interval * self.attack_speed/100 * dmg_scale
		return dps

class TexasAlter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 533  #######including trust
		maxatk = 659
		self.atk_interval = 0.93   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 2: self.base_atk += 22
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Texalt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Texalt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 53
				else: self.base_atk += 40
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent2: self.name += " preKill"
		if self.module == 2 and self.moduledmg: self.name += " alone"
		elif self.module == 2 and not self.moduledmg: self.name += " adjacentAlly"
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 0.2
		if self.module == 2:
			if self.module_lvl == 2: atkbuff += 0.05
			if self.module_lvl == 3: atkbuff += 0.08

		if self.talent2:
			aspd += 8
			if self.pot > 4: aspd += 2
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.55 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)

			artsdmg = 320 + 30 * self.mastery
			if self.mastery == 3: artsdmg -= 10
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + np.fmax(artsdmg *(1-res/100), artsdmg * 0.05)
		
		if self.skill == 2:
			resshred = 0.2
			if self.mastery == 1: resshred = 0.25
			elif self.mastery > 1: resshred = 0.3
			newres = res *(1-resshred)
			atkbuff += 0.4 + 0.05 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			
			dps = 2*hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			skillscale = 1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			maxtargets = 4 if self.mastery == 3 else 3
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * skillscale *(1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			dps += hitdmgarts * min(self.targets, maxtargets)
			
		return dps
	
	def get_name(self):
		atk = 0.2 #talent
		if self.module == 2:
			if self.moduledmg: atk += 0.1
			if self.module_lvl == 2: atk += 0.05
			if self.module_lvl == 3: atk += 0.08
		
		if self.skill == 2:
			atk += 0.4 + 0.05 * self.mastery
			skill_scale = 1.8 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+self.buffs[0] + atk) + self.buffs[1]
			nukedmg = final_atk * skill_scale * (1+self.buffs[3])
			self.name += f" InitialAoe:{int(nukedmg)}"
		if self.skill == 3:
			skill_scale = 1.3 if self.mastery == 0 else 1.2 + 0.15 * self.mastery
			final_atk = self.base_atk * (1+self.buffs[0] + atk) + self.buffs[1]
			nukedmg = final_atk * 2 * skill_scale * (1+self.buffs[3])
			self.name += f" InitialAoe:{int(nukedmg)}"
		return self.name
	
class Tequila(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 306  #######including trust
		maxatk = 352
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Tequila Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Tequila P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.skilldmg = TrTaTaSkMo[3]

		if not self.trait: self.name += " 20Stacks"   ##### keep the ones that apply
		else: self.name += " 40stacks"
		if self.skill == 2 and not self.skilldmg: self.name += " NotCharged"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 2 if self.trait else 1
			
		####the actual skills
		if self.skill == 1:
			atk_scale = 1.7 if self.mastery == 3 else 1.5 + 0.05 * self.mastery
			aspd += 38 + 4 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atk_scale = 2 + 0.1 * self.mastery
			maxtargets = 3 if self.skilldmg else 2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, maxtargets)
		
		return dps

class TerraResearchCommission(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("TerraResearchCommission",pp,[],[],0,6,0) #available skills, available modules, default skill, def pot, def mod
		if not self.talent_dmg: self.name += " after3BigHits"
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		cdmg = self.talent1_params[4] if self.talent_dmg else 1
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		hitdmg2 = np.fmax(0.5 * final_atk - defense, 0.5 * final_atk * 0.05)
		critdmg2 = np.fmax(0.5 * final_atk * cdmg - defense, 0.5 * final_atk * cdmg * 0.05)
		avghit = 0.8 * (hitdmg + hitdmg2) + 0.2 * (critdmg + critdmg2)
		dps = avghit / self.atk_interval * self.attack_speed / 100 * self.targets
		return dps

class Thorns(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__("Thorns",pp,[1,2,3],[1],3,1,1)
		if self.skill == 1 and not self.trait_dmg: self.name += "rangedAtk"   ##### keep the ones that apply
		if self.talent_dmg: self.name += " vsRanged"
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
		if self.skill == 3 and not self.skill_dmg: self.name += " firstActivation"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe	
			
	def skill_dps(self, defense, res):
		bonus = 0.1 if self.module == 1 else 0
		arts_dot = 0 if self.elite < 2 else max(self.talent1_params)
		if not self.talent_dmg: arts_dot *= 0.5
		stacks = self.talent1_params[3] if self.module == 1 and self.module_lvl > 1 else 1
		arts_dot_dps = np.fmax(arts_dot *(1-res/100) , arts_dot * 0.05) * stacks
		
		if self.skill == 1:
			atk_scale = 1 if self.trait_dmg else 0.8
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg)/self.atk_interval * self.attack_speed/100 + arts_dot_dps
		if self.skill == 2 and self.hits > 0:
			atk_scale = 0.8
			cooldown = self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			if(1/self.hits < cooldown):
				dps = (hitdmg/cooldown + arts_dot_dps + bonusdmg/cooldown) * min(self.targets,4)
			else:
				cooldown = 1/self.hits
				dps = (hitdmg/cooldown + arts_dot_dps) * min(self.targets,4)
		elif self.skill == 2:
			return defense*0
		if self.skill == 3:
			bufffactor = 2 if self.skill_dmg else 1
			final_atk = self.atk * (1 + self.buff_atk + bufffactor * self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg)/self.atk_interval * (self.attack_speed + bufffactor * self.skill_params[1])/100 + arts_dot_dps
		return dps

class Toddifons(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 877  #######including trust
		maxatk = 1049
		self.atk_interval = 2.4  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Toddifons Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Toddifons P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " withRacism"
		if self.moduledmg and self.module == 1: self.name += " vsHeavy"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atk_scale = 1.5 if self.pot > 4 else 1.45
			if self.module == 1:
				atk_scale += 0.1 * (self.module_lvl - 1)

		if self.module == 1 and self.moduledmg:
			atk_scale *= 1.1
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.5 + 0.1 * self.mastery
			newdef = defense * 0.75 if self.mastery < 2 else defense * 0.7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			self.atk_interval = 2.7
			skill_scale = 2.1 + 0.1 * self.mastery
			skill_scale2 = 0.8 if self.mastery == 3 else 0.7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmg2 = np.fmax(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05) * self.targets
			
			dps = (hitdmg+hitdmg2)/(self.atk_interval/(1+aspd/100))
		return dps

class Tomimi(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tomimi", pp, [1,2], [2],2,6,2)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
				
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0]
		final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		if self.skill == 1:
			dps = hitdmg/self.atk_interval * (self.attack_speed + self.skill_params[0]) / 100
		if self.skill == 2:
			crate = self.skill_params[2]
			atk_scale = self.skill_params[1]
			critdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			avgnormal = (1-crate) * hitdmg
			avgstun = crate / 3 * hitdmg
			avgcrit = crate / 3 * critdmg
			avgaoe = crate / 3 * hitdmg * self.targets
			dps = (avgnormal + avgstun + avgcrit + avgaoe)/self.atk_interval * self.attack_speed/100
		return dps

class Totter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Totter",pp,[1,2],[1],2,6,1)
		if self.talent_dmg: self.name += " vsInvis"
		if self.module_dmg and self.module == 1: self.name += " vsHeavy"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
				
	def skill_dps(self, defense, res):
		atkbuff = 0
		atk_scale = 1
		#talent/module buffs
		if self.talent_dmg:
			atkbuff += self.talent1_params[0]

		if self.module == 1 and self.module_dmg:
			atk_scale = 1.1
			
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * min(self.targets,2)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			
			dps = avgphys/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			aspd = self.skill_params[0]
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.targets == 1: hitdmg = np.fmax(final_atk * skill_scale *  atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed + aspd)/100)) * min(self.targets, 3)
		return dps

class Typhon(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Typhon",pp,[1,2,3],[1],3,1,1)
		self.try_kwargs(2,["crit","crits","nocrit","nocrits"],**kwargs)
		self.try_kwargs(5,["heavy","vsheavy","vs","light","vslight"],**kwargs)
		self.talent2_dmg = self.talent2_dmg and self.talent_dmg
		if self.elite == 2:
			if not self.talent2_dmg: self.name += " noCrits"
			else:
				if self.skill == 3: self.name += " 1Crit/salvo"
				elif self.skill == 2:
					if self.targets == 1: self.name += " 1/2Crits"
					else: self.name += " allCrits"
				elif self.skill == 1:
					self.name += " allCrits"
		
		if self.module_dmg and self.module == 1: self.name += " vsHeavy"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
				
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		crit_scale = self.talent2_params[0] if self.talent2_dmg and self.elite == 2 else 1
		def_ignore = 0 if self.elite == 0 else 5 * self.talent1_params[1]

		if self.skill == 1:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)		
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense*(1-def_ignore), final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)
			if self.targets == 1: dps = (hitdmg+critdmg)/self.atk_interval * self.attack_speed/100
			else: dps = 2 * critdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			self.atk_interval = 5.5
			hits = self.skill_params[4]
			atk_scale *= self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense*(1-def_ignore), final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)
			totaldmg = hits * hitdmg
			if self.talent2_dmg:
				totaldmg = (hits-1)*hitdmg + critdmg
			dps = totaldmg/self.atk_interval * self.attack_speed/100
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			ammo = self.skill_params[3]
			return(self.skill_dps(defense,res) * ammo * (5.5/(self.attack_speed/100)))
		else:
			return(self.skill_dps(defense,res) * self.skill_duration)

class Ulpianus(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ulpianus",pp,[1,2,3],[1],3,1,1)
		if self.elite == 2 and self.talent2_dmg:
			self.name += f" {int(self.talent2_params[0])}kills"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

		if self.skill == 3:
			bonus_base = self.talent2_params[0] * self.talent2_params[2] if self.talent2_dmg and self.elite == 2 else 0
			atkbuff = self.skill_params[1]
			final_atk = (self.atk + bonus_base) * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			scale = self.skill_params[2]
			nukedmg = final_atk * scale * (1+self.buff_fragile)
			self.name += f" InitialDmg:{int(nukedmg)}"
			
	
	def skill_dps(self, defense, res):
		bonus_base = self.talent2_params[0] * self.talent2_params[2] if self.talent2_dmg and self.elite == 2 else 0
			
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = (self.atk + bonus_base) * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
				
			dps = avghit/self.atk_interval * self.attack_speed/100 * min(2,self.targets)
		if self.skill == 2:
			atkbuff = self.skill_params[1]
			final_atk = (self.atk + bonus_base) * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(3,self.targets)
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			final_atk = (self.atk + bonus_base) * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(2,self.targets)
		return dps

class Utage(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 605  #######including trust
		maxatk = 723
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Utage Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Utage P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " lowHP"
		else: self.name += " fullHP"
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		if self.talent1:
			aspd += 100
			if self.module == 1 and self.module_lvl > 1: atkbuff += 0.02 + 0.01 * self.module_lvl

		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Vanilla(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vanilla",pp,[1],[],1,6,0)
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] + self.skill_params[1]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps
	
class Vermeil(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vermeil",pp,[1,2,],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.module == 1 and self.module_dmg: self.name += " vsAerial"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2 and self.targets > 1: dps *= 2
		return dps

class Vigil(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 458  #######including trust
		maxatk = 542
		lvl1wolf = 304
		maxwolf = 371
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.wolf_atk = lvl1wolf + (maxwolf-lvl1wolf) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Vigil Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Vigil P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0] and TrTaTaSkMo[2]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 25
				else: self.base_atk += 20
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1:
			if self.trait: self.name += " vsBlocked"
			if not self.skilldmg: self.name += " 1wolf"
		else:
			self.name += " noWolves"
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		defignore = 0
		wolves = 0
		if self.talent1:
			wolves = 3 if self.skilldmg  else 1
			if self.trait:
				atk_scale = 1.5
				defignore = 200 if self.pot > 4 else 175
		newdef = np.fmax(0, defense - defignore)
		wolfdef = np.fmax(0, defense - 200) if self.pot > 4 else np.fmax(0, defense - 175)
		####the actual skills
		if self.skill == 2:
			skill_scale = 1.7 + 0.1 * self.mastery
			sp_cost = 5 if self.mastery == 3 else 6
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_wolf  = self.wolf_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = np.fmax(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgwolfskill = np.fmax(final_wolf * skill_scale - wolfdef, final_wolf * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = 1.25/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = hitdmgwolfskill
			if atks_per_skillactivation > 1:
				avghit = (hitdmgwolfskill + (atks_per_skillactivation - 1) * hitdmgwolf) / atks_per_skillactivation						
			
			if self.talent1: dps = avghit/(self.atk_interval/(1+aspd/100)) * wolves
			dps += hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 3:
			skill_scale = 0.5 if self.mastery == 3 else 0.3 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_wolf  = self.wolf_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = np.fmax(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * 0.05)
			hitdps = 3 * hitdmg/(self.atk_interval/(1+aspd/100))
			artdps = 0
			if self.talent1:
				hitdps += wolves * hitdmgwolf/(1.25/(1+aspd/100))
				artdps = wolves * hitdmgarts/(1.25/(1+aspd/100))
				if self.trait:
					artdps += 3 * hitdmgarts/(self.atk_interval/(1+aspd/100))
			dps = hitdps + artdps
			
		return dps

class Vigna(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vigna",pp,[1,2],[2],2,6,2)
		if self.module_dmg and self.module == 2: self.name += " vsLowHp"
			
	def skill_dps(self, defense, res):
		crate = 0 if self.elite == 0 else self.talent1_params[2]
		cdmg = self.talent1_params[0]
		atkbuff = self.skill_params[0]
		if self.skill == 2: self.atk_interval = 1.5
		atk_scale = 1.1 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		final_atk_crit = self.atk * (1 + atkbuff + self.buff_atk + cdmg) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		critdmg = np.fmax(final_atk_crit * atk_scale - defense, final_atk_crit * atk_scale * 0.05)
		avgdmg = crate * critdmg + (1-crate) * hitdmg
		dps = avgdmg / self.atk_interval * self.attack_speed/100
		return dps

class Vina(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("VinaVictoria", pp, [1,2,3],[],3,1,0)
		if self.talent_dmg:
			self.count = 8 if self.skill == 3 else 3
		else:
			self.count = 4 if self.skill == 3 else 0
		if self.elite > 0: self.name += f" {self.count}Allies"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] * self.count		
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			hits = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * skill_scale *(1-res/100), final_atk * skill_scale * 1)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts
			if atks_per_skillactivation > 1:
				avghit = (skilldmgarts + int(atks_per_skillactivation) * hitdmgarts) / (int(atks_per_skillactivation)+1)
			dps = avghit/(self.atk_interval/(self.attack_speed/100))

		if self.skill == 2:
			atkbuff += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * min(self.targets,2)
		if self.skill == 3:
			atk_interval = self.atk_interval + self.skill_params[0]
			atkbuff += self.skill_params[1]
			maxtargets = self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 1)
			hitdmg_lion = np.fmax(self.drone_atk *(1-res/100), self.drone_atk * 1)
			dps = hitdmgarts/(atk_interval/(self.attack_speed/100)) * min(self.targets,maxtargets) + hitdmg_lion/self.drone_atk_interval * min(self.targets, self.count)
		return dps

class Virtuosa(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 447  #######including trust
		maxatk = 525
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Virtuosa Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Virtuosa P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0] #vs elite non elite
		self.talent1 = TrTaTaSkMo[1] 
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3] # skill 1: save up charges for faster reapplication
										#skill 3: self atk+
		if not self.skill == 1:
			if self.trait: self.name += " vsNonBoss"
			else: self.name += " vsBoss"
		else: self.name += " ArtsDpsOnly.Add 400-700elementalDps."
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		eleThreshold = 1000 if self.trait else 2000
		eleDamage = 12000
		eleDuration = 15
		eleBonus = 0.2 if self.pot < 5 else 0.22
			
		####the actual skills
		if self.skill == 1: #todo, which will probably be a pain
			skill_scale = 2.4 + 0.2 * self.mastery
			sp_cost = 6
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)

			skilldmg =np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			aspd += 45 + 5 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			extraEle = final_atk * 0.25 if self.mastery == 3 else final_atk * 0.2
			eleThreshold = eleThreshold / (1 + eleBonus)
			eleApplicationTarget = final_atk * 0.1 + extraEle / (self.atk_interval/(1+aspd/100))
			eleApplicationBase = final_atk * 0.1
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			artsdps = hitdmgarts/(self.atk_interval/(1+aspd/100))
			targetEledps = eleDamage / (eleDuration + eleThreshold/eleApplicationTarget)
			ambientEledps = eleDamage / (eleDuration + eleThreshold/eleApplicationBase)
			
			dps = np.fmin(self.targets, 2) * (artsdps + targetEledps)
			if self.targets > 2:
				dps += ambientEledps * (self.targets -2)			
			
		if self.skill == 3:
			eleBonus *= 2.2 + 0.1 * self.mastery
			atkbuff += 1.4 + 0.15 * self.mastery
			if self.mastery > 1: atkbuff -= 0.05
			eleThreshold = eleThreshold / (1 + eleBonus)
			final_atk = np.fmax(1,-defense) * self.base_atk * (1+atkbuff) + self.buffs[1] #this is so stupid lol, but defense or res HAS to be included
			eleApplication = final_atk * 0.1
			applicationDuration = eleThreshold / eleApplication
			dps = self.targets * eleDamage / (eleDuration + applicationDuration)			

		return dps
	
class Viviana(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 623  #######including trust
		maxatk = 746
		self.atk_interval = 1.25   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Viviana Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Viviana P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]

		
		if self.talent1: self.name += " vsElite"
		
		if self.skilldmg and self.skill == 2: self.name += " afterSteal"
		if self.skilldmg and self.skill == 3: self.name += " 2ndActivation"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		dmg_scale = 1.08 if self.pot < 5 else 1.09
		if self.talent1:
			dmg_scale = dmg_scale + dmg_scale -1

		####the actual skills
		if self.skill == 2:
			atkbuff += 0.4 if self.mastery == 3 else 0.3 + 0.03 * self.mastery
			if self.skilldmg:
				aspd += 40 if self.mastery == 3 else 30 + 3 * self.mastery
			crate = 0.2
			cdmg = 1.5 if self.mastery == 3 else 1.4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			skilldmg = 2 * np.fmax(final_atk * cdmg * (1-res/100), final_atk * cdmg * 0.05) * dmg_scale
			avgdmg = crate * skilldmg + (1-crate) * hitdmgarts
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:
			self.atk_interval = 1.75
			atkbuff += 1.1 if self.mastery == 3 else 0.75 + 0.1 * self.mastery
			hits = 3 if self.skilldmg else 2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			dps = hits * hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		return dps

class Vulcan(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vulcan",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		targets = 2 if self.skill == 2 else 1
		if self.skill == 2: self.atk_interval = 2
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,targets)
		return dps

class W(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 811  #######including trust
		maxatk = 1012
		self.atk_interval = 2.8   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"W Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"W P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 78
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 54
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 45
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent2 and self.module == 2 and self.module_lvl > 1: self.name += " noDmgTaken"
		if self.moduledmg and self.module == 1: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs	
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1
		
		newdef = defense if self.module != 2 else np.fmax(0, defense - 100)
		if self.module == 2 and self.talent2: atkbuff += 0.1 * (self.module_lvl - 1)
		
		stundmg = 0.21 if self.pot > 4 else 0.18
		if self.module == 1: stundmg += 0.03 * (self.module_lvl - 1)
			
		####the actual skills
		
		if self.skill == 1:
			skill_scale = 3.5 if self.mastery == 3 else 3.1 + 0.1 * self.mastery
			sp_cost = 19 - self.mastery + 1.2 #sp lockout
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			dps = (hitdmg/(self.atk_interval/(1+aspd/100)) + skilldmg / sp_cost) * self.targets
			
		if self.skill == 2:
			skill_scale = 2.5 + 0.1 * self.mastery
			sp_cost = 10 - self.mastery
			if self.mastery > 1: sp_cost += 1
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk* atk_scale * skill_scale * 0.05) * (1+stundmg)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
				
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 3:
			skill_scale = 2.8 if self.mastery == 3 else 3.1 + 0.1 * self.mastery
			targets = 3 if self.mastery == 0 else 4
			sp_cost = 39 - 2 * self.mastery + 1.2 #sp lockout
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			dps = (hitdmg/(self.atk_interval/(1+aspd/100)) + skilldmg * min(targets, self.targets) / sp_cost) * self.targets
		
		return dps

class Walter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Wisadel",pp,[1,2,3],[1],3,1,1)
		self.shadows = 0
		if self.elite == 2:
			if self.skill == 3:
				if self.talent2_dmg:
					self.shadows = 3
				else:
					self.shadows = 2
				if self.skill_params[1] == 1:
					self.shadows -= 1
			else:
				self.shadows = 1 if self.talent2_dmg else 0
		if self.elite == 2: self.name += f" shadows:{self.shadows}"
		if self.skill == 2 and self.skill_dmg: self.name += " overdrive"
		if self.targets > 1:
			self.name += f" {self.targets}targets"
			if self.skill == 2: self.name += "(NonOverlapping)"
			
	def skill_dps(self, defense, res):
		bonushits = 2 if self.module == 1 else 1
		maintargetscale = 1 if self.elite == 0 else self.talent1_params[0]
		explosionscale = 0 if self.elite == 0 else self.talent1_params[2]
		prob = 1 - 0.85 ** bonushits
	
		####the actual skills
		if self.skill == 1:
			prob2 = 1 - 0.85 ** (bonushits+2)
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			
			hitdmg_main = np.fmax(final_atk * maintargetscale - defense, final_atk * maintargetscale * 0.05)
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			bonushitdmg_main = np.fmax(final_atk * maintargetscale * 0.5 - defense, final_atk * maintargetscale * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - defense, final_atk  * 0.05)
			skillhitdmg_main = np.fmax(final_atk * maintargetscale * skill_scale - defense, final_atk * maintargetscale * skill_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			explosiondmg = np.fmax(final_atk * explosionscale - defense, final_atk * explosionscale * 0.05)
			sp_cost = self.skill_cost
			avghit_main = (sp_cost * (hitdmg_main + bonushitdmg_main * bonushits) + hitdmg_main + (bonushits+2)*skillhitdmg_main) / (sp_cost + 1)
			avghit = (sp_cost * (hitdmg + bonushitdmg * bonushits) + hitdmg + (bonushits+2)*skillhitdmg) / (sp_cost + 1)
			avg_explosion = (sp_cost * explosiondmg * prob + explosiondmg * prob2) / (sp_cost + 1)
			dps = (avghit_main+avg_explosion)/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += (avghit+avg_explosion)/self.atk_interval * self.attack_speed/100 * (self.targets - 1)
			
		if self.skill == 2:
			atk_interval = self.atk_interval + self.skill_params[0]
			atkbuff = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			atk_scale = self.skill_params[2] if self.skill_dmg else 1
			hitdmg_main = np.fmax(final_atk * maintargetscale * atk_scale - defense, final_atk * maintargetscale * atk_scale * 0.05)
			#hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonushitdmg_main = np.fmax(final_atk * maintargetscale * atk_scale * 0.5 - defense, final_atk * maintargetscale * atk_scale * 0.05)
			#bonushitdmg = np.fmax(final_atk * atk_scale * 0.5 - defense, final_atk * atk_scale * 0.05)
			explosiondmg = np.fmax(final_atk * explosionscale - defense, final_atk * explosionscale * 0.05)
			dps = (hitdmg_main + bonushitdmg_main * bonushits + prob * explosiondmg)/atk_interval * self.attack_speed/100
			if self.skill_dmg: dps *= 4
			elif self.targets > 1: dps *= min(3, self.targets)
		
		if self.skill == 3:
			self.atk_interval = 5
			atkbuff = self.skill_params[0]
			skill_scale = self.skill_params[3]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg_main = np.fmax(final_atk * maintargetscale * skill_scale - defense, final_atk * maintargetscale * skill_scale * 0.05)
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			bonushitdmg_main = np.fmax(final_atk * maintargetscale * skill_scale * 0.5 - defense, final_atk * skill_scale * maintargetscale * 0.5 * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - defense, final_atk * 0.5 * 0.05)
			explosiondmg = np.fmax(final_atk * explosionscale - defense, final_atk * explosionscale * 0.05)
			dps = (hitdmg_main + bonushitdmg_main * bonushits + explosiondmg)/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += (hitdmg + bonushitdmg * bonushits + explosiondmg)/self.atk_interval * self.attack_speed/100 * (self.targets-1)
		
		shadowhit = np.fmax(self.drone_atk * (1-res/100), self.drone_atk * 0.05) * self.shadows
		dps += shadowhit/4
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			self.atk_interval = 5
			return(self.skill_dps(defense,res) * 6 * (self.atk_interval/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Warmy(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 553  #######including trust
		maxatk = 646
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Warmy Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Warmy P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.skilldmg = TrTaTaSkMo[3]

		if self.skill == 1:
			if not self.trait: self.name += " no Burn"
			else:
				if self.skilldmg: self.name += " avgBurn vsNonboss"
				else: self.name += " avgBurn vsBoss"
		if self.skill == 2 and self.skilldmg: self.name += " vsBurn (in your dreams)"

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		falloutdmg = 7000

		####the actual skills
		if self.skill == 1:
			aspd += 70 + 10 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			falloutdmg += 3.2 * final_atk if self.pot > 4 else 3 * final_atk
			newres = np.fmax(0,res-20)
			elegauge = 1000 if self.skilldmg else 2000
			
			hitdmg1 = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			dpsNorm = hitdmg1/(self.atk_interval/(1+aspd/100))
			dpsFallout = hitdmg2/(self.atk_interval/(1+aspd/100))
			timeToFallout = elegauge/(dpsNorm * 0.15)
			dps = (dpsNorm * timeToFallout + dpsFallout * 10 + falloutdmg)/(timeToFallout + 10)
			if not self.trait: dps = dpsNorm
			
		if self.skill == 2:
			self.atk_interval = 2.5
			atkbuff += 1.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgele = final_atk * 0.5
			hitdmg = hitdmgarts + hitdmgele if self.skilldmg else hitdmgarts
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		return dps

class Weedy(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 593  #######including trust
		maxatk = 722
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Weedy Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Weedy P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 72
				elif self.module_lvl == 2: self.base_atk += 64
				else: self.base_atk += 50
				self.name += f" ModX{self.module_lvl}"
			elif self.module == 2:
				if self.module_lvl == 3: self.base_atk += 68
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 46
				self.name += f" ModY{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.moduledmg and self.module_lvl > 1: self.name += " nextToCannon"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.pot > 3: aspd += 8
		if self.module == 1 and self.moduledmg:
			if self.module_lvl == 2: atkbuff += 0.15
			if self.module_lvl == 3: atkbuff += 0.2
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.35 + 0.05 * self.mastery
			sp_cost = 6 if self.mastery == 0 else 5
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
				
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			atkbuff += 1.7 + 0.1 * self.mastery
			self.atk_interval = 1.2 * 3.2

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 2)
		return dps

class Whislash(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Whislash",pp,[1,2],[1],2,6,1)
		if self.module == 1: self.trait_dmg = self.trait_dmg and self.module_dmg
		if not self.trait_dmg: self.name += " blocking"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" 

	def skill_dps(self, defense, res):
		atk_scale = 1	
		if self.trait_dmg:
			atk_scale = 1.3 if self.module == 1 else 1.2
		talent_buff = self.talent1_params[0]
		atkbuff = self.skill_params[1] if self.skill == 2 else 0
		aspd = talent_buff * self.skill_params[0] if self.skill == 2 else 0.5 * talent_buff * self.skill_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		targets = 3 if self.skill == 2 else 1
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100 * min(targets, self.targets)
		return dps

class Wildmane(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("WildMane",pp,[1,2],[1],1,6,1)
	
	def skill_dps(self, defense, res):
		aspd = self.skill_params[0] if self.skill == 1 else 0
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class YatoAlter(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 530  #######including trust
		maxatk = 655
		self.atk_interval = 0.93   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 2: self.base_atk += 22
		
		self.skill = skill if skill in [1,2,3] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Kirito Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Kirito P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		#self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 48
				elif self.module_lvl == 2: self.base_atk += 43
				else: self.base_atk += 36
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 2: self.name += " totalDMG"
		if self.skill == 3: self.name += " dmgPerHit"
		
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		extra_arts = 0.2
		atkbuff += 0.16 if self.pot > 4 else 0.13
		if self.module == 1:
			if self.module_lvl == 2: atkbuff += 0.04
			if self.module_lvl == 3: atkbuff += 0.07
			
		####the actual skills
		if self.skill == 1:
			aspd += 70 + 10 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * extra_arts * (1-res/100), final_atk * extra_arts * 0.05)
			dps = (hitdmg+hitdmgarts)/(self.atk_interval/(1+aspd/100)) * 10 / 3
		if self.skill == 2:
			extra_arts *= 2.1 if self.mastery == 0 else 2.05 + 0.15 * self.mastery
			atk_scale *= 1.5 if self.mastery == 3 else 1.3 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * extra_arts * (1-res/100), final_atk * atk_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts) * self.targets * 16
		if self.skill == 3:
			skill_scale = 3 if self.mastery == 3 else 2.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * extra_arts * (1-res/100), final_atk * skill_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts)*self.targets
		return dps

class ZuoLe(Operator):
	def __init__(self, pp, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 687  #######including trust
		maxatk = 820
		self.atk_interval = 1.2  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"ZouLe Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"ZuoLe P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.highdmg = True
		if self.talent1 and self.talent2: self.name += " lowHp"
		else: 
			self.name += " fullHp"
			self.highdmg = False
		
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		sp_recovery = 1
		if self.highdmg:
			aspd += 50
			sp_recovery += 2
			if self.module == 1:
				aspd += 10 * (self.module_lvl - 1)
				if self.module_lvl > 1: sp_recovery += self.module * 0.1
			sp_recovery += 0.7 / self.atk_interval *(1+aspd/100) if self.pot < 5 else 0.75 / self.atk_interval *(1+aspd/100)
		else:
			sp_recovery += 0.2 / self.atk_interval *(1+aspd/100) if self.pot < 5 else 0.23 / self.atk_interval *(1+aspd/100)
		####the actual skills
		
		if self.skill == 1:
			atk_scale = 2 if self.mastery == 3 else 1.6 + 0.1*self.mastery
			hits = 3 if self.highdmg else 1
			sp_cost = 4 if self.mastery == 3 else 5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			
			sp_cost = sp_cost / sp_recovery + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg * hits
			if atks_per_skillactivation > 1:
				avghit = (skilldmg *hits  + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 1.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 2)
		
		if self.skill == 3:
			atk_scale = 2.2 if self.mastery == 0  else 2.15 + 0.1 * self.mastery
			hits = 6
			sp_cost = 28 - self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			skilldmg2= np.fmax(2*final_atk * atk_scale - defense, 2*final_atk* atk_scale * 0.05)
			sp_cost = sp_cost / sp_recovery + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = (skilldmg * hits + skilldmg2) * min(3,self.targets)
			if atks_per_skillactivation > 1:
				avghit = ((skilldmg * hits + skilldmg2) * min(3,self.targets)  + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		return dps

################################################################################################################################################################################
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
	
################################################################################################################################################################################

#Add the operator with their names and nicknames here
op_dict = {"12f": twelveF, "aak": Aak, "absinthe": Absinthe, "aciddrop": Aciddrop, "adnachiel": Adnachiel, "<:amimiya:1229075612896071752>": Amiya, "amiya": Amiya, "amiya2": AmiyaGuard, "guardmiya": AmiyaGuard, "amiyaguard": AmiyaGuard, "amiyaalter": AmiyaGuard, "amiya2": AmiyaGuard, "amiyamedic": AmiyaMedic, "amiya3": AmiyaMedic, "medicamiya": AmiyaMedic, "andreana": Andreana, "angelina": Angelina, "aosta": Aosta, "april": April, "archetto": Archetto, "arene": Arene, "asbestos":Asbestos, "ascalon": Ascalon, "ash": Ash, "ashlock": Ashlock, "astesia": Astesia, "astgenne": Astgenne, "aurora": Aurora, "<:aurora:1077269751925051423>": Aurora, 
		"bagpipe": Bagpipe, "beehunter": Beehunter, "bibeak": Bibeak, "blaze": Blaze, "<:blaze_smug:1185829169863589898>": Blaze, "<:blemi:1077269748972273764>":Blemishine, "blemi": Blemishine, "blemishine": Blemishine,"blitz": Blitz, "bp": BluePoison, "poison": BluePoison, "bluepoison": BluePoison, "<:bpblushed:1078503457952104578>": BluePoison, "broca": Broca, "bryophyta" : Bryophyta,
		"cantabile": Cantabile, "canta": Cantabile, "caper": Caper, "carnelian": Carnelian, "castle3": Castle3, "catapult": Catapult, "ceobe": Ceobe, "chen": Chen, "chalter": ChenAlter, "chenalter": ChenAlter, "chenalt": ChenAlter, "chongyue": Chongyue, "ce": CivilightEterna, "civilighteterna": CivilightEterna, "eterna": CivilightEterna, "civilight": CivilightEterna, "theresia": CivilightEterna, "click": Click, "coldshot": Coldshot, "conviction": Conviction, "dagda": Dagda, "degenbrecher": Degenbrecher, "degen": Degenbrecher, "diamante": Diamante, "dobermann": Dobermann, "doc": Doc, "dokutah": Doc, "dorothy" : Dorothy, "durin": Durin, "god": Durin, "durnar": Durnar, "dusk": Dusk, 
		"ebenholz": Ebenholz, "ela": Ela, "estelle": Estelle, "ethan": Ethan, "eunectes": Eunectes, "fedex": ExecutorAlter, "executor": ExecutorAlter, "executoralt": ExecutorAlter, "executoralter": ExecutorAlter, "exe": ExecutorAlter, "foedere": ExecutorAlter, "exu": Exusiai, "exusiai": Exusiai, "<:exucurse:1078503466353303633>": Exusiai, "<:exusad:1078503470610522264>": Exusiai, "eyja": Eyjafjalla, "eyjafjalla": Eyjafjalla, 
		"fang": FangAlter, "fangalter": FangAlter, "fartooth": Fartooth, "fia": Fiammetta, "fiammetta": Fiammetta, "<:fia_ded:1185829173558771742>": Fiammetta, "firewhistle": Firewhistle, "flamebringer": Flamebringer, "flametail": Flametail, "flint": Flint, "folinic" : Folinic,
		"franka": Franka, "frost": Frost, "fuze": Fuze, "gavial": GavialAlter, "gavialter": GavialAlter, "GavialAlter": GavialAlter, "gladiia": Gladiia, "gnosis": Gnosis, "gg": Goldenglow, "goldenglow": Goldenglow, "grani": Grani, "greythroat": GreyThroat, "haze": Haze, "hellagur": Hellagur, "hibiscus": Hibiscus, "hibiscusalt": Hibiscus, "highmore": Highmore, "hoe": Hoederer, "hoederer": Hoederer, "<:dat_hoederer:1219840285412950096>": Hoederer, "hool": Hoolheyak, "hoolheyak": Hoolheyak, "horn": Horn, "hoshiguma": Hoshiguma, "hoshi": Hoshiguma, "humus": Humus, "iana": Iana, "ifrit": Ifrit, "indra": Indra, "ines": Ines, "insider": Insider, "irene": Irene, 
		"jackie": Jackie, "jaye": Jaye, "jessica": Jessica, "jessica2": JessicaAlter, "jessicaalt": JessicaAlter, "<:jessicry:1214441767005589544>": JessicaAlter, "jester":JessicaAlter, "jessicaalter": JessicaAlter, "justiceknight": JusticeKnight,
		"kafka": Kafka, "kazemaru": Kazemaru, "kirara": Kirara, "kjera": Kjera, "kroos": KroosAlter, "kroosalt": KroosAlter, "kroosalter": KroosAlter, "3starkroos": Kroos, "kroos3star": Kroos, "laios": Laios, "lapluma": LaPluma, "pluma": LaPluma,
		"lappland": Lappland, "lappy": Lappland, "<:lappdumb:1078503487484207104>": Lappland, "lava3star": Lava3star, "lava": Lavaalt, "lavaalt": Lavaalt,"lavaalter": Lavaalt, "lee": Lee, "lessing": Lessing, "leto": Leto, "logos": Logos, "lin": Lin, "ling": Ling, "lunacub": Lunacub, "luoxiaohei": LuoXiaohei, "luo": LuoXiaohei, "lutonada": Lutonada, 
		"magallan": Magallan, "maggie": Magallan, "manticore": Manticore, "marcille": Marcille, "matoimaru": Matoimaru, "may": May, "melantha": Melantha, "meteor":Meteor, "meteorite": Meteorite, "midnight": Midnight, "mizuki": Mizuki, "mlynar": Mlynar, "uncle": Mlynar, "monster": Mon3tr, "mon3ter": Mon3tr, "mon3tr": Mon3tr, "kaltsit": Mon3tr, "mostima": Mostima, "morgan": Morgan, "mountain": Mountain, "mousse": Mousse, "mrnothing": MrNothing, "mudmud": Mudrock, "mudrock": Mudrock,
		#"mumu": MumuDorothy, "muelsyse": MumuDorothy, "mumudorothy": MumuDorothy,  "mumu1": MumuDorothy, "mumu2": MumuEbenholz,"mumuebenholz": MumuEbenholz, "mumu3": MumuCeobe,"mumuceobe": MumuCeobe, "mumu4": MumuMudrock,"mumumudrock": MumuMudrock, "mumu5": MumuRosa,"mumurosa": MumuRosa, "mumu6": MumuSkadi,"mumuskadi": MumuSkadi, "mumu7": MumuSchwarz,"mumuschwarz": MumuSchwarz, 
		"narantuya": Narantuya, "ntr": NearlAlter, "ntrknight": NearlAlter, "nearlalter": NearlAlter, "nearl": NearlAlter, "nian": Nian, "nymph": Nymph, "odda": Odda, "pallas": Pallas, "passenger": Passenger, "penance": Penance, "pepe": Pepe, "phantom": Phantom, "pinecone": Pinecone,"pith": Pith,  "platinum": Platinum, "plume": Plume, "popukar": Popukar, "pozy": Pozemka, "pozemka": Pozemka, "projekt": ProjektRed, "red": ProjektRed, "projektred": ProjektRed, "provence": Provence, "pudding": Pudding, "qiubai": Qiubai,"quartz": Quartz, 
		"rangers": Rangers, "ray": Ray, "reed": ReedAlter, "reedalt": ReedAlter, "reedalter": ReedAlter,"reed2": ReedAlter, "rockrock": Rockrock, "rosa": Rosa, "rosmontis": Rosmontis, "saga": Saga, "bettersiege": Saga, "scavenger": Scavenger, "scene": Scene, "schwarz": Schwarz, "shalem": Shalem, "sharp": Sharp,
		"siege": Siege, "silverash": SilverAsh, "sa": SilverAsh, "skadi": Skadi, "<:skadidaijoubu:1078503492408311868>": Skadi, "<:skadi_hi:1211006105984041031>": Skadi, "<:skadi_hug:1185829179325939712>": Skadi, "kya": Skadi, "kyaa": Skadi, "skalter": Skalter, "skadialter": Skalter, "specter": Specter, "shark": SpecterAlter, "specter2": SpecterAlter, "spectral": SpecterAlter, "spalter": SpecterAlter, "specteralter": SpecterAlter, "laurentina": SpecterAlter, "stainless": Stainless, "steward": Steward, "stormeye": Stormeye, "surtr": Surtr, "jus": Surtr, "suzuran": Suzuran, "swire": SwireAlt, "swire2": SwireAlt,"swirealt": SwireAlt,"swirealter": SwireAlt, 
		"tachanka": Tachanka, "texas": TexasAlter, "texasalt": TexasAlter, "texasalter": TexasAlter, "texalt": TexasAlter, "tequila": Tequila, "terraresearchcommission": TerraResearchCommission, "trc": TerraResearchCommission, "thorns": Thorns, "thorn": Thorns,"toddifons":Toddifons, "tomimi": Tomimi, "totter": Totter, "typhon": Typhon, "<:typhon_Sip:1214076284343291904>": Typhon, 
		"ulpian": Ulpianus, "ulpianus": Ulpianus, "utage": Utage, "vanilla": Vanilla, "vermeil": Vermeil, "vigil": Vigil, "trash": Vigil, "garbage": Vigil, "vigna": Vigna, "vina": Vina, "victoria": Vina, "siegealter": Vina, "vinavictoria": Vina, "virtuosa": Virtuosa, "<:arturia_heh:1215863460810981396>": Virtuosa, "arturia": Virtuosa, "viviana": Viviana, "vivi": Viviana, "vulcan": Vulcan, "w": W, "walter": Walter, "wisadel": Walter, "warmy": Warmy, "weedy": Weedy, "whislash": Whislash, "aunty": Whislash, "wildmane": Wildmane, "yato": YatoAlter, "yatoalter": YatoAlter, "kirinyato": YatoAlter, "kirito": YatoAlter, "zuo": ZuoLe, "zuole": ZuoLe}

#The implemented operators
operators = ["12F","Aak","Absinthe","Aciddrop","Adnachiel","Amiya","AmiyaGuard","AmiyaMedic","Andreana","Angelina","Aosta","April","Archetto","Arene","Asbestos","Ascalon","Ash","Ashlock","Astesia","Astgenne","Aurora","Bagpipe","Beehunter","Bibeak","Blaze","Blemishine","Blitz","BluePoison","Broca","Bryophyta","Cantabile","Caper","Carnelian","Castle3","Catapult","Ceobe","Chen","Chalter","Chongyue","CivilightEterna","Click","Coldshot","Conviction","Dagda","Degenbrecher","Diamante","Dobermann","Doc","Dorothy","Durin","Durnar","Dusk","Ebenholz","Ela","Estelle","Ethan","Eunectes","ExecutorAlt","Exusiai","Eyjafjalla","FangAlter","Fartooth","Fiammetta","Firewhistle","Flamebringer","Flametail","Flint","Folinic","Franka","Frost","Fuze","Gavialter","Gladiia","Gnosis","Goldenglow","Grani","Greythroat",
		"Haze","Hellagur","Hibiscus","Highmore","Hoederer","Hoolheyak","Horn","Hoshiguma","Humus","Iana","Ifrit","Indra","Ines","Insider","Irene","Jackie","Jaye","Jessica","JessicaAlt","JusticeKnight","Kazemaru","Kirara","Kjera","Kroos","Kroos3star","Laios","Lapluma","Lappland","Lava3star","LavaAlt","Lee","Lessing","Logos","Leto","Lin","Ling","Lunacub","LuoXiaohei","Lutonada","Magallan","Manticore","Marcille","Matoimaru","May","Melantha","Meteor","Meteorite","Midnight","Mizuki","Mlynar","Mon3tr","Mostima","Morgan","Mountain","Mousse","MrNothing","Mudrock","Narantuya","NearlAlter","Nian","Nymph","Odda","Pallas","Passenger","Penance","Pepe","Phantom","Pinecone","Pith","Platinum","Plume","Popukar","Pozemka","ProjektRed","Provence","Pudding","Qiubai","Quartz","Rangers","Ray","ReedAlt","Rockrock",
		"Rosa","Rosmontis","Saga","Scavenger","Scene","Schwarz","Shalem","Sharp","Siege","SilverAsh","Skadi","Skalter","Specter","SpecterAlter","Stainless","Steward","Stormeye","Surtr","Suzuran","SwireAlt","Tachanka","TexasAlter","Tequila","TerraResearchCommission","Thorns","Toddifons","Tomimi","Totter","Typhon","Ulpianus","Utage","Vanilla","Vermeil","Vigil","Vigna","VinaVictoria","Virtuosa","Viviana","Vulcan","W","Warmy","Weedy","Whislash","Wildmane","Wis'adel","YatoAlter","ZuoLe"]
