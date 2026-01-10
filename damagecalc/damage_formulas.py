import math  # fuck you, Kjera
import numpy as np

import dill

from Database.JsonReader import OperatorData
from damagecalc.utils import PlotParameters

with open('Database/json_data.pkl', 'rb') as f:
	op_data_dict= dill.load(f)

class AttackSpeed:
	def __init__(self, value=100):
		self._value = self._clamp(value)
	def _clamp(self, x):
		return max(20, min(600, x))
	@property
	def value(self):
		return self._value
	@value.setter
	def value(self, new_value):
		self._value = self._clamp(new_value)
	def __int__(self):
		return self._value
	def __float__(self):
		return float(self._value)
	def __repr__(self):
		return f"AttackSpeed({self._value})"
	def __str__(self):
		return str(self._value)
	#Addition stays AttackSpeed, multiplication turns it into float
	def __add__(self, other):
		return AttackSpeed(self._clamp(self._value + other))
	def __radd__(self, other):
		return self.__add__(other)
	def __sub__(self, other):
		return AttackSpeed(self._clamp(self._value - other))
	def __rsub__(self, other):
		return AttackSpeed(self._clamp(other - self._value))
	def __mul__(self, other):
			return float(float(self._value) * other)
	def __rmul__(self, other):
			return self.__mul__(other)
	def __truediv__(self, other):
		return float(self._value / float(other))
	def __rtruediv__(self, other):
		return float(other) / float(self._value)
	def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
		raw_inputs = [float(i) if isinstance(i, AttackSpeed) else i for i in inputs]
		result = getattr(ufunc, method)(*raw_inputs, **kwargs)
		return result

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
		self.targets = min(max(1,params.targets),128)
		self.sp_boost = params.sp_boost
		self.physical = op_data.physical
		self.ranged = op_data.ranged
		
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
			if not (skill in available_skills or skill == 0):
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
				self.name += " S0"
			self.skill = skill

		skill_lvl = params.mastery if params.mastery > 0 and params.mastery < max_skill_lvls[elite] else max_skill_lvls[elite]
		if skill_lvl < max_skill_lvls[elite] and self.skill != 0:
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
					if name in ["Kaltsit","Phantom","Mizuki","Rosmontis","Dusk","Eunectes","Raidian","Pepe","SwireAlter","Gnosis","Hoolheyak"]:
						mod_name = ["X","Y","$\\alpha$"]
					self.name += " Mod" + mod_name[module-1] + f"{module_lvl}"
		
		
		if trust != 100:
			self.name += f" {trust}Trust"
		self.base_name = self.name

		########### Read all the parameters from the json
		self.attack_speed = AttackSpeed()
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
				elif module == available_modules[1]:
					self.atk += op_data.atk_module[1][module_lvl-1]
					self.attack_speed += op_data.aspd_module[1][module_lvl-1]
				else:
					self.atk += op_data.atk_module[2][module_lvl-1]
					self.attack_speed += op_data.aspd_module[2][module_lvl-1]
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
								if pot > talent_data[4] and pot > current_req_pot:
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
									if pot > talent_data[4] and pot > current_req_pot:
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
								if pot > talent_data[4] and pot > current_req_pot:
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
									if pot > talent_data[4] and pot > current_req_pot:
										self.talent2_params = talent_data[5]
										current_promo = talent_data[0]
										current_req_lvl = talent_data[1]
										current_req_pot = talent_data[4]
										current_req_module_lvl = talent_data[3]
		self.drone_atk = 0
		self.drone_atk_interval = 1
		if op_data.drone_atk_e0 != []:
			try:
				slot = skill - 1
				if len(op_data.drone_atk_e0) < 2: slot = 0
				self.drone_atk_interval = op_data.drone_atk_interval[slot]
				self.drone_atk = op_data.drone_atk_e0[slot][0] + (op_data.drone_atk_e0[slot][1]-op_data.drone_atk_e0[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)
				if elite == 1: self.drone_atk = op_data.drone_atk_e1[slot][0] + (op_data.drone_atk_e1[slot][1]-op_data.drone_atk_e1[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)
				if elite == 2: self.drone_atk = op_data.drone_atk_e2[slot][0] + (op_data.drone_atk_e2[slot][1]-op_data.drone_atk_e2[slot][0]) * (level-1) / (max_levels[elite][rarity-1]-1)
			except:
				pass #fuck you, Tragodia
			
		
		############### Buffs
		self.buff_name = "" #needed to put the conditionals before the buffs
		self.atk = self.atk * params.base_buffs[0] + params.base_buffs[1]
		if params.base_buffs[0] > 1: self.buff_name += f" bAtk+{int(100*(params.base_buffs[0]-0.999999))}%"
		elif params.base_buffs[0] < 1: self.buff_name += f" bAtk{int(100*(params.base_buffs[0]-1.000001))}%"
		if params.base_buffs[1] > 0: self.buff_name += f" bAtk+{int(params.base_buffs[1])}"
		elif params.base_buffs[1] < 0: self.buff_name += f" bAtk{int(params.base_buffs[1])}"

		self.buff_atk = params.buffs[0]
		if self.buff_atk > 0: self.buff_name += f" atk+{int(100*self.buff_atk)}%"
		elif self.buff_atk < 0: self.buff_name += f" atk{int(100*self.buff_atk)}%"
		
		self.attack_speed += params.buffs[2]
		if params.buffs[2] > 0: self.buff_name += f" aspd+{params.buffs[2]}"
		elif params.buffs[2] < 0: self.buff_name += f" aspd{params.buffs[2]}"

		self.buff_atk_flat = params.buffs[1]
		if self.buff_atk_flat > 0: self.buff_name += f" atk+{int(self.buff_atk_flat)}"
		elif self.buff_atk_flat < 0: self.buff_name += f" atk{int(self.buff_atk_flat)}"

		self.buff_fragile = params.buffs[3]
		if self.buff_fragile > 0: self.buff_name += f" dmg+{int(100*self.buff_fragile)}%"
		elif self.buff_fragile < 0: self.buff_name += f" dmg{int(100*self.buff_fragile)}%"

		if self.sp_boost > 0: self.buff_name += f" +{self.sp_boost}SP/s"

		if params.shred[0] != 1: self.buff_name += f" -{int(100*(1-params.shred[0])+0.0001)}%def" 
		if params.shred[1] != 0: self.buff_name += f" -{int(params.shred[1])}def"
		if params.shred[2] != 1: self.buff_name += f" -{int(100*(1-params.shred[2])+0.0001)}%res"
		if params.shred[3] != 0: self.buff_name += f" -{int(params.shred[3])}res"

		if params.mul_add[0] != 1: self.buff_name += f" x{int(params.mul_add[0])}"
		if params.mul_add[1] > 0: self.buff_name += f" +{int(params.mul_add[1])}"
		if params.mul_add[1] < 0: self.buff_name += f" {int(params.mul_add[1])}"

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
				case _: pass
			return True
		return False
		
	def skill_dps(self, defense, res):
		print("The operator has not implemented the skill_dps method")
		return -100
	
	def total_dmg(self,defense,res):
		if self.skill_duration < 1 or self.skill == 0:
			return (self.skill_dps(defense,res))
		else:
			return (self.skill_dps(defense,res) * self.skill_duration)
	
	def avg_dps(self,defense,res):
		if self.skill_duration < 1 or self.skill == 0:
			return (self.skill_dps(defense,res))
		else:
			tmp = self.skill
			skill_dps = self.skill_dps(defense,res)
			self.skill = 0
			offskill_dps = self.skill_dps(defense,res)
			self.skill = tmp
			cycle_dmg = skill_dps * self.skill_duration + offskill_dps * self.skill_cost/(1+self.sp_boost)
			dps = cycle_dmg / (self.skill_duration+self.skill_cost/(1+self.sp_boost))
			return dps
	
	def get_name(self):
		return self.name + self.buff_name


class NewBlueprint(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("NewBlueprint",pp,[1,2,3],[2,1],3,1,1) #available skills, available modules, default skill, def pot, def mod

		if self.trait_dmg or self.talent_dmg or self.talent2_dmg: self.name += " withBonus"
		if self.skill == 3 and self.skill_dmg: self.name += " overcharged"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = 1 if self.module == 1 and self.module_dmg else 1
		print(self.skill_params)
		print(self.talent1_params)
		print(self.talent2_params)
		atkbuff = 0# self.talent1_params[0]
		aspd = 0# self.talent2_params[0]
		
		if self.skill != 5:
			atkbuff += self.skill_params[0]
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps
	
class Guide(Operator):
	def __init__(self, pp, *args, **kwargs):
		#the name given to the init function can be found and must be updated in Database/JsonReader.py
		super().__init__("NewBlueprint",pp,[1,2,3],[2,1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		#kwargs include stuff like hits received per second and maybe soon stacks, summon counts and more. see penance for the use

		if self.trait_dmg or self.talent_dmg or self.talent2_dmg and self.elite > 0: self.name += " withBonus"
		if self.skill == 3 and self.skill_dmg: self.name += " overcharged"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dps = defense + res #are all numpy arrays of the same size. especially the dps getting returned needs the same size, which needs to be factored in for true dmg
		self.atk #is the base attack. this already includes boni from trust, potentials and modules, as well as increases from the baseatk buffs from prompts
		self.drone_atk #same for the summons, except it does not include base atk buffs (which maybe should be changed). should automatically search the right stats for the right skill. skill = 0 will always use the largest skill number instead
		self.attack_speed #is 100 + whatever boni come from module upgrades or potentials. this also includes aspd buff from prompts.
		#note that attack_speed is its own data type, that always stays within 20 and 600 when you add/subtract integers. after multiplication the type is lost and gives a float

		self.atk_interval #self explanatory. make sure not to overwrite this if a skill changes it. it may be accessed multiple time for showing dmg numbers in the graph
		self.drone_atk_interval #same for summons

		self.buff_atk #atk buff from the prompt for example warfarin giving 0.9
		self.buff_atk_flat #same but flat values, like 250ish from skalter
		self.buff_fragile #10% fragile being 0.1, this is automatically accounted for in the dps and you only need to access it with operators having their own fragile, to see which is stronger. see Iana/suzuran
		self.sp_boost #is for ptilopsis buff
		
		self.skill #the requested skill, can be 0,1,2,3
		self.skill_cost #sp cost of the skill
		self.skill_duration #written duration for the skill. unlimited and instant skills usually are -1
		self.skill_params #the VALUES of the skill in the order as given by the game files. it is a list with length depending on the skills. degen s3 has like 10+ entries, other skills have only 1, still a list
		self.talent1_params #and
		self.talent2_params #are the same for the talents. this automatically includes the correct changes from promition level, the potentials and USUALLY also the module, but modules tend to mix around the order, so watch out for that

		self.module #can be 0 for no module, 1 for x, 2 for y and 3 for alpha/delta
		self.module_lvl #is 0,1,2 or 3

		self.targets #are the targets given prompts. automatically clamped between 1 and 128
		self.elite # is 0,1,2

		self.trait_dmg and self.talent_dmg and self.talent2_dmg and self.skill_dmg and self.module_dmg #are booleans for the conditionals

		self.base_name #is the name prior to setting the conditionals and buff descriptions. only needed for the short prompt
		self.buff_name #the buff description
		
		atk_scale = 1 if self.module == 1 and self.module_dmg else 1
		print(self.skill_params)
		print(self.talent1_params)
		print(self.talent2_params)
		atkbuff = 0# self.talent1_params[0]
		aspd = 0# self.talent2_params[0]
		
		if self.skill != 5:
			atkbuff += self.skill_params[0]
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps


class Defense(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("12F",pp,[],[],0,6,0) #just here so the plot function doesnt break
		self.name = "defense"
	def skill_dps(self, defense, res):
		return defense
class Res(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("12F",pp,[],[],0,6,0) #just here so the plot function doesnt break
		self.name = "res"
	def skill_dps(self, defense, res):
		return res

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
		if self.module == 1 and self.module_lvl > 1: crate = 0.25 + 0.75 * 0.2 if self.module_lvl == 2 else 0.25 + 0.75 * 0.3
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat if self.skill == 3 else self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		aspd = self.skill_params[0] if self.skill == 1 else self.skill_params[1] * self.skill / 3
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		avghit = (1-crate) * hitdmg + crate * critdmg
		dps = avghit/self.atk_interval * (self.attack_speed + aspd)/100
		return dps

class Absinthe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Absinthe",pp,[1,2],[1],2,6,1)
		if self.skill == 2 and self.module == 1 and self.module_lvl > 1: self.talent_dmg = True
		if self.talent_dmg and self.elite > 0: self.name += " lowHpTarget"
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 1
		newres = np.fmax(0,res-10) if self.module == 1 else res
		final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat if self.skill == 1 else self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		atk_scale = 4 * self.skill_params[1] if self.skill == 2 else 1
		hitdmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05) * dmg_scale	
		dps = hitdmgarts/self.atk_interval * self.attack_speed/100
		return dps

class Aciddrop(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Aciddrop",pp,[1,2],[1],2,6,1)
		if self.talent_dmg and self.elite > 0: self.name += " directFront"

	def skill_dps(self, defense, res):
		if self.elite == 0: mindmg = 0.05
		elif self.talent_dmg: mindmg = self.talent1_params[1]
		else: mindmg = self.talent1_params[0]
		aspd = self.skill_params[0] if self.skill == 1 else 0
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * mindmg)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * max(1, self.skill)
		return dps

class Adnachiel(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Adnachiel",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0]
		final_atk = self.atk * (1 + self.skill_params[0] * self.skill + self.buff_atk) + self.buff_atk_flat
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
		if self.skill < 2:
			aspd = self.skill_params[0] * self.skill
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
	
class AmiyaGuard(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("AmiyaGuard",pp,[1,2],[1],1,6,1)
		if self.module == 1 and self.module_dmg: self.name += " NotBlocking"
		if self.skill == 2:
			if self.skill_dmg: self.name += " 3kills"
			else: self.name += " no kills"
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + 2 * self.talent1_params[0]) + self.buff_atk_flat
			nukedmg = final_atk * 9 * skill_scale * (1+self.buff_fragile)
			truedmg = final_atk * 2 * skill_scale * (1+self.buff_fragile)
			self.name += f"  Nuke:{int(nukedmg)}Arts+{int(truedmg)}True"
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] * (1 + min(1, self.skill))
		aspd = 8 if self.module == 1 and self.module_dmg else 0
		if self.skill < 2:
			atkbuff += self.skill_params[0] * self.skill
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05)
			dps = (1 + self.skill) * hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			if self.skill_dmg:
				atkbuff += 3 * self.skill_params[3]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			dps = final_atk/(self.atk_interval/((self.attack_speed+aspd)/100)) * np.fmax(1,-defense) #this defense part has to be included
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
		if self.skill < 2:
			aspd = self.skill_params[0] * self.skill
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
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
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

		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
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
		aspd = self.skill_params[1] if self.skill == 1 else 0
		if self.skill < 2:
			final_atk = self.atk * (1 + self.skill_params[0] * self.skill + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * self.targets
		if self.skill == 2:
			final_atk = self.atk * (1 + self.skill_params[1] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / 3.45 * self.attack_speed / 100 * self.targets
			talent_scale *= 2
		active_ratio = min(1, talent_duration/ (self.atk_interval / (self.attack_speed+aspd) * 100))
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
		if self.skill != 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill/2) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Archetto(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Archetto",pp,[1,2,3],[2,1],3,1,1)
		if self.module == 1 and self.module_lvl > 1 and self.talent_dmg and self.skill != 3: self.name += " +2ndSniper"	
		if self.module_dmg and self.module == 1: self.name += " aerialTarget"
		if self.module_dmg and self.module == 2: self.name += " GroundEnemy"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		aspd = 8 if self.module == 2 and self.module_dmg else 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		recovery_interval = max(self.talent1_params) if self.elite > 0 else 10000000
		if self.module == 1 and self.talent_dmg and self.module_lvl > 1:
			recovery_interval -= 0.3 if self.module_lvl == 2 else 0.4

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			skill_scale2= self.skill_params[1]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			aoedmg = np.fmax(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05)
			
			#figuring out the chance of the talent to activate during downtime
			base_cycle_time = (sp_cost+1)/((self.attack_speed+aspd)/100)
			talents_per_base_cycle = base_cycle_time / recovery_interval
			failure_rate = 1.8 / (sp_cost + 1)  #1 over sp cost because thats the time the skill would technically be ready, the bonus is for sp lockout. (basis is a video where each attack had 14 frames, but it was 25 frames blocked)
			talents_per_base_cycle *= 1-failure_rate
			new_spcost = np.fmax(1,sp_cost - talents_per_base_cycle)
			hitdps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * (new_spcost-1)/new_spcost
			skilldps = skilldmg/(self.atk_interval/((self.attack_speed+aspd)/100)) /new_spcost
			aoedps = aoedmg/(self.atk_interval/((self.attack_speed+aspd)/100)) /new_spcost *(min(self.targets,4)-1)
			dps = hitdps + skilldps + aoedps
				
		if self.skill == 2:
			sprecovery = 1/recovery_interval + (self.attack_speed+aspd)/100
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			targets = min(5, self.targets)
			totalhits = [5,9,12,14,15]
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) + sprecovery/self.skill_cost * skilldmg * totalhits[targets-1]
		
		if self.skill in [0,3]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill/3) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * (1 + self.skill * 2 / 3)
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
			if self.skill == 3: dps *= min(self.targets, 2)
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
		if self.skill == 0:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			dps = 2 * hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			hitdmgarts = np.fmax(final_atk * skill_scale * atk_scale  * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100 * min(2,self.targets)
		return dps

class Asbestos(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Asbestos",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		extra_scale = 0.1 if self.module == 1 else 0
		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1 + extra_scale) * (1-res/100), final_atk * (1 + extra_scale) * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1 + extra_scale) * (1-res/100), final_atk * (1 + extra_scale) * 0.05)
			dps = hitdmg/2 * self.attack_speed/100 * self.targets
		return dps

class Ascalon(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ascalon",pp,[1,2,3],[1,2],3,1,1)
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
		if self.skill in [0,2]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill/2) + self.buff_atk_flat
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

		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.skill)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			if self.skill_dmg: atk_scale *= self.skill_params[1] 
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dmg_bonus = self.talent1_params[2] if self.module == 1 and self.module_lvl > 1 and self.skill_dmg else 1
			dps = hitdmg/0.2 * (self.attack_speed+aspd)/100 * dmg_bonus
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 2:
			return(self.skill_dps(defense,res) * 31 * (0.2/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Ashlock(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ashlock",pp,[1,2],[1],2,1,1)
		if not self.talent_dmg: self.name += " LowTalent"
		if self.module_dmg and self.module == 1: self.name += " blockedTarget"	
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe			
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.talent_dmg else self.talent1_params[0]
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
		atk_interval = self.atk_interval if self.skill != 2 else self.atk_interval * (1 + self.skill_params[1])
		dps = hitdmg / atk_interval * self.attack_speed/100 * self.targets
		return dps

class Astesia(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Astesia", pp, [1,2],[2],2,1,2)
		if self.talent_dmg: self.name += " maxStacks"
		if self.module == 2 and self.module_dmg: self.name += " blocking"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dmg = 1.1 if self.module == 2 and self.module_dmg else 1
		aspd = self.talent1_params[0] * self.talent1_params[2] if self.talent_dmg else 0
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd)/100 * dmg
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
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * targetscaling[targets]
			skill_targetscaling = [0,1,4,6,8] if self.module == 2 else [0, 1, 2 * 1.85, 2*(1.85+0.85**2), 2*(1.85+0.85**2+0.85**3)]
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * skill_targetscaling[targets]
			if self.skill == 0: skilldmg = hitdmg
			sp_cost = sp_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1 and self.skill == 1:
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Aurora",pp,[1,2],[1],2,1,1)
		if self.skill_dmg and self.skill == 2: self.name += " 1/3vsFreeze"

	def skill_dps(self, defense, res):
		atk_interval = 1.85 if self.skill == 2 else self.atk_interval
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		skill_scale = self.skill_params[3]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		skilldmg =  np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
		avgdmg = hitdmg
		if self.skill_dmg and self.skill == 2: avgdmg = 2/3 * hitdmg + 1/3 * skilldmg			
		dps = avgdmg/atk_interval * self.attack_speed/100
		return dps

class Ayerscarpe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ayerscarpe",pp,[1,2],[1],2,1,1)
		if not self.trait_dmg and self.skill == 1: self.name += " rangedAtk"   
		if self.targets > 1 and self.skill > 0: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atk_scale = 0.8 if not self.trait_dmg and self.skill == 1 else 1
		bonus = 0.1 if self.module == 1 else 0
		aspd = self.talent1_params[0] if self.elite > 0 else 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill < 2:
			skill_scale = self.skill_params[0]
			targets = self.skill_params[2] if self.skill == 1 else 1
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale *(1-res/100), final_atk * skill_scale * 0.05) * min(self.targets,targets)
			avgdmg = (self.skill_cost * hitdmg + skilldmg)/(self.skill_cost + 1)
			if self.skill == 0: avgdmg = hitdmg
			dps = (avgdmg + bonusdmg) / self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			skilldmg *= self.targets if self.trait_dmg else self.targets -1
			dps = (hitdmg + bonusdmg + skilldmg) / self.atk_interval * (self.attack_speed+aspd)/100
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

		if self.skill < 2:
			atkbuff = self.skill_params[0] * self.skill
			aspd = self.skill_params[1] * self.skill
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Beehunter",pp,[1,2],[1],2,6,1)
		if self.talent_dmg and self.elite > 0: self.name += " maxStacks"
		if self.module == 1:
			if self.module_dmg: self.name += " >50% hp"				
			else: self.name += " <50% hp"

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] * self.talent1_params[1] if self.talent_dmg else 0
		aspd = 10 if self.module == 1 and self.module_dmg else 0
		atk_interval = self.atk_interval * (1 + self.skill_params[0]) if self.skill == 2 else self.atk_interval
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/atk_interval * (self.attack_speed+aspd)/100
		return dps

class Beeswax(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Beeswax",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			nukehit = final_atk * self.skill_params[0]
			self.name += f" InitialHit:{int(nukehit)}"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill == 0: return res * 0
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
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

		if self.skill < 2:
			skill_scale = self.skill_params[0]
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * dmg_multiplier
			skillartsdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_multiplier
			if self.skill == 0: skillhitdmg = hitdmg
			sp_cost = self.skill_cost
			avg_phys = 2 * (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avg_arts = 0 if self.targets == 1 else skillartsdmg / (sp_cost +1) * self.skill
			dps = (avg_phys+avg_arts)/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2:
			skill_scale = self.skill_params[2]
			skillartsdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_multiplier
			avg_hit = (2 * hitdmg * self.skill_cost + skillartsdmg * min(self.targets, self.skill_params[0])) / self.skill_cost
			dps = avg_hit/self.atk_interval * (self.attack_speed + aspd)/100
		return dps
	
class Blaze(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Blaze", pp, [1,2],[1,2],2,1,1)
		if self.elite == 2 and not self.talent2_dmg and not self.skill == 2: self.name += " w/o talent2"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		if self.module == 2 and self.module_dmg and self.module_lvl > 1: self.name += " >50%hp"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		newdef = np.fmax(0,defense-150) if self.module == 2 and self.module_dmg and self.module_lvl > 1 else defense
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
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) * min(self.targets, targets)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		else:
			atkbuff += self.skill_params[0] * self.skill/2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05) * min(self.targets,targets)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class BlazeAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("BlazeAlter",pp,[1,2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill in [1,2]:
			if not self.trait_dmg: self.name += " no Burn"
			else:
				if self.skill_dmg: self.name += " avgBurn"
				else: self.name += " avgBurn vsBoss"
		if self.skill == 3 and self.skill_dmg: self.name += " vsBurn"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		burst_scale = 1.1 if self.module == 1 and self.skill_dmg else 1
		falloutdmg = 7000
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		module_atk = 0.05 * (self.module_lvl - 1) if self.module == 1 and self.module_lvl > 1 and ((self.trait_dmg and self.skill != 3) or (self.skill_dmg and self.skill == 3)) else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		if self.elite > 0: falloutdmg += final_atk * self.talent1_params[0]

		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + module_atk) + self.buff_atk_flat
			newres = np.fmax(0,res-20)
			elegauge = 1000 if self.skill_dmg else 2000
			hitdmg1 = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) #number 2 is against enemies under burn fallout
			skilldmg1 = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			skilldmg2 = np.fmax(final_atk * skill_scale * (1-newres/100), final_atk * skill_scale * 0.05)
			dpsNorm = hitdmg1/self.atk_interval * (self.attack_speed)/100 + skilldmg1 * self.targets
			dpsFallout = hitdmg2/self.atk_interval * (self.attack_speed)/100 + skilldmg2 * self.targets
			timeToFallout = elegauge/(skilldmg1 * self.skill_params[1])
			dps = (dpsNorm * timeToFallout + dpsFallout * burst_scale * 10 + falloutdmg)/(timeToFallout + 10)
			if not self.trait_dmg: dps = dpsNorm
		
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			skill_scale = self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff + module_atk) + self.buff_atk_flat
			newres = np.fmax(0,res-20)
			elegauge = 1000 if self.skill_dmg else 2000
			hitdmg1 = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * min(self.targets,3)
			hitdmg2 = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) * min(self.targets,3) #number 2 is against enemies under burn fallout
			skilldmg1 = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			skilldmg2 = np.fmax(final_atk * skill_scale * (1-newres/100), final_atk * skill_scale * 0.05)
			dpsNorm = hitdmg1/2.5 * (self.attack_speed)/100 + skilldmg1 * self.targets
			dpsFallout = hitdmg2/2.5 * (self.attack_speed)/100 + skilldmg2 * self.targets
			timeToFallout = elegauge/(skilldmg1 * self.skill_params[1])
			dps = (dpsNorm * timeToFallout + dpsFallout * burst_scale * 10 + falloutdmg)/(timeToFallout + 10)
			if not self.trait_dmg: dps = dpsNorm

		if self.skill == 3:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + module_atk) + self.buff_atk_flat
			newres = np.fmax(0,res-20) if self.skill_dmg else res
			ele_scale = self.skill_params[3] if self.skill_dmg else 0
			hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) + final_atk * ele_scale
			dps = hitdmg * burst_scale / 0.3 * self.attack_speed/ 100 * self.targets
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * self.skill_params[2] * (0.3/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Blemishine(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Blemishine",pp,[1,2,3],[2,1],3,1,1)
		if self.elite > 0:
			if self.talent2_dmg: self.name += " vsSleep"
			else: self.name += " w/o sleep"
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		atk_scale = self.talent2_params[0] if self.talent2_dmg else 1
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			if self.skill == 0: skilldmg = hitdmg
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
		atk_scale = 1 if self.skill < 2 and not self.talent_dmg else self.talent1_params[0]
		if self.skill < 2:
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
			
		if self.skill < 2:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * min(2,self.targets)
			if self.skill == 0: skillhitdmg = hitdmg
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/((self.attack_speed + aspd)/100)) + artsdps * min(1 + self.skill,self.targets)
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = self.skill_params[1] * hitdmg/(self.atk_interval/((self.attack_speed+ aspd)/100)) + hitdmg/(self.atk_interval/((self.attack_speed+ aspd)/100)) * min(2,self.targets-1) + artsdps * min(3, self.targets)
		return dps
		
class Broca(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Broca",pp,[1,2],[1],2,1,1)
		if self.talent_dmg and self.elite > 0: self.name += " blocking2+"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.talent_dmg else 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff += self.skill_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		atk_interval = 1.98 if self.skill == 2 else self.atk_interval
		hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05) if self.skill > 0 else np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/atk_interval * self.attack_speed/100 * min(3, self.targets)
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
		else:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill/2) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Cantabile(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Cantabile",pp,[1,2],[2],2,1,2)
		if self.elite > 0:
			if self.talent_dmg: self.name += " melee"
			else: self.name += " ranged"
		if self.skill == 2:
			aspd = self.talent1_params[0] if not self.talent_dmg else 0
			self.skill_duration = self.skill_params[3] * self.atk_interval / (self.attack_speed + aspd) * 100
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.talent_dmg else 0
		aspd = self.talent1_params[0] if not self.talent_dmg else 0
		if self.skill > 0:
			atkbuff += self.skill_params[0]
			aspd += self.skill_params[1]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Caper(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Caper",pp,[1,2],[1],2,6,1)
		if self.module == 1: self.trait_dmg = self.trait_dmg and self.module_dmg
		if not self.trait_dmg: self.name += " maxRange"
		else: self.name += " minRange"

	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.trait_dmg else 1
		crate = self.talent1_params[0] if self.elite > 0 else 0
		cdmg = self.talent1_params[1] if self.elite > 0 else 1
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * cdmg * atk_scale - defense, final_atk * cdmg * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			skillcritdmg = np.fmax(final_atk * cdmg * skill_scale * atk_scale - defense, final_atk * cdmg * skill_scale * atk_scale * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			skillhitdmg = skillcritdmg * crate + (1-crate) * skillhitdmg
			if self.skill == 0: skillhitdmg = hitdmg
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			interval = 20/13.6 if not self.trait_dmg else (self.atk_interval/(self.attack_speed/100)) #source: dr silvergun vid
			dps = avgphys/interval
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * cdmg * atk_scale - defense, final_atk * cdmg * atk_scale * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			interval = 20/13.6 if not self.trait_dmg else (self.atk_interval/(self.attack_speed/100))
			dps = 2 * hitdmg/interval
		return dps

class Carnelian(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Carnelian",pp,[1,2,3],[1,2],3,1,1)
		if self.skill_dmg and self.skill != 1: self.name += " charged"
		if self.skill == 3: self.name += " (averaged)"
		if self.module_dmg and self.module == 2: self.name += " manyTargets"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		if self.skill == 0: return (defense * 0)
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 2:
			atk_interval = self.atk_interval + self.skill_params[0]
			atkbuff = self.skill_params[2] if self.skill_dmg else 0
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 3:
			maxatkbuff = self.skill_params[0]
			duration = 21
			totalatks = 1 + int(duration / (self.atk_interval/(self.attack_speed/100))) # +1 because the first attack is already at 0
			totalduration = totalatks * (self.atk_interval/(self.attack_speed/100))
			damage = 0
			bonusscaling = 5 if self.skill_dmg else 0
			for i in range(totalatks):
				final_atk = self.atk * (1 + self.buff_atk + i * (self.atk_interval/(self.attack_speed/100)) /21 * maxatkbuff) + self.buff_atk_flat
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

		if self.skill < 2:
			sp_cost = self.skill_cost
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * skill_scale *(1-newres/100), final_atk * skill_scale * 0.05)
			if self.skill == 0: skilldmgarts = hitdmgarts
			defbonusdmg = np.fmax(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed+aspd)*100
			if self.module == 2 and self.module_dmg:
				sp_cost = sp_cost / (1 + 1/atkcycle + self.sp_boost) + 1.2 #bonus sp recovery vs elite mobs + sp lockout
			else:
				sp_cost = sp_cost /(1 + self.sp_boost) + 1.2 #sp lockout
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts
			if atks_per_skillactivation > 1 and self.skill == 1:
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Chen",pp,[1,2,3],[1,2],3,1,1)
		if self.skill == 3: self.name += " totalDMG"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		dmg = 1.1 if self.module == 1 else 1
		atkbuff = self.talent2_params[0] if self.elite == 2 else 0
		newdef = np.fmax(0, defense - 70) if self.module == 2 else defense
		sp_gain = self.talent1_params[1] / self.talent1_params[0] if self.elite > 0 else 0
		if self.module == 1 and self.module_lvl == 3: sp_gain *= 2

		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05) * 2
		if self.skill == 0: dps = hitdmg / self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			skilldmg = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05) * dmg
			sp_cost = self.skill_cost/(1/(self.atk_interval*self.attack_speed/100) + sp_gain)
			avghit = ( int(sp_cost / (1/(self.atk_interval*self.attack_speed/100))) * hitdmg + skilldmg)/(int(sp_cost / (1/(self.atk_interval*self.attack_speed/100)))+1)
			dps = avghit / self.atk_interval * self.attack_speed/100
		
		if self.skill == 2:
			hitdmgphys = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05) * dmg
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg
			skilldmg = hitdmgphys + hitdmgarts
			sp_cost = self.skill_cost/(1/(self.atk_interval*self.attack_speed/100) + sp_gain)
			dps = hitdmg / self.atk_interval * self.attack_speed/100 + skilldmg/sp_cost * min(self.targets, self.skill_params[1])
			
		if self.skill == 3:
			hitdmg = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05) * dmg
			dps = 10 * hitdmg
		return dps

class ChenAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ChenAlter",pp,[1,3],[1,2],3,1,2)
		if self.skill == 0 and not self.trait_dmg: self.name += " maxRange"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		aspd = 8 if self.elite == 2 else 0 #im not going to include the water buff for now
		if self.module == 2:
			if self.module_lvl == 2: atkbuff += 0.1
			if self.module_lvl == 3:
				atkbuff += 0.28
				aspd = 20
			
		atk_scale = 1.6 if self.module == 1 else 1.5
		if self.skill == 0 and not self.trait_dmg: atk_scale = 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		
		if self.skill < 2:
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
		if self.skill == 3:
			ammo = 16
			save_rate = self.talent1_params[0]
			ammo = ammo/(1-save_rate)
			return(self.skill_dps(defense,res) * ammo * (self.atk_interval/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Chongyue(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Chongyue",pp,[1,3],[1,2],3,1,2)
		if self.module == 2 and self.module_dmg: self.name += " >50%Hp"
		if self.skill == 1 and self.elite > 0 and not self.talent_dmg: self.name += " NoSkillCrit"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		aspd = 10 if self.module == 2 and self.module_dmg else 0
		crate = self.talent1_params[0] if self.elite > 0 else 0
		dmg = self.talent1_params[1] if self.elite > 0 else 1
		duration = self.talent1_params[2] if self.elite > 0 else 0

		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
		if self.skill < 2:
			if self.talent_dmg and self.elite > 0: skilldmg *= dmg
			relevant_hits = int(duration/(self.atk_interval /(self.attack_speed+aspd)*100)) + 1
			crit_chance = 1 - (1-crate) ** relevant_hits
			hitdmg *= (1-crit_chance) + dmg * crit_chance
			dps = (hitdmg + skilldmg/self.skill_cost * self.skill) / self.atk_interval * (self.attack_speed+aspd)/100

		if self.skill == 3:
			hits = self.skill_cost // 2 + self.skill_cost % 2
			relevant_hits = int(duration/(self.atk_interval /(self.attack_speed+aspd)*100)) * 2 + 2
			relevant_hits *= hits/(hits+1) #skill hits cant trigger crit and therefore technically have a lower crit rate than normal attacks, but ehh
			crit_chance = 1 - (1-crate) ** relevant_hits
			skilldmg *= self.targets
			avghit = 2 * (hits * hitdmg + skilldmg) /(hits + 1) * ((1-crit_chance) + dmg * crit_chance)
			dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Click",pp,[1,2],[2],2,6,2)
		if not self.trait_dmg: self.name += " minDroneDmg"

	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0]
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		drone_dmg = 1.2 if self.module == 2 else 1.1
		if not self.trait_dmg: drone_dmg = 0.2
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		dmgperinterval = final_atk + drone_dmg * final_atk
		hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/self.atk_interval * (self.attack_speed + aspd) / 100
		return dps

class Coldshot(Operator):
	def __init__(self, pp, *args,**kwargs):
		super().__init__("Coldshot",pp,[1,2],[1],2,6,1)
		if not self.trait_dmg: self.name += " outOfAmmo"
		elif self.elite > 0:
			ammo = 4 + 2 * self.elite
			if self.talent_dmg: self.name += f" TalentOn1/{ammo}Shots"
			else: self.name += " idealTalentUsage"
	
	def skill_dps(self, defense, res):
		ammo = 4 + 2 * self.elite
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		atk_scale = 1.2
		talent_scale = self.talent1_params[0] if self.elite > 0 else 1
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		reload_time = 2.4 if self.skill == 2 else 1.6 
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		hitdmg2 = np.fmax(final_atk * atk_scale * talent_scale - defense, final_atk * atk_scale * talent_scale * 0.05)
		if self.atk_interval/self.attack_speed*100 >= 2: hitdmg = hitdmg2 #if attacks are so slow that the talent actually activates
		
		if self.trait_dmg: #full clip
			if self.talent_dmg or self.atk_interval/self.attack_speed*100 >= 2:
				dps = (hitdmg * (ammo -1) + hitdmg2) / ammo / self.atk_interval * self.attack_speed/100
			else:
				dps = hitdmg2 / 2
		else:
			if self.module != 1:
				dps = hitdmg2/(self.atk_interval/self.attack_speed*100 + reload_time)
			else:
				if self.atk_interval/self.attack_speed*100 >= 2:
					dps = hitdmg2 * 2 /(self.atk_interval/self.attack_speed*100 * 2 + reload_time)
				else:
					dps = (hitdmg2 + hitdmg) /(self.atk_interval/self.attack_speed*100 * 2 + reload_time)
		return dps

class Contrail(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Contrail",pp,[1,2],[],2,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		if self.targets > 2 and self.skill == 2: self.name += "(including1Drone)"
	
	def skill_dps(self, defense, res):
		targets = 3 if self.skill == 2 else 1
		atk_scale = self.talent1_params[0] if self.elite > 0 else 1
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100 * min(self.targets, targets)
		return dps

class Conviction(Operator):
	def __init__(self, pp, *args, **kwargs):
		pp.pot = 6
		super().__init__("Conviction",pp,[1,2],[1],1,6,1)
		self.name = self.name.replace(" P6","")
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		if self.skill == 2 and self.skill_dmg: self.name += " SkillSuccess"
		if self.skill == 2 and not self.skill_dmg: self.name += " selfstun"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1

		if self.skill < 2:
			skill_scale = (self.skill_params[0]-1) * self.skill + 1
			skill_scale2 = (self.skill_params[3]-1) * self.skill + 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg1 = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skilldmg2 = np.fmax(final_atk * atk_scale * skill_scale2 - defense, final_atk* atk_scale * skill_scale2 * 0.05)	
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg1 * 0.95 + skilldmg2 * 0.05
			if atks_per_skillactivation > 1:
				avghit = (0.95 * skilldmg1 + 0.05 * skilldmg2 + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
			dps = avghit/self.atk_interval * self.attack_speed/100

		if self.skill == 2:
			skill_scale = self.skill_params[1]
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05) * self.targets
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.skill_dmg: 
				dps += skilldmg / sp_cost
			else:
				dps *= (sp_cost -5)/sp_cost
		return dps

class Crownslayer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Crownslayer",pp,[1,3],[1,2],3,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 1 and not self.talent2_dmg: self.name += " dmgTaken"
		if self.skill == 3 and not self.skill_dmg: self.name += " singleTargetOnly"
		if self.module == 2 and self.module_dmg: self.name += " alone"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.1 if self.module_dmg and self.module == 2 else 0
		atk_scale = self.talent2_params[0] if self.talent2_dmg and self.elite == 2 else 1
		if self.skill < 2:
			final_atk = self.atk * (1 + self.skill_params[0]*self.skill + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 3:
			skill_scale = self.skill_params[3]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg
			if not self.skill_dmg: dps *= 1/3
		return dps

class Dagda(Operator):
	def __init__(self, pp, *args,**kwargs):
		super().__init__("Dagda",pp,[1,2],[1],2,6,1)
		if self.talent_dmg and self.elite > 0: self.name += " maxStacks"
		elif self.elite > 0 : self.name += " noStacks"
		if self.module_dmg and self.module == 1: self.name += " >50%hp"
	
	def skill_dps(self, defense, res):
		aspd = 10 if self.module == 1 and self.module_dmg else 0
		crate = 0.3
		cdmg = self.talent1_params[2] if self.talent_dmg else self.talent1_params[1]
		if self.elite == 0: cdmg = 1
		if self.skill == 2: crate = self.skill_params[1]
		hits = 2 if self.skill == 2 else 1
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		avgdmg = crate * critdmg + (1-crate) * hitdmg
		dps = hits * avgdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Degenbrecher(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Degenbrecher",pp,[1,3],[1],3,1,1)		
		if self.skill == 3: self.name += " totalDMG"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		newdef = defense * (1 - self.talent2_params[0]) if self.elite == 2 else defense
		dmg = 1.1 if self.module == 1 else 1
		atk_scale = self.talent1_params[1] if self.elite > 0 else 1
			
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * 2
			hitdmg_crit = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05) * 2
			hitdmg_tremble = np.fmax(final_atk - newdef, final_atk * 0.05) * 2
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * dmg * 2
			skilldmg_crit = np.fmax(final_atk * skill_scale * atk_scale - newdef, final_atk * skill_scale * atk_scale * 0.05) * dmg * 2
			skilldmg_tremble = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05) * dmg * 2
			crate = 0 if self.elite == 0 else self.talent1_params[0]
			relevant_attack_count = int(5/(self.atk_interval / self.attack_speed * 100)) * 2 #tremble lasts 5 seconds
			chance_that_no_crit_occured = (1-crate) ** relevant_attack_count
			avghit = hitdmg_crit * crate + hitdmg * (1-crate) * chance_that_no_crit_occured + hitdmg_tremble * (1-crate) * (1 - chance_that_no_crit_occured)
			avgskill = skilldmg_crit * crate + skilldmg * (1-crate) * chance_that_no_crit_occured + skilldmg_tremble * (1-crate) * (1 - chance_that_no_crit_occured) * min(self.targets,self.skill_params[1])
			if self.skill == 0: avgskill = avghit
			average = (self.skill_cost * avghit + avgskill)/(self.skill_cost + 1)
			dps = average/self.atk_interval * self.attack_speed/100

		if self.skill == 3:
			skill_scale = self.skill_params[2]
			last_scale = self.skill_params[6] 
			hitdmg1 = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05) * dmg
			hitdmg2 = np.fmax(final_atk * atk_scale * last_scale - newdef, final_atk * atk_scale * last_scale * 0.05) * dmg
			dps = (10 * hitdmg1 + hitdmg2) * min(self.targets,self.skill_params[1])
		return dps

class Diamante(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Diamante",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2:
			if self.talent_dmg and self.skill_dmg: self.name += " vsFallout(800dpsNotIncluded)"
			else: self.name += " noNecrosis"
			if self.targets > 1: self.name += f" {self.targets}targets"
		elif self.skill == 1:
			if not self.trait_dmg: self.name += " noNecrosis"
			elif not self.talent_dmg and not self.skill_dmg: self.name += " avgNecrosis(vsBoss)"
			elif self.talent_dmg ^ self.skill_dmg: self.name += " avgNecrosis(nonBoss)"
			else: self.name += " vsFallout(800dpsNotIncluded)"
	
	def skill_dps(self, defense, res):
		burst_scale = 1.1 if self.module == 1 else 1
		if self.skill in [0,2]:
			atkbuff = self.talent1_params[0] if self.talent_dmg and self.skill_dmg and self.skill == 2 else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			skill_scale = self.skill_params[1] if self.talent_dmg and self.skill_dmg and self.skill == 2 else 0
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			eledmg =  np.fmax(final_atk * 0 * (1-res/100), final_atk * skill_scale) /(1+self.buff_fragile) * burst_scale
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
			fallout_dps = 12000 / (time_to_apply_necrosis + 15) /(1+self.buff_fragile)

			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmg_necro = np.fmax(final_atk_necro * (1-res/100), final_atk_necro * 0.05)
			eledmg_necro =  np.fmax(final_atk_necro * 0 * (1-res/100), final_atk_necro * skill_scale) /(1+self.buff_fragile)
			avg_hitdmg = hitdmg * time_to_apply_necrosis / (time_to_apply_necrosis + 15) + hitdmg_necro * 15 / (time_to_apply_necrosis + 15)
			avg_eledmg = eledmg_necro * 15 / (time_to_apply_necrosis + 15)

			if not self.trait_dmg: dps = (hitdmg) / self.atk_interval * (self.attack_speed) / 100
			elif not self.talent_dmg and not self.skill_dmg: dps = fallout_dps + (avg_hitdmg + avg_eledmg * burst_scale) / self.atk_interval * (self.attack_speed) / 100
			elif self.talent_dmg ^ self.skill_dmg: dps = fallout_dps + (avg_hitdmg + avg_eledmg * burst_scale) / self.atk_interval * (self.attack_speed) / 100
			else: dps = (hitdmg_necro + eledmg_necro) * burst_scale / self.atk_interval * (self.attack_speed) / 100

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

		if self.skill < 2:
			skill_scale = self.skill_params[0]			
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			if self.skill == 0: avgphys = hitdmg
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
		atk_interval = self.atk_interval + self.skill_params[3] if self.skill == 1 else self.atk_interval
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
		dps = hitdmg/atk_interval * self.attack_speed/100
		return dps

class Dorothy(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Dorothy",pp,[1,2,3],[2,1],3,1,2)
		if not self.trait_dmg or self.skill == 0: self.name += " noMines"
		else:
			if not self.talent_dmg: self.name += " 1MinePerSPcost"
			else: self.name += " 1MinePer5s"
			if self.skill == 1 and self.skill_dmg: " withDefshredNormalAtks"
		if self.talent2_dmg: self.name += " maxTalent2"
		if self.module == 1 and self.module_lvl == 3 and self.module_dmg: self.name += " +ExtraMines"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atkbuff = self.talent2_params[0] * self.talent2_params[1] if self.talent2_dmg else 0
		cdmg = 1.2 if self.module == 2 else 1
		if self.module == 1 and self.module_lvl == 3 and self.module_dmg: cdmg = 1.5
		sp_cost = max(self.skill_cost / (1+ self.sp_boost),5)
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		mine_scale = self.skill_params[1] if self.trait_dmg and self.skill > 0 else 0

		if self.skill == 1:
			defshred = 1 + self.skill_params[2]
			hitdmgmine = np.fmax(final_atk * mine_scale - defense * defshred, final_atk * mine_scale * 0.05) * cdmg	
			if not self.trait_dmg or not self.skill_dmg:
				defshred = 1
			elif not self.talent_dmg:
				defshred = 1 + 5 / sp_cost * self.skill_params[2]  #include uptime of the debuff for auto attacks
			hitdmg = np.fmax(final_atk - defense * defshred, final_atk * 0.05)
		if self.skill in [0,2]:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgmine = np.fmax(final_atk * mine_scale - defense, final_atk * mine_scale * 0.05) * cdmg
		if self.skill == 3:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgmine = np.fmax(final_atk * mine_scale * (1-res/100), final_atk * mine_scale * 0.05) * cdmg
		minedps = hitdmgmine/5 if self.talent_dmg else hitdmgmine/sp_cost
		dps = hitdmg/self.atk_interval * self.attack_speed/100 + minedps * self.targets
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
		super().__init__("Durnar",pp,[1,2],[1],2,6,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		extra_scale = 0.1 if self.module == 1 else 0
		final_atk = self.atk * (1 + self.skill_params[0] * min(self.skill,1) + self.buff_atk + self.talent1_params[0]) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1 + extra_scale) * (1-res/100), final_atk * (1 + extra_scale) * 0.05) if self.skill > 0 else np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2: dps *= min(self.targets,3)
		return dps

class Dusk(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Dusk",pp,[1,2,3],[1,2,3],3,1,1)
		if self.talent_dmg and self.elite > 0: self.name += f" {int(self.talent1_params[1])}stacks"
		if self.talent2_dmg and self.elite == 2: self.name += " +Freeling"
		if self.skill == 2 and self.skill_dmg: self.name += " vsLowHp"		
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.module == 3: self.name += " MOD NOT PROPERLY IMPLEMENTED YET"
		if self.module == 2:
			if self.module_lvl == 2: self.drone_atk += 15
			if self.module_lvl == 3: self.drone_atk += 25

	def skill_dps(self, defense, res):
		freedps = 0
		if self.talent2_dmg:
			final_freeling = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
			freehit = np.fmax(final_freeling - defense, final_freeling * 0.05)
			freedps = freehit/self.drone_atk_interval
		
		atkbuff = self.talent1_params[0] * self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 0

		if self.skill < 2:
			skill_scale = (self.skill_params[0]-1) * self.skill + 1
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2 #lockout
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)		
			dps = avghit/self.atk_interval * self.attack_speed/100 * self.targets	
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			atk_scale = self.skill_params[3] if self.skill_dmg else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + self.skill_params[1])/100 * self.targets
		if self.skill == 3:
			atkbuff += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/4.06 * self.attack_speed/100 * self.targets
		return dps+freedps

class Ebenholz(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ebenholz",pp,[1,3],[1,2,3],3,1,3)
		if not self.talent_dmg and self.module == 2: self.module_dmg = False
		if self.talent_dmg and self.elite > 0: self.name += " +Talent1Dmg"
		if self.module == 3 and self.talent2_dmg: self.name += " withAvgNecrosis"
		if self.module_dmg and self.module == 2: self.name += " +30aspd(mod,somehow)"
		if not self.module_dmg and self.module == 3: self.name += " vsBoss"
		if self.targets > 1 and self.elite == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		aspd = 30 if self.module_dmg and self.module == 2 else 0
		atk_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		eledmg = 0
		bonus_scale = self.talent2_params[0] if self.targets == 1 and self.elite == 2 else 0
		eledmg = self.module_lvl * 0.1 /(1+self.buff_fragile) if self.module == 3 and self.module_lvl > 1 and self.talent2_dmg else 0
		extra_scale = self.talent2_params[3] if self.module == 2 and self.module_lvl > 1 else 0
			
		if self.skill < 2:
			skill_scale = self.skill_params[1] if self.skill == 1 else 1
			atk_interval = self.atk_interval * self.skill_params[0] if self.skill == 1 else self.atk_interval
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
			extradmg = np.fmax(final_atk * extra_scale * (1-res/100), final_atk * extra_scale * 0.05)
			dps = hitdmg/(atk_interval/((self.attack_speed + aspd)/100))
			if self.module == 3:
				ele_gauge = 1000 if self.module_dmg else 2000
				eledps = dps * 0.08
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)/(1+self.buff_fragile)
				dps += eledmg * final_atk /(self.atk_interval/((self.attack_speed + aspd)/100)) * 15/(fallouttime + 15)
			if self.targets == 1:
				dps += bonusdmg/(atk_interval/((self.attack_speed + aspd)/100))
			if self.targets > 1 and self.module == 2:
				dps += extradmg/(atk_interval/((self.attack_speed + aspd)/100)) * (self.targets -1)
			
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			if self.talent_dmg:
				atk_scale *= self.skill_params[2]
			aspd += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
			extradmg = np.fmax(final_atk * extra_scale * (1-res/100), final_atk * extra_scale * 0.05)
			
			dps = hitdmg/(self.atk_interval/((self.attack_speed + aspd)/100))
			if self.module == 3:
				ele_gauge = 1000 if self.module_dmg else 2000
				eledps = dps * 0.08
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)/(1+self.buff_fragile)
				dps += eledmg * final_atk /(self.atk_interval/((self.attack_speed + aspd)/100)) * 15/(fallouttime + 15)
			if self.targets == 1:
				dps += bonusdmg/(self.atk_interval/((self.attack_speed + aspd)/100))
			if self.targets > 1 and self.module == 2:
				dps += extradmg/(self.atk_interval/((self.attack_speed + aspd)/100)) * (self.targets -1)
		return dps

class Ela(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ela",pp,[1,2,3],[3],3,1,3)
		self.try_kwargs(3,["mine","minedebuff","debuff","grzmod","nomines","nomine","mines"],**kwargs)
		if self.talent2_dmg: self.name += " MineDebuff"
		else: self.name += " w/o mines"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
			
	def skill_dps(self, defense, res):
		if self.elite > 1:
			if self.talent2_params[0] > 1:
				cdmg = self.talent2_params[0]
				crate = self.talent2_params[1]
			else:
				cdmg = self.talent2_params[1]
				crate = self.talent2_params[0]
			if self.talent2_dmg:
				crate = 1.0
		else:
			crate = 0
			cdmg = 1

		if self.skill < 2:
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
			fragile = self.skill_params[3]
			if not self.talent2_dmg: fragile = 0
			fragile = max(fragile, self.buff_fragile)
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[5]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1+fragile)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * (1+fragile)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/0.5 * self.attack_speed/100 /(1+self.buff_fragile)
			
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * 40 * (0.5/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Entelechia(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Entelechia",pp,[1,2,3],[1,2],3,1,1)
		if self.skill == 2 and self.skill_dmg: self.name += " overlapp"
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.module == 2 and self.module_dmg: self.name += " vs2+"
	
	def skill_dps(self, defense, res):
		arts_damage = self.talent1_params[2] if self.module == 2 and self.module_lvl > 1 else self.talent1_params[3]
		arts_dps = np.fmax(arts_damage * (1-res/100), self.talent1_params[3] * 0.05) * self.targets if self.elite > 0 else 0
		aspd = 12 if self.module == 2 and self.module_dmg else 0

		if self.skill < 2:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1) if self.skill == 1 else hitdmg
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1  + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps = 2 * hitdmg
			if self.skill_dmg: dps *= 2
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			aspd += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * self.targets
			hitdmg_candle = np.fmax(final_atk - defense, final_atk * 0.35) * min(self.targets, 3)
			dps = (hitdmg+hitdmg_candle)/self.atk_interval * (self.attack_speed + aspd)/100
			
		return dps + arts_dps

class Erato(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Erato",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg and self.elite > 0: self.name += " vsSleep"
		if not self.talent_dmg and self.elite > 0 and self.skill == 1: self.name += " selfAppliedSleep"
		if self.module == 1 and self.module_dmg: self.name += " vsHeavy"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		newdef = defense * (1 - self.talent1_params[0]) if self.talent_dmg or self.skill == 1 else defense
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmg_base = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.talent_dmg: hitdmg_base = hitdmg
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)
			if self.skill == 0: skilldmg = hitdmg
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = int(sp_cost / atkcycle)
			hits_on_sleep = min(int(5 / atkcycle), atks_per_skillactivation)			
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + hits_on_sleep * hitdmg + (atks_per_skillactivation-hits_on_sleep) * hitdmg_base) / (atks_per_skillactivation +1)
			dps = avghit/self.atk_interval*self.attack_speed/100

		if self.skill == 2:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		return dps

class Estelle(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Estelle",pp,[1,2],[2],2,6,2)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(1,self.skill)) + self.buff_atk_flat
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
		if self.skill in [0,2]:
			final_atk = self.atk * (1 + self.skill_params[0] * self.skill/2 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100 * self.targets
		return dps

class Eunectes(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Eunectes",pp,[1,2,3],[1,2,3],3,1,1)
		if not self.talent_dmg and self.elite > 0: self.name += " <50%hp"
		if self.module_dmg and self.module == 2: self.name += " WhileBlocking"

	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[2] if self.talent_dmg and self.elite > 0 else 1
		atkbuff = 0.15 if self.module_dmg and self.module == 2 else 0
		final_atk = self.atk *(1+ self.buff_atk + atkbuff + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
		atk_interval = 2 if self.skill == 2 else self.atk_interval
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/atk_interval * self.attack_speed/100
		block = 3 if self.skill == 3 else 1
		if self.module == 3 and self.skill > 0:
			dps *= min(self.targets, block + (self.module_lvl - 1))
			dps *= 0.8 + 0.2 * self.module_lvl
		return dps

class ExecutorAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ExecutorAlter",pp,[1,2,3],[1,2],3,1,1)
		self.ammo = 4 + 4 * self.skill
		if self.elite > 0 and self.skill != 1:
			if self.talent2_dmg and self.elite == 2: self.ammo += 4
			if not self.talent_dmg:
				self.name += " NoAmmoUsed"
				self.ammo = 1
			else:
				self.name += f" {self.ammo}AmmoUsed"
		if self.skill == 3: self.name += f" {self.ammo}stacks"	
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.skill == 3:
			extra = 0.04 * self.module_lvl if self.module == 2 and self.module_lvl > 1 else 0
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] + self.ammo * self.skill_params[1] + extra) + self.buff_atk_flat
			dmg = final_atk * self.skill_params[3] * (1 + self.buff_fragile)
			self.name += f" finalHit:{int(dmg)}"
		if self.module == 2 and self.module_dmg: self.name += " vs2+"

	def skill_dps(self, defense, res):
		crate = self.talent1_params[0] + self.talent1_params[1] * self.ammo if self.elite > 0 and self.skill != 0 else 0
		try: critdefignore = self.talent1_params[2]
		except: critdefignore = 0
		crate = min(crate, 1)
		aspd = 12 if self.module == 2 and self.module_dmg else 0
		modatkbuff = 0.04 * self.module_lvl if self.module == 2 and self.module_lvl > 1 else 0

		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		if self.skill < 2:
			defignore = self.skill_params[1] if self.skill == 1 else 0
			newdef = np.fmax(0, defense - defignore)
			critdef =np.fmax(0, defense - defignore - critdefignore)
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill * modatkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - newdef, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		
		if self.skill == 2:
			critdef = np.fmax(0, defense - critdefignore)
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + modatkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - defense, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
		
		if self.skill == 3:
			atkbuff += self.ammo * self.skill_params[1]
			critdef = np.fmax(0, defense - critdefignore)
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + modatkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg =  np.fmax(final_atk - defense, final_atk * 0.05) + np.fmax(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/1.8 * (self.attack_speed+aspd)/100 * self.targets
		return dps
	
class Exusiai(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Exusiai",pp,[1,2,3],[1,2],3,1,2)
		if self.module_dmg and self.module == 1: self.name += " aerialTarget"
		if self.module_dmg and self.module == 2: self.name += " groundEnemies"
		if self.module == 2 and self.module_lvl > 1 and not self.talent_dmg: self.name += " w/o Defignore"
	
	def skill_dps(self, defense, res):
		atkbuff = min(self.talent2_params) #they changed the order in the module ffs
		aspd = self.talent1_params[0]
		if self.module == 2 and self.module_dmg: aspd += 8
		newdef = np.fmax(defense - self.talent1_params[1]*self.talent1_params[2],0) if self.module == 2 and self.module_lvl > 1 and self.talent_dmg else defense
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1+atkbuff+self.buff_atk) + self.buff_atk_flat
		skill_scale = self.skill_params[0] if self.skill > 0 else 1
		if self.skill < 2:
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk* atk_scale * skill_scale * 0.05) * 3
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			if self.skill == 0: avgphys = hitdmg
			dps = avgphys/(self.atk_interval/((self.attack_speed+aspd)/100))
		elif self.skill == 2:
			hitdmg = np.fmax(final_atk *atk_scale * skill_scale - newdef, final_atk* atk_scale* skill_scale * 0.05)
			dps = 4*hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		elif self.skill == 3:
			atk_interval = self.atk_interval + 2 * self.skill_params[2]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk* atk_scale* skill_scale * 0.05)
			dps = 5*hitdmg/(atk_interval/((self.attack_speed+aspd)/100))
		return dps

class ExusiaiAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ExusiaiAlter",pp,[1,2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.skill == 2 and self.skill_dmg: self.name += " +StolenAspd"
	
	def skill_dps(self, defense, res):
		atkbuff = 2 * self.talent2_params[0] if self.elite > 1 else 0
		explosion_prob = min(self.talent1_params[1:])
		explosion_scale = max(self.talent1_params)

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			explosionhit = np.fmax(final_atk * explosion_scale - defense, final_atk * explosion_scale * 0.05) * self.skill
			dps = (hitdmg + explosionhit * explosion_prob * self.targets) / self.atk_interval * (self.attack_speed) / 100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			aspd = 70 if self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			explosionhit = np.fmax(final_atk * explosion_scale - defense, final_atk * explosion_scale * 0.05)
			dps =  (hitdmg + explosionhit * explosion_prob * self.targets) / 0.6 * (self.attack_speed + aspd) / 100
		if self.skill == 3:
			atkbuff += self.skill_params[5]
			skill_scale = self.skill_params[3]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			explosionhit = np.fmax(final_atk * explosion_scale - defense, final_atk * explosion_scale * 0.05)
			dps =  5 * (hitdmg + explosionhit * explosion_prob * self.targets) / self.atk_interval * (self.attack_speed) / 100
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 1:
			return(self.skill_dps(defense,res) * 8 * (self.atk_interval/(self.attack_speed/100)))
		elif self.skill == 2:
			aspd = 70 if self.skill_dmg else 0
			ammo = 40 if self.skill_dmg else 35
			return(self.skill_dps(defense,res) * ammo * (0.6/((self.attack_speed+aspd)/100)))
		elif self.skill == 3:
			return(self.skill_dps(defense,res) * 10 * (self.atk_interval/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))
		
class Eyjafjalla(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Eyjafjalla",pp,[1,2,3],[1,2],3,1,1)
		if self.skill_dmg:
			if self.skill == 1: self.name += " 2ndSkilluse"
			if self.skill == 2: self.name += " permaResshred"
		if not self.skill_dmg and self.skill == 2: self.name += " minResshred"
		if self.module == 2 and self.module_lvl == 3 and not self.talent_dmg: self.name += " minAspd+"
		if self.skill == 2 and self.module == 2 and self.module_dmg: self.name += " vsElite"
		if self.targets > 1 and self.skill > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.elite > 0 else 0
		resignore = 10 if self.module == 1 else 0
		newres = np.fmax(0, res - resignore)
		aspd = 0 
		if self.module == 2 and self.module_lvl == 3:
			if self.talent_dmg: aspd = 16
			else: aspd = 6

		if self.skill < 2:
			aspd += self.skill_params[0] if self.skill == 1 else 0
			if self.skill_dmg and self.skill == 1: atkbuff += self.skill_params[2]
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
			extra_boost = 1/(self.atk_interval)*(self.attack_speed+aspd)/100 if self.module == 2 and self.module_dmg else 0
			sp_cost = self.skill_cost/(1+self.sp_boost + extra_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg + (self.targets - 1) * aoeskilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[3] > 1:
					avghit = (skilldmg + (self.targets - 1) * aoeskilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + (self.targets - 1) * aoeskilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)								
			dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100
			
		if self.skill == 3:
			self.atk_interval = 0.5
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			maxtargets = self.skill_params[2]
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100 * min(self.targets, maxtargets)
			 
		return dps

class FangAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("FangAlter",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		if self.skill == 1:
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhit = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * 2
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skillhit
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avghit = (skillhit + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skillhit + int(atks_per_skillactivation ) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill in [0,2]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill/2) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,(1+self.skill/2))
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
		if self.skill in [0,2]:
			aspd += self.skill_params[0] * self.skill/2
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

		if self.skill < 2:
			atkbuff += self.skill_params[0] * self.skill
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

class Figurino(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Figurino",pp,[1,2],[1],1,1,1) #available skills, available modules, default skill, def pot, def mod
		if not self.talent_dmg and self.elite > 0: self.name += " blocking"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent1_params[0] if self.elite > 0 and self.talent_dmg else 1
		if self.skill < 1:
			atkbuff = self.skill_params[0] * self.skill
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg_scale
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * dmg_scale
			dps = hitdmg * min(self.targets, self.skill_params[1])
		return dps

class Firewhistle(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Firewhistle",pp,[1,2],[1],2,1,1)
		if not self.talent_dmg and self.elite > 0: self.name += " meelee"
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.talent_dmg else 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		if self.skill < 2:
			skill_scale = self.skill_params[2]
			fire_scale = self.skill_params[1] * self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgskill = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * fire_scale * (1-res/100), final_atk * 0.05)
			avgdmg = 3/4 * self.targets * hitdmg + 1/4 * hitdmgskill * self.targets + hitdmgarts / 4
			if self.skill == 0: avgdmg = hitdmg
			dps = avgdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 + hitdmgarts
			dps = dps * self.targets
		return dps

class Flamebringer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Flamebringer",pp,[1,2],[2],2,6,2)
		if self.module_dmg and self.module == 2: self.name += " afterRevive"

	def skill_dps(self, defense, res):
		aspd = 30 if self.module == 2 and self.module_dmg else 0
		if self.skill < 2:
			skill_scale = self.skill_params[0]	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			if self.skill == 0: avgphys = hitdmg
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			aspd += self.skill_params[1]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Flametail(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Flametail",pp,[1,3],[2,1],3,1,1)
		if self.module_dmg and self.module == 1: self.name += " blocking"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		cdmg = 1
		if self.module == 1 and self.module_lvl > 1: cdmg = 1.2 if self.module_lvl == 3 else 1.15
		critrate = 0
		atk_interval = 1.05 * 0.7 if self.skill == 3 else self.atk_interval
		dodge = self.talent2_params[0] if self.elite == 2 else 0
		if self.skill == 3:
			dodge = 1-((1-dodge)*(1-self.skill_params[2]))
		if self.hits > 0:
			dodgerate = dodge * self.hits
			atkrate = 1/atk_interval * self.attack_speed/100
			critrate = min(1, dodgerate/atkrate)
			
		if self.skill < 2:
			final_atk = self.atk * (1+ self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * 2 * min(2, self.targets)
			avghit = critrate * critdmg + (1 - critrate) * hitdmg
			dps = avghit/atk_interval * self.attack_speed/100
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+ self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * 2 * min(3, self.targets)
			avghit = critrate * critdmg + (1 - critrate) * hitdmg
			dps = avghit/atk_interval * self.attack_speed/100
		return dps

class Flint(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Flint",pp,[1,2],[1],2,1,1)
		if self.skill == 1 and not self.talent_dmg: self.name += " blocking"
		if self.module == 1 and self.module_dmg: self.name += " >50%Hp"

	def skill_dps(self, defense, res):
		dmgscale = 1 if self.skill == 1 and not self.talent_dmg else self.talent1_params[0]
		aspd = 10 if self.module == 1 and self.module_dmg else 0
		
		if self.skill < 2:
			skill_scale = self.skill_params[0]	
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			if self.skill == 0: avgphys = hitdmg
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
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets
		else: return 0 * defense
		return dps

class Franka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Franka",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module_dmg and self.module == 1 else 1
		crate = self.talent1_params[0] if self.elite > 0 else 0
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
		aspd = self.skill_params[1] if self.skill == 1 else 0
		crate *= 2.5 if self.skill == 2 else 1
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk *atk_scale * 0.05)
		critdmg = final_atk * atk_scale
		avghit = crate * critdmg + (1-crate) * hitdmg	
		dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Frost(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Frost",pp,[1,2],[2],2,1,2)
		if not self.trait_dmg or self.skill == 0: self.name += " noMines"   ##### keep the ones that apply
		else:
			if not self.talent_dmg: self.name += " 1MinePerSPcost"
			else: self.name += " 1MinePer5s"
			if self.skill == 2 and self.skill_dmg: self.name += " MineInRange"
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		newdef = np.fmax(0, defense - 40 * self.module_lvl) if self.module == 2 and self.module_lvl > 1 else defense
		hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.trait_dmg and self.skill > 0:
			critdmg = 1.2 if self.module == 2 else 1
			mine_scale = self.skill_params[1] if self.skill == 1 else self.skill_params[4]
			hitdmg_mine = np.fmax(final_atk * mine_scale - newdef, final_atk * mine_scale * 0.05) * critdmg
			if self.skill == 2 and self.skill_dmg:
				hitdmg_mine += np.fmax(final_atk * self.skill_params[1] - newdef, final_atk * self.skill_params[1] * 0.05) * 3
			hitrate = 5 if self.talent_dmg else max(5, self.skill_cost/(1+self.sp_boost))
			dps += hitdmg_mine/hitrate
		return dps

class Frostleaf(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Frostleaf",pp,[1,2],[1],1,6,1) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " rangedAtk"
	
	def skill_dps(self, defense, res):
		atk_scale = 0.8 if not self.trait_dmg else 1
		atk_interval = self.atk_interval if self.elite < 2 else self.atk_interval + 0.15
		extra_arts_scale = 0.1 if self.module == 1 else 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		hitdmgarts = np.fmax(final_atk * extra_arts_scale * (1-res/100), final_atk * extra_arts_scale * 0.05)

		if self.skill == 1:
			skill_scale = self.skill_params[2]
			skilldmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)	
			dps = (avghit+hitdmgarts)/atk_interval * self.attack_speed/100
		if self.skill in [0,2]:
			aspd = self.skill_params[1] * self.skill/2
			dps = (hitdmg+hitdmgarts) / atk_interval * (self.attack_speed + aspd) / 100
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("GavialAlter",pp,[1,2,3],[1,2],3,1,1)
		block = 5 if self.skill == 3 else 3
		if self.elite < 2: block = 2
		if self.talent_dmg and self.elite > 0: self.name += f""" {min(block,self.targets)}talentStack{"s" if self.targets > 1 else ""}"""
		if self.module in [1,2] and self.module_dmg: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		block = 5 if self.skill == 3 else 3
		if self.elite < 2: block = 2
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		dmg = 0.95 + self.module_lvl * 0.05 if self.module == 2 else 1
		atkbuff = self.talent1_params[0]
		if self.talent_dmg and self.elite > 0: atkbuff += self.talent1_params[2] * min(self.targets,block)
		
		atkbuff += self.skill_params[0] * min(self.skill,1)
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		aspd = self.skill_params[1] if self.skill == 3 else 0
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval *(self.attack_speed+aspd)/100 * min(self.targets, block)
		return dps * dmg

class Gladiia(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Gladiia",pp,[1,2,3],[1,2],2,6,1)
		if self.elite == 2:
			if not self.talent2_dmg: self.name += " vsHeavy"
			else: self.name += " vsLight"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = min(self.talent2_params) if self.elite == 2 and self.talent2_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill < 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg if self.skill == 1 else hitdmg
			if atks_per_skillactivation > 1 and self.skill == 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)			
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[2]
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/2.7 * self.attack_speed/100 * min(self.targets,2)
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/1.5 * self.targets
		return dps

class Gnosis(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Gnosis",pp,[1,3],[1,2],3,1,1)
		if self.skill == 3:
			if self.skill_dmg: self.name += " vsFrozen"
			else: self.name += " vsNonFrozen"
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			nukedmg = final_atk * self.skill_params[0] * max(1+self.buff_fragile, max(self.talent1_params))
			self.name += f" Nukedmg:{int(nukedmg)}"
		if self.module == 2 and self.skill == 1:
			if self.module_dmg: self.name += "vsElite"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		coldfragile = 0.5 * (max(self.talent1_params) - 1) if self.elite > 0 else 0
		frozenfragile = 2 * coldfragile
		coldfragile = max(coldfragile, self.buff_fragile)
		frozenfragile = max(frozenfragile, self.buff_fragile)
		frozenres = np.fmax(0, res - 15)
		atkbuff = 0.05 * self.module_lvl if self.module == 2 and self.module_lvl > 1 else 0
		extra_sp = 0.25 if self.module == 2 and self.skill == 1 and self.module_dmg else 0
		####the actual skills
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+ self.sp_boost + extra_sp) + 1.2 #sp lockout
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)*(1+coldfragile)/(1+self.buff_fragile)
			skilldmg1 = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)*(1+coldfragile)/(1+self.buff_fragile)
			skilldmg2 = np.fmax(final_atk * skill_scale * (1-frozenres/100), final_atk * skill_scale * 0.05)*(1+frozenfragile)/(1+self.buff_fragile)
			skilldmg = skilldmg1 + skilldmg2
			if self.skill == 0: skilldmg = hitdmg
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval*(self.attack_speed)/100
		
		if self.skill == 3:
			aspd = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)*(1+coldfragile)/(1+self.buff_fragile)
			if self.skill_dmg: hitdmg = np.fmax(final_atk * (1-frozenres/100), final_atk * 0.05)*(1+frozenfragile)/(1+self.buff_fragile)
			dps = hitdmg/(self.atk_interval/((self.attack_speed + aspd)/100)) * min(2, self.targets)
			
		return dps

class Goldenglow(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Goldenglow",pp,[1,2,3],[],3,1,1)
		if not self.trait_dmg: self.name += " minDroneDmg"
		if self.targets > 1 and self.elite > 0: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		newres = np.fmax(res-self.talent2_params[0],0)
		drone_dmg = 1.2 if self.module == 2 else 1.1
		drone_explosion = self.talent1_params[1] if self.elite > 0 else 0
		explosion_prob = 0.1 if self.elite > 0 else 0
		aspd = 0
		drones = 2
		if not self.trait_dmg:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		atkbuff = self.skill_params[0] * min(self.skill,1)
		if self.skill == 1:
			aspd += self.skill_params[1]
		if self.skill == 3:
			drones = 3
		final_atk = self.atk * (1+atkbuff+self.buff_atk) + self.buff_atk_flat
		drone_atk = drone_dmg * final_atk
		drone_explosion = final_atk * drone_explosion * self.targets
		dmgperinterval = final_atk*(3-drones) + drones * drone_atk * (1-explosion_prob) + drones * drone_explosion * explosion_prob
		if self.skill == 0: dmgperinterval = final_atk + drone_atk
		hitdmgarts = np.fmax(dmgperinterval *(1-newres/100), dmgperinterval * 0.05)
		dps = hitdmgarts/self.atk_interval*(self.attack_speed+aspd)/100
		return dps

class Gracebearer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Gracebearer",pp,[1,2],[],1,1,0) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg and self.elite > 0: self.name += " +talent"
		if self.skill == 1:
			if self.skill_dmg:
				self.name += " avgNervous"
				if not self.trait_dmg: self.name += "(vsBoss)"
			else: self.name += " noNervous"
		if self.skill == 2 and self.skill_dmg: self.name += " vsFallout"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		if self.elite > 0:
			atkbuff = self.talent1_params[0] + self.talent1_params[1] if self.talent_dmg else self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		atk_scale = self.skill_params[0] if self.skill == 1 else 1
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 1:
			dps *= 2
			if self.skill_dmg:
				ele_gauge = 1000 if self.trait_dmg else 2000
				time_to_fallout = ele_gauge/(0.1 * dps)
				dps += 6000/(10 + time_to_fallout)
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) if not self.skill_dmg else final_atk * skill_scale
			dps += 3 * skilldmg/((self.skill_cost + 1.2)/(1+self.sp_boost)) * min(self.targets, self.skill_params[1])
		return dps

class Grani(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Grani",pp,[1,2],[1],2,6,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		targets = 2 if self.skill == 2 else 1
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,targets)
		return dps

class GreyThroat(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("GreyThroat",pp,[1,2],[2],2,1,2)
		if self.module_dmg and self.module == 2: self.name += " GroundTargets"

	def skill_dps(self, defense, res):
		aspd = 8 if self.module == 2 and self.module_dmg else 0
		if self.elite > 0: aspd += 6
		crate = self.talent1_params[1] if self.elite > 0 else 0
		cdmg = 1.5
			
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * 2
			skillcrit = np.fmax(final_atk * skill_scale * cdmg - defense, final_atk * skill_scale * cdmg * 0.05) * 2
			avgnorm = crate * critdmg + (1-crate) * hitdmg
			avgskill = crate * skillcrit + (1-crate) * skilldmg

			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = avgskill
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avghit = (avgskill + (atks_per_skillactivation - 1) * avgnorm) / atks_per_skillactivation
				else:
					avghit = (avgskill + int(atks_per_skillactivation) * avgnorm) / (int(atks_per_skillactivation) + 1)					
			dps = avghit/self.atk_interval * (self.attack_speed+aspd)/100
			
		if self.skill in [0,2]:
			atkbuff = self.skill_params[0] * self.skill/2
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk  * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk  * cdmg * 0.05)
			avgnorm = crate * critdmg + (1-crate) * hitdmg
			dps = (1 + self.skill) * avgnorm/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class GreyyAlter(Operator):#TODO: proper dmg bonus uprate for module (how often is slow active)
	def __init__(self, pp, *args, **kwargs):
		super().__init__("GreyyAlter",pp,[1,2],[1],1,1,1) #available skills, available modules, default skill, def pot, def mod
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		bonushits = 2 if self.module == 1 else 1
		dmg = 1 + 0.05 * self.module_lvl if self.module == 1 and self.module_lvl > 1 else 1
		if self.skill < 2:
			atkbuff = self.skill_params[0] * self.skill
			aspd = self.skill_params[1] * self.skill
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg
			bonusdmg =  np.fmax(final_atk * 0.5 - defense, final_atk * 0.5 * 0.05) * dmg
			dps = (hitdmg + bonusdmg * bonushits) / self.atk_interval * (self.attack_speed + aspd) / 100 * self.targets
		
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg
			bonusdmg = np.fmax(final_atk * 0.5 - defense, final_atk * 0.5 * 0.05) * dmg
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg
			dps = (hitdmg + bonusdmg * bonushits) / self.atk_interval * (self.attack_speed) / 100 * self.targets
			dps += hitdmgarts / 1.5 * self.targets
		return dps

class Hadiya(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Hadiya",pp,[1,2],[],2,1,0) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 0 and self.talent_dmg: self.name += " maxStacks"
		if self.skill == 1 and not self.skill_dmg: self.name += " noDP"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] * self.talent1_params[1] if self.elite > 0 and self.talent_dmg else 0
		if self.skill < 2:
			if self.skill == 1 and self.skill_dmg: atkbuff += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100 * min(self.targets, self.skill_params[1])
		return dps

class Harmonie(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Harmonie",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 0 and self.talent_dmg or self.skill == 2: self.name += " vsBlocked"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.elite > 0 and self.talent_dmg or self.skill == 2 else 1
		if self.skill < 2:
			atk_interval = self.atk_interval/5 if self.skill == 1 else self.atk_interval
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg / atk_interval * self.attack_speed / 100
		if self.skill == 2:
			atk_interval = self.atk_interval * self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk  * atk_scale * 0.05)
			extra_dps = np.fmax(self.skill_params[0] * (1-res/100), self.skill_params[0] * 0.05) * self.targets
			dps = hitdmg / atk_interval * self.attack_speed / 100 + extra_dps
		return dps

class Haze(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Haze",pp,[1,2],[1],2,6,1)
	
	def skill_dps(self, defense, res):
		resignore = 10 if self.module == 1 else 0
		newres = np.fmax(0, res-resignore) * (1 + self.talent1_params[1])
		atkbuff = self.skill_params[0] * self.skill if self.skill < 2 else self.skill_params[1]
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		return dps
	
class Hellagur(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Hellagur",pp,[1,2,3],[1,2],3,1,1)
		if self.talent_dmg: self.name += " lowHP"
		else: self.name += " fullHP"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		aspd = max(self.talent1_params) if self.talent_dmg else 0
		atkbuff = self.skill_params[0] if self.skill > 1 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * 2
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill in [0,2]:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1 + self.skill/2)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 3:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * min(self.targets, 3)
		return dps

class Hibiscus(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("HibiscusAlter",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		dmg = self.talent1_params[1] if self.elite > 0 else 1
		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
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

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1		
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
		super().__init__("Hoederer",pp,[1,2,3],[1,2],3,1,1)
		if self.skill == 2 and self.skill_dmg: self.talent_dmg = True
		if self.talent_dmg and self.elite > 0: self.name += " vsStun/Bind"
		elif self.skill == 3 and self.skill_dmg: self.name += " vsSelfAppliedStun"
		if self.skill == 2 and not self.skill_dmg: " defaultState"
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.module == 2 and self.module_dmg: self.name += " vsBlocked"

	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 2 and self.module_dmg else 1
		if self.elite > 0:
			atk_scale *= max(self.talent1_params) if self.talent_dmg else min(self.talent1_params)
		dmg_bonus = 1
		if self.module == 1:
			if self.module_lvl == 2: dmg_bonus = 1.06
			if self.module_lvl == 3: dmg_bonus = 1.1
			
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Hoolheyak",pp,[1,2,3],[1,2,3],3,1,1)
		if self.talent_dmg: self.name += " vsAerial"
		if self.skill == 3:
			if self.skill_dmg: self.name += " maxRange"
			else: self.name += " minRange"
		if self.module == 2 and self.module_lvl > 1 and self.talent2_dmg: self.name += " vsLowHp"
		if self.skill == 1 and self.module == 2 and self.module_dmg: self.name += " vsElite"
		if self.targets > 1 and not self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		newres = np.fmax(res-10,0) if self.module in [1,3] else res
		dmg_scale = 1
		if self.module == 2 and self.talent2_dmg:
			dmg_scale += 0.1 * (self.module_lvl -1)
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2 #sp lockout
			if self.module == 2 and self.module_dmg: sp_cost = self.skill_cost/(1 + self.sp_boost + 1/self.atk_interval*self.attack_speed/100) + 1.2 #sp lockout
			hitdmgarts = np.fmax(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05) * dmg_scale
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg * min(2, self.targets)
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg * min(2, self.targets) + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation						
				else:
					avghit = (skilldmg * min(2, self.targets) + int(atks_per_skillactivation) * hitdmgarts) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval * self.attack_speed/100
			
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = 9 * hitdmgarts/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			skill_scale = self.skill_params[1] if self.skill_dmg else self.skill_params[0]
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = hitdmgarts/3 * self.attack_speed/100 * min(self.targets, 3)
		return dps
	
class Horn(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Horn",pp,[1,2,3],[1,2],3,1,1)
		self.try_kwargs(3,["afterrevive","revive","after","norevive"],**kwargs)
		self.try_kwargs(4,["overdrive","nooverdrive"],**kwargs)
		self.try_kwargs(5,["blocked","unblocked"],**kwargs)
		if self.talent2_dmg and self.elite == 2: self.name += " afterRevive"
		if self.skill_dmg and not self.skill == 1: self.name += " overdrive"
		elif self.skill > 1: self.name += " no overdrive"
		if self.module_dmg and self.module == 1: self.name += " blockedTarget"
		if self.module_dmg and self.module == 2: self.name += " rangedAtk"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
			
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent1_params[0]
		aspd = self.talent2_params[2] if self.talent2_dmg else 0
		if self.module == 2 and self.module_dmg: aspd += 10
		if self.module == 2 and self.module_lvl > 1:
			if self.module_lvl == 2: aspd += 5
			if self.module_lvl == 3: aspd += 8

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Hoshiguma",pp,[1,2,3],[2,1],2,1,2)
		if self.module == 2 and self.module_dmg and self.module_lvl > 1: self.name += " afterDodge"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets"
		try: self.hits = kwargs['hits']
		except KeyError: self.hits = 0
		if self.hits > 0 and self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1] if self.module == 2 and self.module_lvl > 1 and self.module_dmg else 0
		targets = self.targets if self.skill == 3 else 1
		if self.skill == 3: atkbuff += self.skill_params[0]
		final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * targets
		if self.skill == 2 and self.hits > 0:
			skill_scale = self.skill_params[0]
			reflectdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps += reflectdmg * self.hits
		return dps

class HoshigumaAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("HoshigumaAlter",pp,[1,3],[1],2,1,1)
		if self.talent2_dmg and self.talent_dmg and self.elite == 2: self.name += " maxTenacity"
		if self.skill == 3 and self.skill_dmg: self.name += " lastStand"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets"
		try: self.hits = kwargs['hits']
		except KeyError: self.hits = 0
		if self.hits > 0 and self.skill == 1: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		extra_scale = 0.1 if self.module == 1 else 0
		atkbuff = self.talent2_params[2] if self.talent2_dmg and self.talent_dmg and self.elite == 2 else 0
		if self.module == 1 and self.module_lvl > 1 and self.talent2_dmg and self.talent_dmg: atkbuff += 0.05 * self.module_lvl
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1 + extra_scale) * (1-res/100), final_atk * (1 + extra_scale) * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			skill_scale = self.skill_params[2] + extra_scale
			reflectdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps += reflectdmg * self.hits
		
		if self.skill == 3:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[1]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1 + extra_scale) * (1-res/100), final_atk * (1 + extra_scale) * 0.05) 
			hits = 4 if self.skill_dmg else 3
			dps = hits * hitdmg/self.atk_interval * self.attack_speed/100 * min(self.skill_params[2], self.targets)

		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3 and self.skill_dmg: self.skill_duration = 11
		return super().total_dmg(defense, res)

class Humus(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Humus",pp,[1,2],[1],2,6,1)
		if self.skill == 2:
			if self.skill_dmg: self.name += " >80%Hp"
			else: self.name += " <50%Hp"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1	
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Iana",pp,[1,2],[1],2,1,1)
		if self.skill == 1:
			atkbuff = 0.15 if self.module == 1 else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			fragile = max(self.talent1_params[2] - 1, self.buff_fragile)
			nukedmg = final_atk * self.skill_params[0] * (1+fragile)
			self.name += f" InitialDmg:{int(nukedmg)}"
			
	def skill_dps(self, defense, res):
		atkbuff = 0.15 if self.module == 1 else 0
		fragile = self.talent1_params[2] - 1
		fragile = max(fragile, self.buff_fragile)
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * (1+fragile)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 /(1+self.buff_fragile)
		return dps

class Ifrit(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ifrit",pp,[1,2,3],[1,3],3,1,1)
		if self.module_dmg and self.module == 1: self.name += " maxRange"
		if self.module == 3:
			if self.talent_dmg: 
				self.name += " withAvgBurn"
				if not self.module_dmg: " vsBoss"
			else: self.name += " noBurn"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		resshred = self.talent1_params[0]
		ele_gauge = 1000 if self.module_dmg else 2000
		burnres = np.fmax(0,res-20)
		
		recovery_interval = self.talent2_params[1]
		sp_recovered = self.talent2_params[0] if self.elite == 2 else 0
		if self.module == 1:
			if self.module_lvl == 2: sp_recovered = 3
			if self.module_lvl == 3: sp_recovered = 2 + 0.3 * 5
			
		####the actual skills
		if self.skill < 2:
			atkbuff = self.skill_params[1] if self.skill == 1 else 0
			aspd = self.skill_params[0] if self.skill == 1 else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			newres = res * (1+resshred)
			hitdmgarts = np.fmax(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
			if self.module == 3 and self.talent_dmg and self.module_lvl > 1:
				time_to_proc = ele_gauge * self.targets / (dps*0.08)
				newres2 = burnres * (1 + resshred)
				hitdmgarts = np.fmax(final_atk *(1-newres2/100), final_atk * 0.05)
				ele_hit = final_atk * (0.2*0.1*self.module_lvl)/(1+self.buff_fragile) if self.module_lvl > 1 else 0
				fallout_dps = (hitdmgarts + ele_hit)/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
				dps = (dps * time_to_proc + 10 * fallout_dps + 7000/(1+self.buff_fragile))/(time_to_proc+10)
		
		if self.skill == 2:
			sp_cost = self.skill_cost
			skill_scale = self.skill_params[0]
			burn_scale = 0.99
			newres = res * (1+resshred)
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			skilldmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05)
			burndmg = np.fmax(final_atk * burn_scale *(1-newres/100), final_atk * burn_scale * 0.05)
			sp_cost = sp_cost / (1+sp_recovered/recovery_interval + self.sp_boost) + 1.2 #talent bonus recovery + sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts + burndmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmgarts + burndmg + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation	
			dps = avghit/self.atk_interval * self.attack_speed/100 * self.targets
			
			if self.module == 3 and self.talent_dmg and self.module_lvl > 1:
				time_to_proc = ele_gauge * self.targets / (dps*0.08)
				newres2 = burnres * (1 + resshred)
				hitdmgarts = np.fmax(final_atk *(1-newres2/100), final_atk * 0.05)
				skilldmgarts = np.fmax(final_atk * skill_scale *(1-newres2/100), final_atk * skill_scale * 0.05)
				burndmg = np.fmax(final_atk * burn_scale * (1-newres2/100), final_atk * burn_scale * 0.05)
				ele_hit = final_atk * (0.2*0.1*self.module_lvl)/(1+self.buff_fragile) if self.module_lvl > 1 else 0
				avghit = skilldmgarts + burndmg + ele_hit
				if atks_per_skillactivation > 1:
					avghit = (skilldmgarts + burndmg + (atks_per_skillactivation - 1) * hitdmgarts + ele_hit) / atks_per_skillactivation	
				fallout_dps = (avghit + ele_hit)/self.atk_interval * self.attack_speed/100 * self.targets
				dps = (dps * time_to_proc + 10 * fallout_dps + 7000/(1+self.buff_fragile))/(time_to_proc+10)
				
		if self.skill == 3:
			atk_scale *= self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			flatshred = -self.skill_params[2]
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				res = res / self.shreds[0]
			newres = np.fmax(0, res-flatshred)
			newres = newres * (1+resshred)
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				newres *= self.shreds[2]
			hitdmgarts = np.fmax(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
			
			if self.module == 3 and self.talent_dmg and self.module_lvl > 1:
				time_to_proc = ele_gauge * self.targets / (dps*0.08)
				if self.shreds[2] < 1 and self.shreds[2] > 0:
					res = res / self.shreds[0]
				newres2 = np.fmax(0, res-flatshred-20)
				newres2 = newres2 * (1+resshred)
				if self.shreds[2] < 1 and self.shreds[2] > 0:
					newres2 *= self.shreds[2]
				hitdmgarts = np.fmax(final_atk *atk_scale *(1-newres2/100), final_atk * atk_scale * 0.05)
				ele_hit = final_atk * (0.2*0.1*self.module_lvl)/(1+self.buff_fragile) if self.module_lvl > 1 else 0
				fallout_dps = (hitdmgarts + ele_hit) * self.targets
				dps = (dps * time_to_proc + 10 * fallout_dps + 7000/(1+self.buff_fragile))/(time_to_proc+10)
		return dps

class Indra(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Indra",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " >50% HP"

	def skill_dps(self, defense, res):
		aspd = 10 if self.module_dmg and self.module == 1 else 0
		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			newdef = defense * (1 - self.skill_params[1]) 
			if self.skill == 1: final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skilldmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			dps = 0.2*(4*hitdmg + skilldmg)/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Ines(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ines",pp,[1,2,3],[2],2,1,2)
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
		if self.skill in [0,3]:
			atkbuff = self.skill_params[1] if self.skill == 3 else 0
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
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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

		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg1 = np.fmax(final_atk - newdef1, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk - newdef2, final_atk * 0.05)
			skill_dmg = np.fmax(final_atk * skill_scale - newdef2, final_atk * skill_scale * 0.05) * skill_dmg
			if self.skill == 0: skill_dmg = (hitdmg1+hitdmg2)/2
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
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		skilldmg = np.fmax(final_atk * self.skill_params[0] - defense, final_atk * self.skill_params[0] * 0.05)
		avgdmg = (hitdmg * self.skill_cost + skilldmg) / (self.skill_cost+1) if self.skill == 1 else hitdmg
		dps = avgdmg/self.atk_interval*(self.attack_speed+aspd)/100
		return dps

class Jaye(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Jaye",pp,[1,2],[1],2,6,1)
		self.try_kwargs(2,["infected","vsInfected","notinfected","noinfected"],**kwargs)
		if self.talent_dmg: self.name += " vsInfected"
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
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
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
			self.skill_duration = 1.8 * 20 / self.attack_speed * 100

	def skill_dps(self, defense, res):
		if self.skill < 2:
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[1] * self.skill) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			self.atk_interval = 0.3
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			final_atk = final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/ 1.8 * self.attack_speed/100
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

class Kafka(Operator):#TODO: dmg numbers in the label
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kafka",pp,[1,2],[2],2,1,2)
		if self.module_dmg and self.module == 2: self.name += " alone"
		if self.skill == 2: self.skill_duration = self.skill_params[1]

	def skill_dps(self, defense, res):
		if self.skill == 1: return res * 0
		atkbuff = 0.1 if self.module_dmg and self.module == 2 else 0
		if self.skill == 0:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		atkbuff += self.talent1_params[0]
		if self.skill == 2:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Kaltsit(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kaltsit",pp,[1,2,3],[1,2,3],3,1,2)
		if not self.talent_dmg and self.module == 2 and self.module_lvl > 1: self.name += " NotInHealRange"
		if self.skill == 3: self.name += " averaged"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
		if self.module in [2,3]:
			self.attack_speed -= 4 + self.module_lvl #because we want mon3trs attack speed

	def skill_dps(self, defense, res):
		aspd = 0
		if self.module == 2 and self.talent_dmg:
			if self.module_lvl == 2: aspd = 12
			if self.module_lvl == 3: aspd = 20
		atkbuff = 0.25 * (self.module_lvl - 1) if self.module == 3 else 0
			
		if self.skill < 2:
			final_atk = self.drone_atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.drone_atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.drone_atk * (1 + self.buff_atk + self.skill_params[1] + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.drone_atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,3)
		if self.skill == 3:
			final_atk = self.drone_atk * (1 + self.buff_atk + self.skill_params[0] * 0.5 + atkbuff) + self.buff_atk_flat
			dps = final_atk/self.drone_atk_interval * (self.attack_speed+aspd)/100 * np.fmax(-defense, 1)
		return dps

class Kazemaru(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kazemaru",pp,[1,2],[1],2,1,1)
		if self.skill == 2 and not self.skill_dmg: self.name += " w/o doll"
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat	
			damage = final_atk * self.talent1_params[0]* (1+self.buff_fragile)
			self.name += f" SummoningAoe:{int(damage)}"

	def skill_dps(self, defense, res):
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
		if self.skill < 2:
			skill_scale = self.skill_params[0]		
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale * (1 - res/100), final_atk * skill_scale * 0.05)
			if self.skill == 0: skillhitdmg = hitdmg
			sp_cost = self.skill_cost
			avghit = ((sp_cost+1) * hitdmg + skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * skill_scale * (1- res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg * self.targets
		return dps

class Kjera(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kjera",pp,[1,2],[2],2,6,2)
		if not self.talent_dmg and self.elite > 0: self.name += " noGroundTiles"
		if not self.trait_dmg: self.name += " minDroneDmg"
		self.freezeRate = 0 #ill just assume the freezing hit already benefits from the resshred
		if self.skill == 2:
			baseChance = self.skill_params[2]
			hitchances = [0,0,0]
			atkInterval = self.atk_interval / self.attack_speed * 100
			countingCycles = int(2.5 / atkInterval)
			for j in range(3): #TL;DR what is the chance of at least 2 hits of the past counting ones to have applied cold, calced for all 3 individual hits per attack, then averaged
				totalHits = 3 * countingCycles + j + 1
				for successes in range (2,totalHits+1):
					hitchances[j] += (1-baseChance)**(totalHits-successes) * baseChance**successes * math.comb(totalHits, successes)
			self.freezeRate = sum(hitchances)/3
	
	def skill_dps(self, defense, res):
		drone_dmg = 1.2 if self.module == 2 else 1.1
		if not self.trait_dmg: drone_dmg = 0.2
		atkbuff = 0
		if self.elite > 0: atkbuff += self.talent1_params[2] if self.talent_dmg else self.talent1_params[0]		
		
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0] * min(self.skill, 1)) + self.buff_atk_flat
		drone_atk = drone_dmg * final_atk
		dmgperinterval = final_atk + drone_atk * self.skill
		if self.skill < 2:
			hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			res2 = np.fmax(0,res-15)
			hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			hitdmgfreeze = np.fmax(dmgperinterval *(1-res2/100), dmgperinterval * 0.05)
			damage = hitdmgfreeze * self.freezeRate + hitdmgarts * (1 - self.freezeRate)
			dps = damage/self.atk_interval * self.attack_speed/100
		return dps
	
class Kroos(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Kroos",pp,[1],[],1,6,0)
		self.name = self.name.replace("S0","S1")
	
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
		hits = 4 if self.skill == 2 and self.skill_dmg else 1 + min(self.skill, 1)
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
		
		if self.skill < 2:
			atkbuff = self.skill_params[1] if self.skill_dmg and self.skill == 1 else 0
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

		if self.skill < 2:
			skill_scale = self.skill_params[0]		
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1) if self.skill == 1 else hitdmg
			dps = avgphys/self.atk_interval * (self.attack_speed+aspd)/100 * self.targets
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
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
		####the actual skills
		if self.skill < 2:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg) / self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg) / self.atk_interval * self.attack_speed/100 * min(2,self.targets)
		return dps*(1+fragile)/(1+self.buff_fragile)

class LapplandAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LapplandAlter",pp,[1,2,3],[1],3,1,1)
		if self.elite > 0 and not self.talent_dmg: self.name += " noTalentBuffs"
		if not self.trait_dmg: self.name += " minDroneDmg"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		drone_dmg = 1.1
		drones = 1
		if not self.trait_dmg:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		if self.talent_dmg and self.elite > 0:
			drone_dmg *= self.talent1_params[1]
			drones += 1
		try: aspd = self.talent2_params[1]
		except: aspd = 0
		atkbuff = self.skill_params[0] * min(self.skill,1)
		if self.skill == 1: drones += 1
		if self.skill == 2: drones += 3
		if self.skill == 3: drones += 2
		final_atk = self.atk * (1+atkbuff+self.buff_atk) + self.buff_atk_flat
		drone_atk = drone_dmg * final_atk
		dmgperinterval = final_atk + drones * drone_atk
		hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/self.atk_interval*(self.attack_speed+aspd)/100
		if self.skill == 3:
			dps += self.targets * final_atk * self.skill_params[4] * np.fmax((1-res/100),0.05)
		return dps

class Lava3star(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lava",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + self.skill_params[0] * self.skill) / 100 * self.targets
		return dps

class Lavaalt(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LavaAlter",pp,[1,2],[1],2,6,1)
		if self.skill_dmg and self.skill==2: self.name += " overlap"
		if self.skill_dmg and self.skill==1 and self.targets > 1: self.name += " overlap"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/self.atk_interval * self.attack_speed/100 * self.targets
			if self.skill_dmg and self.targets > 1 and self.skill == 1:
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lee",pp,[1,2,3],[1,2],3,1,1)
		if self.talent_dmg and self.elite > 0:
			if self.targets == 1: self.name += " blocking(doubled)"
			else: self.name += " blocking"
		if self.module == 2 and self.module_dmg: self.name += " 5modStacks"
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.skill == 2:
			skillscale = self.skill_params[0]
			maxscale = skillscale + self.skill_params[1] * self.skill_params[2]
			atkbuff = 0.2 if self.module == 2 and self.module_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			nukedmg = final_atk * skillscale * (1+self.buff_fragile)
			maxdmg = final_atk * (maxscale) * (1+self.buff_fragile)
			self.name += f" NukeDmg:{int(nukedmg)}-{int(maxdmg)}"

	def skill_dps(self, defense, res):
		aspd = self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 0
		if self.targets == 1 and self.talent_dmg: aspd *= 2
		atkbuff = 0.2 if self.module == 2 and self.module_dmg else 0
		if self.skill == 2: aspd += self.skill_params[5]
		else: atkbuff += self.skill_params[0] * min(self.skill,1)
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class LeiziAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("LeiziAlter",pp,[1,2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg and self.skill != 2: self.name += " minTrait"
		if self.skill == 1:
			if self.skill_dmg: self.name += " tripleHit"
			self.name += " totalDmg"
		if self.skill == 2 and self.skill_dmg: self.name += " maxStacks"
		if self.skill == 3:
			balls = 1 if self.skill_dmg else 0
			if self.module_dmg: balls += 1
			if self.talent2_dmg: balls += 1
			self.name += f" {balls}balls"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[2] if self.skill > 0 else 1
		lightning =  self.talent1_params[1]
		#initial hit of 100% atk as arts when activating skill
		atkbuff = 2
		if not self.trait_dmg:
			if self.skill == 3: atkbuff = 1.8
			if self.skill == 0: atkbuff = 0
			if self.skill == 1: atkbuff = 0.55

		if self.skill == 0:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			lightdmg = 0.1 * np.fmax(final_atk * lightning * atk_scale * (1-res/100), final_atk * lightning * atk_scale * 0.05)
			dps = lightdmg * self.targets

		if self.skill == 1:
			skill_scale =  self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			artsdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			if self.skill_dmg: hitdmg *= 3
			dps = hitdmg + artsdmg if self.elite == 2 else hitdmg
			dps *= self.targets

		if self.skill == 2:
			skill_scale = self.skill_params[0]
			targets = self.skill_params[1]
			if self.skill_dmg:
				atkbuff += 2.5
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			lightdmg = 0.1 * np.fmax(final_atk * lightning * atk_scale * (1-res/100), final_atk * lightning * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100 * min(self.targets, targets) + lightdmg * self.targets
		
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			arts_scale = self.skill_params[3]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			lightdmg = 0.1 * np.fmax(final_atk * lightning * atk_scale * (1-res/100), final_atk * lightning * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * arts_scale * atk_scale * (1-res/100), final_atk * arts_scale * atk_scale * 0.05)
			balls = 1 if self.skill_dmg else 0
			if self.module_dmg: balls += 1
			if self.talent2_dmg: balls += 1
			arts_dmg = hitdmgarts * 3 + balls * 4 * hitdmgarts

			dps = (hitdmg + arts_dmg * self.targets) / 2.9 * (self.attack_speed) / 100

		return dps

class Lemuen(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lemuen",pp,[1,2,3],[2],2,1,2) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2: self.talent_dmg = self.talent_dmg and self.skill_dmg
		if self.talent_dmg and self.elite > 0: self.name += " vsMarked"
		if not self.talent2_dmg and self.elite > 1: self.name += f" <{int(self.talent2_params[0])}s"
		if self.targets > 1 and self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.skill == 3: self.name += " totalDMG"
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent2_params[1] if self.talent2_dmg and self.elite > 1 else 0
		dmg = min(self.talent1_params) if self.talent_dmg and self.elite > 0 else 1
		
		if self.skill < 2:
			atk_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * min(self.targets, 1 + self.skill) * dmg
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		
		if self.skill == 2:
			aspd = self.skill_params[0]
			atkbuff += self.skill_params[1]
			atk_scale = self.skill_params[8]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			if self.talent_dmg: hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * dmg
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
			if self.talent_dmg:
				dps = hitdmg / self.skill_params[3]
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			ammo = 5 + self.talent2_params[2] if self.talent2_dmg else 5
			centralhit_dmg = np.fmax(final_atk * self.skill_params[4] - defense, final_atk * self.skill_params[4] * 0.05) * dmg
			outerhit_dmg = np.fmax(final_atk * self.skill_params[6] - defense, final_atk * self.skill_params[6] * 0.05) * dmg
			dps = ammo * centralhit_dmg * self.targets

		return dps
	
	def total_dmg(self, defense, res):
		extra_ammo = self.talent2_params[2] if self.elite > 1 and self.talent2_dmg else 0
		if self.skill == 1:
			return(self.skill_dps(defense,res) * (self.skill_params[1] + extra_ammo) * (self.atk_interval/(self.attack_speed/100)))
		elif self.skill == 2 and self.talent_dmg:
			return(self.skill_dps(defense,res) * (self.skill_params[2] + extra_ammo) * (self.skill_params[3]))
		else:
			return(super().total_dmg(defense,res))

class Lessing(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lessing",pp,[1,2,3],[1,2],2,6,1)

		if self.skill == 3 and self.module == 1:
			self.skill_dmg = self.skill_dmg and self.module_dmg
			self.module_dmg = self.skill_dmg
		if self.skill == 3 and self.skill_dmg: self.talent_dmg = False
		if not self.talent2_dmg and self.elite == 2: self.name += " w/o talent2"
		if self.module == 2 and self.module_lvl > 1 and not self.talent_dmg and not self.skill == 3: self.name += " vsBlocked"
		if self.module_dmg and self.module == 1 and not self.skill == 3: self.name += " vsBlocked"
		if self.module_dmg and self.module == 2: self.name += " afterRevive"
		elif self.skill == 3 and self.skill_dmg: self.name += " vsBlocked"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent2_params[0] if self.talent2_dmg else 0
		aspd = 30 if self.module == 2 and self.module_dmg else 0
		newdef = defense * (1 - 0.04 * self.module_lvl) if self.module == 2 and self.module_lvl > 1 and self.talent_dmg else defense

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale *skill_scale - newdef, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)	
			dps = avgphys/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + atkbuff + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps = 2 * hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 3:
			if self.skill_dmg: atk_scale *= self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps =  hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		return dps
	
class Leto(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Leto",pp,[1,2],[2],2,1,2)
		if not self.trait_dmg and not self.skill == 2: self.name += " rangedAtk"  
		if self.module == 2 and self.targets == 1 and self.module_dmg: self.name += " +12aspd(mod)"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atk_scale = 0.8 if self.skill < 2 and not self.trait_dmg else 1
		aspd = 12 if self.module == 2 and (self.targets > 1 or self.module_dmg) else 0
		aspd += self.talent1_params[0]
		final_atk = self.atk * (1 + self.skill_params[0] * min(self.skill,1) + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1: aspd += self.skill_params[1]
		hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2 and self.targets > 1: dps *= 2
		return dps

class Lin(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lin",pp,[1,2,3],[1,2],3,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets"
		if self.module == 2 and self.module_dmg: self.name += "  manyTargets"
	
	def skill_dps(self, defense, res):
		if self.skill == 0: return res * 0
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
		if self.module == 2 and self.module_dmg: dps *= 1.15
		return dps

class Ling(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ling",pp,[1,2,3],[2],3,1,2)
		if self.module == 2 and self.module_lvl ==3:
			if self.skill in [0,3]: self.drone_atk += 60
			if self.skill == 2: self.drone_atk += 35
			if self.skill == 1: self.drone_atk += 45
		if not self.trait_dmg: self.name += " noDragons"  
		elif not self.talent_dmg: self.name += " 1Dragon"
		else: self.name += " 2Dragons"
		if self.skill in [0,3] and self.trait_dmg:
			if self.skill_dmg: self.name += "(Chonker)"
			else: self.name += "(small)"			
		if not self.talent2_dmg and self.elite == 2: self.name += " noTalent2Stacks"
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets"
		if self.skill == 0: self.name = self.name.replace("S0","S0(S3)")			
	
	def skill_dps(self, defense, res):
		talentbuff = self.talent2_params[0] * self.talent2_params[2] if self.talent2_dmg else 0
		dragons = 2 if self.talent_dmg else 1
		if not self.trait_dmg: dragons = 0

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
		if self.skill in [0,3]:
			atkbuff = self.skill_params[0] * self.skill/3
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
	
	def avg_dps(self, defense, res):
		if self.skill == 3: return super().avg_dps(defense, res)
		else: return self.skill_dps(defense,res)

class Logos(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Logos",pp,[1,2,3],[3,2],3,1,3)
		if self.skill == 2 and self.skill_dmg: self.name += " after5sec"
		if self.module == 3 and self.talent_dmg: self.name += " withAvgNecrosis"
		elif self.module == 3: self.name += " noNecrosis"
		if self.module == 3 and self.talent_dmg and not self.module_dmg: self.name += " vsBoss"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets"
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			limit = final_atk *  self.skill_params[1]
			self.name += f" Death@{int(limit)}HP"
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
	
	def skill_dps(self, defense, res):
		bonuschance = self.talent1_params[0] if self.elite > 0 else 0
		if self.module == 3: bonuschance += 0.1 * (self.module_lvl - 1)
		bonusdmg = self.talent1_params[1]
		bonus_hitcount = 2 if self.module == 2 and self.module_lvl > 1 else 1
		falloutdmg = 0.2 * self.module_lvl /(1+self.buff_fragile) if self.module == 3 and self.module_lvl > 1 else 0
		newres = np.fmax(0,res-10) if self.elite == 2 else res
		if self.elite == 2:
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				res = res / self.shreds[2]
			newres = np.fmax(0, res	- 10)
			if self.shreds[2] < 1 and self.shreds[2] > 0:
				newres *= self.shreds[2]
		shreddmg = self.talent2_params[2] if self.elite == 2 else 0
		
		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance * bonus_hitcount
			dps = (hitdmg+bonusdmg)/self.atk_interval * self.attack_speed/100
			if self.module == 3 and self.talent_dmg:
				ele_gauge = 1000 if self.module_dmg else 2000
				eledps = dps * 0.08
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)/(1+self.buff_fragile)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg /self.atk_interval * self.attack_speed/100 * bonuschance * 15 / (fallouttime + 15)
		
		if self.skill == 2:
			scaling = self.skill_params[2]
			if self.skill_dmg: scaling *= 3
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * scaling * (1-newres/100), final_atk * scaling * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance * bonus_hitcount
			dps = (hitdmg+bonusdmg) * 2
			if self.module == 3 and self.talent_dmg:
				ele_gauge = 1000 if self.module_dmg else 2000
				eledps = dps * 0.08 
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15)/(1+self.buff_fragile)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg * 2 * bonuschance * 15 / (fallouttime + 15)
			
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (np.fmax(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + np.fmax(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance * bonus_hitcount
			dps = (hitdmg+bonusdmg)/self.atk_interval * self.attack_speed/100 * min(self.targets,self.skill_params[1])
			if self.module == 3 and self.talent_dmg:
				ele_gauge = 1000 if self.module_dmg else 2000
				eledps = dps * 0.08 / min(self.targets,self.skill_params[1])
				fallouttime = ele_gauge / eledps
				dps += 12000/(fallouttime + 15) * min(self.targets,self.skill_params[1]) /(1+self.buff_fragile)
				if self.module_lvl > 1:
					dps += final_atk * falloutdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,self.skill_params[1]) * bonuschance * 15 / (fallouttime + 15)
		return dps

class Lucilla(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lucilla", pp, [1,2],[1],2,1,1)
		if self.talent_dmg and self.elite > 0:
			self.name += " vsTrash"
			if self.skill == 2 and self.skill_dmg: self.name +="(maxMultiplier)"
		if self.targets > 1 and self.skill != 0: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		fragile = self.talent1_params[0] - 1 if self.elite > 0 and self.talent_dmg else 0
		if self.skill == 2 and self.skill_dmg: fragile *= self.skill_params[3]
		fragile = max(fragile, self.buff_fragile)
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * min(self.targets, self.skill_params[1])
			if self.skill == 0: skilldmg = hitdmg
			avghit = (hitdmg * self.skill_cost + skilldmg)/(self.skill_cost + 1)
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed/100 * min(self.targets, 2)
		return dps*(1+fragile)/(1+self.buff_fragile)

class Lunacub(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Lunacub",pp,[1,2],[2],2,1,2)
	
	def skill_dps(self, defense, res):
		atk_shorter = 0.15 if self.elite == 2 else 0
		if self.module == 2: atk_shorter += 0.05 * (self.module_lvl - 1)
		if self.skill == 0: atk_shorter = 0
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
		if self.skill == 0 and not self.trait_dmg: self.name += " rangedAtk"
		if self.module == 2 and self.targets == 1 and self.module_dmg: self.name += " +12aspd(mod)"
	
	def skill_dps(self, defense, res):
		dmg_scale = 1 + 0.04 * self.module_lvl if self.below50 else 1
		aspd = 12 if self.module == 2 and (self.module_dmg or self.targets > 1) else 0
		
		if self.skill == 0:
			atk_scale = 1 if self.trait_dmg else 0.8
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk * atk_scale * 0.05) * dmg_scale
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
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
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Magallan",pp,[1,2,3],[1,2],3,1,2)
		if not self.trait_dmg or self.skill == 1: self.name += " noDrones"
		elif not self.talent_dmg: self.name += " 1Drone"
		else: self.name += " 2Drones"
		if self.targets > 1 and self.trait_dmg and self.skill != 1: self.name += f" {self.targets}targets"
		if self.module == 2 and self.module_lvl == 3:
			if self.skill == 2: self.drone_atk += 40
			if self.skill in [0,3]: self.drone_atk += 50
		if self.skill == 0: self.name = self.name.replace("S0","S0(S3)")

	def skill_dps(self, defense, res):
		drones = 2 if self.talent_dmg else 1
		if not self.trait_dmg: drones = 0
		bonusaspd = 3 if self.module == 2 and self.module_lvl == 3 else 0

		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			final_drone = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
			
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = np.fmax(final_drone * (1-res/100), final_drone * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100 + hitdmgdrone/self.drone_atk_interval* (self.attack_speed+aspd+bonusaspd)/100 * drones * self.targets
		if self.skill in [0,3]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill/3) + self.buff_atk_flat
			final_drone = self.drone_atk * (1 + self.buff_atk + self.skill_params[0]*self.skill/3) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = np.fmax(final_drone - defense, final_drone * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 + hitdmgdrone/self.drone_atk_interval* (self.attack_speed+bonusaspd)/100 * drones * self.targets
		return dps

class Manticore(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Manticore",pp,[1,2],[1],2,1,1)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atk_interval = 5.2 if self.skill == 2 else self.atk_interval
		atkbuff_talent = self.talent1_params[1] if self.elite > 0 else 0
		if self.module == 1 and self.module_lvl > 1: atkbuff_talent += 0.05 * (self.module_lvl -1)
		if self.elite > 0:
			if atk_interval/self.attack_speed * 100 < self.talent1_params[0]: atkbuff_talent = 0
		atkbuff = self.skill_params[1] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + atkbuff_talent + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/atk_interval * self.attack_speed/100 * self.targets
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

		if self.skill < 2:
			atkbuff += self.skill_params[3] if self.skill == 1 else 0
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Matoimaru",pp,[1,2],[2],2,6,2)
		if self.module_dmg and self.module == 2: self.name += " afterRevive"

	def skill_dps(self, defense, res):
		aspd = 30 if self.module_dmg and self.module == 2 else 0
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class May(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("May",pp,[1,2],[1],1,6,1)
		if self.module == 1 and self.module_dmg: self.name += " vsAerial"
		
	def skill_dps(self, defense, res):
		atkbuff = min(self.talent1_params)
		aspd = max(self.talent1_params)
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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
		final_atk = self.atk * (1 + self.buff_atk + self.talent1_params[0] + self.skill_params[0]*self.skill) + self.buff_atk_flat
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
			
		if self.skill < 2:
			sp_cost = self.skill_cost 
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			defshred = self.skill_params[1] if self.skill == 1 else 0
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Meteorite",pp,[1],[2],1,1,2)
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		crate = self.talent1_params[1] if self.elite > 0 else 0
		newdef = np.fmax(0, defense - 100) if self.module == 2 else defense
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_atk_crit = self.atk * (1 + self.buff_atk + 0.6) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
		hitcrit = np.fmax(final_atk_crit - newdef, final_atk_crit * 0.05)
		skill_scale = self.skill_params[0] if self.skill > 0 else 1
		if self.skill < 2:	
			skillhitdmg = np.fmax(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05)
			skillcritdmg = np.fmax(final_atk_crit *skill_scale - newdef, final_atk_crit * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avghit = crate * hitcrit + (1-crate) * hitdmg
			avgskill = crate * skillcritdmg + (1-crate) * skillhitdmg
			avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1) 
			dps = avgphys/self.atk_interval * self.attack_speed/100 * self.targets
		return dps

class Midnight(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Midnight",pp,[1],[],1,6,0) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " rangedAtk"
	
	def skill_dps(self, defense, res):
		atk_scale = 1 if self.trait_dmg else 0.8
		crate = self.talent1_params[0] if self.elite > 0 else 0
		cdmg = self.talent1_params[1]
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
		if self.skill == 1:
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * cdmg * atk_scale * (1-res/100), final_atk * cdmg * atk_scale * 0.05)
		else:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * cdmg * atk_scale - defense, final_atk * cdmg * atk_scale * 0.05)
		avghit = crate * critdmg + (1-crate) * hitdmg
		dps = avghit / self.atk_interval * self.attack_speed / 100
		return dps

class Minimalist(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Minimalist",pp,[1,2],[2],2,6,2)
		if not self.trait_dmg: self.name += " minDroneDmg"

	def skill_dps(self, defense, res):
		drone_dmg = 1.2 if self.module == 2 else 1.1
		if not self.trait_dmg: drone_dmg = 0.2
		crate = self.talent1_params[0] if self.elite > 0 else 0
		cdmg = self.talent1_params[1]
		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
			dmgperinterval = final_atk + drone_dmg * final_atk
			hitdmgarts = np.fmax(dmgperinterval * (1-res/100), dmgperinterval * 0.05) * (1 + crate*(cdmg-1))
			dps = hitdmgarts/self.atk_interval * (self.attack_speed + self.skill_params[1] * self.skill) / 100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			dmgperinterval = final_atk + drone_dmg * final_atk
			hitdmg = np.fmax(dmgperinterval * (1-res/100), dmgperinterval * 0.05) * (1 + crate*(cdmg-1))
			skilldmg = hitdmg * skill_scale * 2
			if not self.trait_dmg: skilldmg *= 2.55/2.4 #because it hits twice, the second hit is guaranteed to hit for more
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval*(self.attack_speed)/100
		return dps

class Mint(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mint",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			nukehit = final_atk * self.skill_params[1]
			self.name += f" lastHit:{int(nukehit)}"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		if self.skill == 0: return res * 0
		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class MissChristine(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("MissChristine",pp,[1,2],[1],2,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 1 and self.skill_dmg : self.name += " avgNerv"
		if self.skill == 2 and self.skill_dmg and self.trait_dmg: self.name += " vsFallout"
		if self.module == 1 and self.module_lvl > 1 and self.module_dmg: self.name += " vsPara"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.trait_dmg else 1
		if self.module == 1 and self.module_lvl > 1 and self.module_dmg:
			atk_scale *= 0.9 + 0.1 * self.module_lvl
		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 1:
			final_atk = self.atk * (1 + self.skill_params[0] + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
			if self.skill_dmg:
				ele_gauge = 1000 if self.trait_dmg else 2000
				time_to_fallout = ele_gauge/(0.1 * dps)
				dps += 6000/(10 + time_to_fallout)
			dps *= min(2,self.targets)

		if self.skill == 2:
			skill_scale = self.skill_params[5]
			ele_scale = self.skill_params[2] if self.skill_dmg and self.trait_dmg else 0
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)
			eledmg = final_atk * ele_scale * atk_scale
			dps = (hitdmg + eledmg) * self.targets

		return dps

class MisumiUika(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("MisumiUika",pp,[2],[1],2,1,1)

	def skill_dps(self, defense, res):
		if self.skill == 2:
			skill_scale = self.skill_params[2] + self.talent2_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg / 0.3
		else:
			dps = res * 0
		return dps

class Mizuki(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mizuki",pp,[1,2,3],[1,2,3],3,1,1)
		if self.talent2_dmg: self.name += " vsLowHp"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.module == 3 and self.module_dmg: self.name += " inIS"

	def skill_dps(self, defense, res):
		bonusdmg = self.talent1_params[0] if self.elite > 0 else 0
		bonustargets = self.talent1_params[1] if self.elite > 0 else 0
		atkbuff = self.talent2_params[1] if self.talent2_dmg else 0
		aspd = 50 if self.module == 3 and self.module_dmg else 0
		if self.module == 3 and self.module_dmg and self.module_lvl > 1: bonustargets += 1
		if self.module == 3 and self.module_dmg and self.module_lvl == 3 and self.skill > 0: bonustargets += 1

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			talent_scale = self.skill_params[1] if self.skill == 1 else 1
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2 #sp lockout
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitbonus = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			skillbonus = np.fmax(final_atk * bonusdmg * talent_scale * (1-res/100), final_atk * bonusdmg * talent_scale * 0.05)

			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			avgarts = skillbonus
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
					avgarts = (skillbonus + (atks_per_skillactivation -1) * hitbonus) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
					avgarts = (skillbonus + int(atks_per_skillactivation) * hitbonus) / (int(atks_per_skillactivation)+1)		
			dps = avghit/(self.atk_interval/(self.attack_speed/100)) * self.targets + avgarts/(self.atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets, bonustargets)
			
		if self.skill == 2:
			atkbuff += self.skill_params[1]
			atk_interval = self.atk_interval + self.skill_params[0]
			bonustargets += 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(atk_interval/(self.attack_speed/100)) * self.targets + hitdmgarts/(atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets, bonustargets)
		
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			bonustargets += 2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * self.targets + hitdmgarts/(self.atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets, bonustargets)
		return dps

class Mlynar(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mlynar",pp,[1,2,3],[1],3,1,1)
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
		if self.skill == 0: dps = res * 0
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
		super().__init__("Mon3tr",pp,[3],[],3,1,0)
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		aspd = self.talent2_params[1] if self.elite > 1 else 0		
		if self.skill < 3: return res * 0
		if self.skill == 3:
			atk_interval = self.atk_interval + self.skill_params[4]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] ) + self.buff_atk_flat
			dps = final_atk/(atk_interval / (self.attack_speed+aspd)*100) * np.fmax(-defense, 1) * min(self.targets, 3)
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
		skill_scale = max(self.skill_params[:2]) if self.skill > 0 else 1
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
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*min(self.skill,1)) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps * self.targets

class Mountain(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mountain",pp, [1,2,3],[2,1],2,1,1)
		if self.module == 2:
			if self.module_dmg: self.name += " >50% hp"				
			else: self.name += " <50% hp"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		crate = self.talent1_params[1]
		cdmg = self.talent1_params[0]
		aspd = 10 if self.module == 2 and self.module_dmg else 0

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
		if self.skill in [0,2]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill/2) + self.buff_atk_flat
			normalhitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			crithitdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = normalhitdmg * (1-crate) + crithitdmg * crate
			dps = avgdmg/(self.atk_interval/((self.attack_speed + aspd)/100)) * min(self.targets , (1+self.skill/2))
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
		super().__init__("Mousse", pp, [1,2],[1],1,6,1)
		if self.module == 1 and self.module_dmg: self.name += " NotBlocking"
	
	def skill_dps(self, defense, res):
		crate = self.talent1_params[0]
		atkbuff = self.skill_params[0] * min(self.skill,1)
		aspd = 8 if self.module == 1 and self.module_dmg else 0

		if self.skill < 2:
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			final_atk2 = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg2 = np.fmax(final_atk2 * (1-res/100), final_atk2 * 0.05)
			avgdmg = (hitdmg * sp_cost + hitdmg2) / (sp_cost + 1)
			dps = avgdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * (1+crate)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * (1+crate)
		return dps

class MrNothing(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("MrNothing",pp,[1,2],[1],2,1,1)
		if self.elite > 0 and not self.talent_dmg: self.name += " idealTalentUsage"
		if self.elite == 0: self.talent_dmg = True
		if not self.talent_dmg: self.skill_dmg = False
		if self.skill_dmg and self.skill == 2: self.name += " Apsd+Skill"

	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		aspd = self.skill_params[3] if self.skill == 2 and self.skill_dmg else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		hitdmg2 = np.fmax(final_atk * self.talent1_params[1] - defense, final_atk * self.talent1_params[1] * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 if self.talent_dmg else hitdmg2 / self.talent1_params[0]
		return dps
		
class Mudrock(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Mudrock",pp,[1,2,3],[1,2],3,1,1)
		if self.module == 2 and self.module_dmg: self.name += " alone"
		if self.module == 2 and self.talent2_dmg: self.name += " vsNonSarkaz"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
		try: self.hits = kwargs['hits']
		except KeyError: self.hits = 0
		if self.hits > 0 and self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
			
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 3 else 0
		if self.module == 2 and self.module_dmg: atkbuff += 0.08
		dmg = self.talent2_params[1] if self.module == 2 and self.module_lvl > 1 and self.talent2_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		atk_interval = self.atk_interval * 0.7 if self.skill == 3 else self.atk_interval
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * dmg
		dps = hitdmg/atk_interval * self.attack_speed/100
		if self.skill == 3: dps *= min(self.targets,3)

		if self.skill == 2 and self.hits > 0:
			atk_scale = self.skill_params[0]
			skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * dmg
			spcost = self.skill_cost
			extra_sp = (self.module_lvl-1)/9 if self.module == 1 else 0
			if self.module_lvl == 2: extra_sp *= (spcost-1)/spcost #these roughly factor in the wasted potential. realistically more gets wasted due to the lockout
			if self.module_lvl == 3: extra_sp *= (2*spcost-3)/(2*spcost)
			skillcycle = spcost / (self.hits+extra_sp) + 1.2
			dps += skilldmg / skillcycle * self.targets
		return dps
	
class Muelsyse(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Muelsyse",pp,[1,2,3],[1,2],3,1,1)
		try:
			self.cloned_op = kwargs["prev_op"]
			_ =  self.cloned_op.ranged
		except:
			self.cloned_op = Ela(pp)
		clone_name = "Muelsyse(" + self.cloned_op.name.split()[0] + ")"
		self.name = self.name.replace("Muelsyse", clone_name)
		if not self.skill == 3: self.trait_dmg = self.trait_dmg and self.talent_dmg
		
		if not self.cloned_op.ranged:
			if not self.talent_dmg: self.name += " no Clones"
			else:
				if self.trait_dmg: self.name += " blocked"
				if self.talent2_dmg: self.name += " maxSteal"
		else:
			if self.skill == 3:
				clones = 5
				if not self.skill_dmg: clones -= 2
				if not self.talent_dmg: clones -= 1
				if self.trait_dmg: self.name += " blocked"
				self.name += f" {clones}clones"
			else:
				if not self.talent_dmg:
					self.name += " noClones"
				else:
					if self.trait_dmg: self.name += " blocked"
					self.name += " CloneAlwaysAtks"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.5 if self.trait_dmg else 1
		if self.trait_dmg and self.module == 2: atk_scale = 1.65
		copy_factor = 1 if self.module == 1 and self.module_lvl == 3 else 0.5 + 0.2 * self.elite

		atkbuff = self.skill_params[2] if self.skill == 1 else self.skill_params[1] * min(self.skill,1)
		aspd = self.skill_params[3] if self.skill == 1 else 0

		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100

		main = 1 if self.talent_dmg else 0
		clone_atk = self.cloned_op.atk * copy_factor * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		if not self.cloned_op.ranged and self.talent2_dmg: clone_atk += 250
		summondamage = np.fmax(clone_atk * (1-res/100), clone_atk * 0.05) if not self.cloned_op.physical else np.fmax(clone_atk - defense, clone_atk * 0.05)
		extra_summons = 0
		extra_summons_skill = 0
		if self.cloned_op.ranged and self.talent_dmg: 
			extra_summons += min(4,2.5/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100)))
			extra_summons_skill =  min(4,2.5/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100)) * 2) if self.skill == 2 else min(4,2.5/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100)))
			if self.skill == 0: extra_summons_skill = extra_summons
			extra_summons = (50 * extra_summons + 15 * extra_summons_skill) / 65
			
		if self.skill == 3 and self.cloned_op.ranged:
			extra_summons = 4 if self.skill_dmg else 2
			dps += (main+extra_summons) * summondamage/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100))
		if self.skill == 2 and self.cloned_op.ranged:
			dps += (main+extra_summons) * summondamage/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100)) * 2
		elif self.skill != 3 or (self.skill == 3 and not self.cloned_op.ranged):
			dps += (main+extra_summons) * summondamage/(self.cloned_op.atk_interval/((self.attack_speed + aspd)/100))
		return dps

class Narantuya(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Narantuya",pp,[1,2,3],[1],3,1,1)
		if self.module == 1: self.trait_dmg = self.trait_dmg and self.module_dmg
		if not self.trait_dmg: self.name += " maxRange"
		else: self.name += " minRange"
		if self.talent_dmg and self.elite > 0: self.name += " maxSteal"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
	def skill_dps(self, defense, res):
		stealbuff = self.talent1_params[1] if self.elite > 0 and self.talent_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat + stealbuff
		atk_scale = 1.1 if self.module == 1 and self.trait_dmg else 1
		
		if self.skill == 1:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			interval = self.atk_interval/self.attack_speed*100 if self.trait_dmg else 2.1
			dps = hitdmg / interval
			if self.targets > 1: dps *= 3
		if self.skill == 2:
			skill_scale = self.skill_params[2]
			return_scale = self.skill_params[3]
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			returndmg = np.fmax(final_atk * return_scale * atk_scale - defense, final_atk * return_scale * atk_scale * 0.05) * self.targets
			interval = 1.15 if self.trait_dmg else 2
			dps = (hitdmg+returndmg) / interval
		if self.skill in [0,3]:
			skill_scale = self.skill_params[0] if self.skill == 3 else 1
			aoe_scale = self.skill_params[1] if self.skill == 3 else 0
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat + stealbuff
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05) * max(self.skill,1)
			aoedmg = np.fmax(final_atk * aoe_scale * atk_scale - defense, final_atk * aoe_scale * atk_scale * 0.05)
			if not self.trait_dmg: aoedmg = 0
			interval = 20/13.6 if not self.trait_dmg else (self.atk_interval/(self.attack_speed/100))
			dps = hitdmg/interval + min(self.targets,3) * aoedmg/interval
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
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
		if self.skill == 1: aspd += self.skill_params[1]
		hitdmg = np.fmax(final_atk * atk_scale - defense * (1 - def_shred), final_atk * atk_scale * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Necrass(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Eblana",pp,[1,2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 0:
			if not self.trait_dmg: self.name += " noSummon"
			else: self.name += f" {int(self.talent1_params[0])}Summons"
			if self.talent_dmg: self.name += "(upgraded)"
		if self.skill == 1:
			if not self.trait_dmg: self.name += " 1Summon"
			else: self.name += f" {int(self.talent1_params[0])}Summons"
			if self.talent_dmg: self.name += "(upgraded)"
		if self.skill == 3:
			if not self.trait_dmg: self.name += " noSummon"
			else:
				if self.talent_dmg:
					self.name += " 1+2summons"
				else:
					self.name += " 1summon"
				if self.skill_dmg: self.name += "(Maxed)"
		if self.talent2_dmg and self.elite > 1: self.name += " vsLowHp"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		self.no_kill = self.try_kwargs(6,["nokill","kill"],**kwargs)
		if self.module == 1 and self.module_lvl > 1 and not self.no_kill: self.name += " afterKill"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent2_params[1] if self.elite > 1 and self.talent2_dmg else 1
		atk_scale = 1.15 if self.module_dmg and self.module == 1 else 1
		atkbuff = 0.05 + 0.1 * self.module_lvl if self.module == 1 and self.module_lvl > 1  and not self.no_kill else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		summon_atk = self.talent1_params[2] if self.talent_dmg else 0
		if self.skill == 0:
			drones = self.talent1_params[0] if self.trait_dmg else 0
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale * atk_scale
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100
			final_atk_summon = self.drone_atk * (1 + self.buff_atk + summon_atk) + self.buff_atk_flat
			summondmg = np.fmax(final_atk_summon * (1-res/100), final_atk_summon * 0.05) * dmg_scale
			dps += drones * summondmg / self.drone_atk_interval * (self.attack_speed) / 100
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale * atk_scale
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_scale
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100
			hits = self.talent1_params[0] if self.trait_dmg else 1
			dps += hits * skilldmg * self.targets / (self.skill_cost/(1 + self.sp_boost) + 1.2) #sp lockout
			final_atk_summon = self.drone_atk * (1 + self.buff_atk + summon_atk) + self.buff_atk_flat
			summondmg = np.fmax(final_atk_summon * (1-res/100), final_atk_summon * 0.05) * dmg_scale
			dps += hits * summondmg / self.drone_atk_interval * (self.attack_speed) / 100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_scale * atk_scale
			dps = 2 * hitdmg * min(self.targets,2)
		if self.skill == 3:
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale * atk_scale
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100
			skill_scale = self.skill_params[1]
			skill_hits = self.skill_params[4]
			skilldmg =  np.fmax(final_atk *skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_scale * atk_scale
			dps += skilldmg * skill_hits * self.targets / (self.skill_cost/(1 + self.sp_boost) + 1.2 + skill_hits)
			if self.trait_dmg:
				main_atk_buff = 2 + 0.8 * 6 if self.skill_dmg else 2
				main_summon_atk = self.drone_atk * (1 + self.buff_atk + main_atk_buff) + self.buff_atk_flat
				mainhit = np.fmax(main_summon_atk * (1-res/100), main_summon_atk * 0.05) * dmg_scale
				maindps = mainhit/(self.drone_atk_interval + 0.7) * self.attack_speed/100
				mainskilldps = np.fmax(main_summon_atk * 1.2 * (1-res/100), main_summon_atk * 1.2 * 0.05) * dmg_scale
				dps += (maindps * 15/(1+self.sp_boost) + mainskilldps * 8 * self.targets) / (8 + 15/(1+self.sp_boost))
				if self.talent_dmg:
					final_atk_summon = self.drone_atk * (1 + self.buff_atk + summon_atk) + self.buff_atk_flat
					summondmg = np.fmax(final_atk_summon * (1-res/100), final_atk_summon * 0.05) * dmg_scale
					dps += 2 * summondmg / self.drone_atk_interval * (self.attack_speed) / 100

		return dps

class Nian(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Nian",pp,[1,2,3],[1,2],3,1,1)
		if self.module == 1 and self.module_lvl > 1 and self.module_dmg: self.name += " 3shieldsBroken"
		try: self.hits = kwargs['hits']
		except KeyError: self.hits = 0
		if self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
		if self.module == 1: #module lvl 1 does not come with an atk increase, breaking the automatic system
			if self.module_lvl > 1: self.atk += 35
			if self.module_lvl > 2: self.atk += 15
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		if self.module == 1 and self.module_dmg and self.module_lvl > 1:
			atkbuff += 3 * 0.05 if self.module_lvl == 2 else 3 * 0.07

		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			atk_scale = self.skill_params[2]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg * self.hits
		if self.skill in [0,3]:
			atkbuff += self.skill_params[4] if self.skill == 3 else 0
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class Nymph(Operator): #TODO: rework with the module and stuff
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Nymph",pp,[1,2,3],[1],3,1,1)
		if self.talent2_dmg and self.elite == 2: self.name += f" {int(self.talent2_params[1])}stacks"
		if self.trait_dmg and self.talent_dmg: self.name += " vsFallout(not inlcuding 800FalloutDps)"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		talent1_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 0
		atkbuff = self.talent2_params[0] * self.talent2_params[1] if self.elite == 2 and self.talent2_dmg else 0
		aspd = self.talent2_params[2] if self.module == 1 and self.module_lvl > 1 and self.talent2_dmg else 0
		burst_scale = 1.1 if self.module == 1 else 1
			
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			necrosis_scale = self.skill_params[1]
			ele_scale = self.skill_params[2]
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			eledmg = 0
			if self.trait_dmg and self.talent_dmg:
				eledmg = final_atk * ele_scale
			dps = (hitdmg+eledmg)/self.atk_interval * (self.attack_speed+aspd)/100
			
		if self.skill == 2:
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2
			atk_scale = self.skill_params[0]
			talent1_overwrite = self.skill_params[3]
			necrosis_scale = self.skill_params[1]
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05) * self.targets
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 + skilldmg/sp_cost
		
		if self.skill in [0,3]:
			atkbuff += self.skill_params[0] if self.skill == 3 else 0
			aspd += self.skill_params[1] if self.skill == 3 else 0
			final_atk = self.atk * (1+atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			if self.trait_dmg and self.talent_dmg and self.skill == 3:
				hitdmg = final_atk * np.fmax(1,-res) /(1+self.buff_fragile) * burst_scale
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,1+self.skill/3)
		
		extra_dmg = 0
		if self.talent_dmg and self.trait_dmg:
			dmg_rate = talent1_scale
			if self.skill == 2:
				dmg_rate = talent1_overwrite
			extra_dmg = final_atk * dmg_rate
		
		return dps + extra_dmg

class Odda(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Odda",pp,[1,2],[1],2,6,1)	
		if self.module == 1 and self.module_dmg: self.name += " 3inRange"
		if self.talent_dmg and self.elite > 0: self.name += f" after{int(self.talent1_params[0])}Hits"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 0
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			splashhitdmg = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			splashskillhitdmg = np.fmax(0.5 * final_atk * atk_scale * skill_scale - defense, 0.5 * final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avgsplash = (sp_cost * splashhitdmg + splashskillhitdmg) / (sp_cost + 1)
			dps = avgphys/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += avgsplash/self.atk_interval * self.attack_speed/100 * (self.targets - 1)
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			splashhitdmg = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += splashhitdmg/self.atk_interval * self.attack_speed/100 * (self.targets - 1)
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
			
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1	
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + (1 + self.skill) * skillhitdmg) / (sp_cost + 1)
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Passenger",pp,[1,2,3],[1,2],3,1,1)
		if self.talent_dmg and self.elite > 0: self.name += " vsHighHp"
		if not self.talent2_dmg and self.elite == 2: self.name += " EnemyClose"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		targetscaling = [0,1,2,3,4,5] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3, 1.85+0.85**2+0.85**3+0.85**4]
		if self.module == 1: targetscaling = [0, 1, 1.9, 1.9+0.9**2, 1.9+0.9**2+0.9**3, 1.9+0.9**2+0.9**3+0.9**4]
		targets = min(5, self.targets) if self.skill == 2 else min(4, self.targets)
		if self.elite < 2 and self.skill == 3: targetscaling[4] = targetscaling[3]

		dmg_scale = self.talent1_params[1] if self.elite > 0 and self.talent_dmg else 1	
		sp_boost = 0
		atkbuff = self.talent2_params[0] if self.talent2_dmg and self.elite == 2 else 0
		if self.module == 1 and self.module_lvl > 1 and self.talent2_dmg:
			sp_boost = 0.05 + 0.1 * self.module_lvl

		if self.skill == 1:
			sp_cost = self.skill_cost/(1+sp_boost + self.sp_boost) +1.2
			atk_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skill = int(sp_cost/atkcycle)
			avghit = (hitdmg * atks_per_skill + skilldmg) / (atks_per_skill + 1)	
			dps = avghit/(self.atk_interval/(self.attack_speed/100)) * targetscaling[targets]
		if self.skill in [0,2]:
			atkbuff += self.skill_params[2] if self.skill == 2 else 0
			atk_interval = self.atk_interval * (1 + self.skill_params[0] * self.skill/2)
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(atk_interval/(self.attack_speed/100)) * targetscaling[targets]
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+sp_boost + self.sp_boost) + 1.2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skillhit = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * targetscaling[targets]
			dps += 8 * skillhit / (sp_cost)
		return dps*dmg_scale

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

		if self.skill < 2:
			atk_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk  * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			if self.skill == 0: skilldmg = hitdmg
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
		super().__init__("Pepe",pp,[1,2,3],[1,3],3,1,1)
		self.try_kwargs(4,["stacks","maxstacks","max","nostacks"],**kwargs)
		if self.module == 1 and self.module_dmg: self.name += " 3inRange"
		if self.skill_dmg and not self.skill == 1: self.name += " maxStacks"
		if self.targets > 1: self.name += f" {self.targets}targets"	
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent2_params[0]
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			sp_cost = self.skill_cost /(1+self.sp_boost) + 1.2 #sp lockout
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) + np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05) * (self.targets-1)
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05) + np.fmax(0.5 * skill_scale * final_atk * atk_scale - defense, 0.5 * skill_scale * final_atk * atk_scale * 0.05) * (self.targets-1)
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
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgaoe = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) + hitdmgaoe/(self.atk_interval/((self.attack_speed+aspd)/100))*(self.targets - 1)
		
		if self.skill == 3:
			self.atk_interval = 2
			atkbuff += self.skill_params[0]
			if self.skill_dmg:
				atkbuff += 4 * self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgaoe = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) + hitdmgaoe/(self.atk_interval/(self.attack_speed/100))*(self.targets - 1)
		return dps

class Phantom(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Phantom",pp,[1,2,3],[1,2,3],2,1,2)
		if self.skill == 2: self.name += f" {int(self.skill_params[0])}hitAvg"
		if self.elite == 0: self.talent_dmg = False
		if self.talent_dmg and self.elite > 0: self.name += " with clone"   ##### keep the ones that apply
		if not self.module_dmg and self.module == 2: self.name += " adjacentAllies"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.module == 2 and self.module_lvl == 3: self.drone_atk += 60
		if self.skill == 3:
			mainbuff = 0.1 if self.module == 2 and self.module_dmg else 0
			atkbuff = 0.1 if self.module == 2 and self.module_lvl > 1 and self.talent_dmg else 0
			final_atk = self.atk * (1 + atkbuff + mainbuff + self.buff_atk) + self.buff_atk_flat
			final_atk_drone = self.drone_atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			damage = final_atk * self.skill_params[0] * (1+self.buff_fragile)
			damage2 = final_atk_drone * self.skill_params[0] * (1+self.buff_fragile)
			if not self.talent_dmg: self.name += f" initialHit:{int(damage)}"
			else: self.name += f" initialHits:{int(damage)}/{int(damage2)}"

	def skill_dps(self, defense, res):
		if self.skill == 2:
			selfhit = 0
			clonehit = 0
			mainbuff = 0.1 if self.module == 2 and self.module_dmg else 0
			atkbuff = 0.1 if self.module == 2 and self.module_lvl > 1 and self.talent_dmg else 0
			rate = self.skill_params[1]
			count = int(self.skill_params[0])
			for i in range(count):
				atkbuff += rate
				final_atk = self.atk * (1 + atkbuff + mainbuff + self.buff_atk) + self.buff_atk_flat
				final_clone = self.drone_atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
				selfhit += np.fmax(final_atk - defense, final_atk * 0.05)
				clonehit += np.fmax(final_clone - defense, final_clone * 0.05)			
			dps = selfhit /self.atk_interval * self.attack_speed/100 / count
			if self.talent_dmg:
				dps += clonehit /self.drone_atk_interval * self.attack_speed/100 / count
		else:
			mainbuff = 0.1 if self.module == 2 and self.module_dmg else 0
			atkbuff = 0.1 if self.module == 2 and self.module_lvl > 1 and self.talent_dmg else 0
			final_atk = self.atk * (1 + atkbuff + mainbuff + self.buff_atk) + self.buff_atk_flat
			final_clone = self.drone_atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg_clone = np.fmax(final_clone - defense, final_clone * 0.05)	
			dps = hitdmg /self.atk_interval * self.attack_speed/100
			if self.talent_dmg:
				dps += hitdmg_clone /self.drone_atk_interval * self.attack_speed/100

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
			
		if self.skill < 2:
			skill_scale = self.skill_params[0] * self.skill
			defignore = self.skill_params[1] if self.skill == 1 else 0
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
		atkbuff = self.skill_params[0] * self.skill
		aspd = self.skill_params[1] * self.skill
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
		final_atk = self.atk * (1 + max(self.skill_params) * min(self.skill, 1) + self.buff_atk) + self.buff_atk_flat
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
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + self.skill_params[1] * self.skill) / 100
		return dps

class Popukar(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Popukar",pp,[1],[],1,6,0)
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]*self.skill) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100 * min(self.targets,2)
		return dps

class Pozemka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pozemka",pp,[1,3],[2,1],3,1,2)
		if self.module == 2 and self.module_lvl > 1: self.drone_atk += 10 + 20 * self.module_lvl
		if not self.talent_dmg and self.elite > 0:
			self.name += " w/o Typewriter"
			self.talent2_dmg = False
		elif not self.talent2_dmg and self.elite > 1: self.name += " TW separate"
		self.pot = pp.pot
		if self.skill == 3:
			self.module_dmg = self.module_dmg and self.skill_dmg
		if self.module == 2 and self.module_dmg: self.name += " DirectFront"

	def skill_dps(self, defense, res):
		defshred = 0
		if self.talent_dmg:
			if self.talent2_dmg:
				defshred = 0.25 if self.pot > 4 else 0.23
			else:
				defshred = 0.2 if self.pot > 4 else 0.18
			if self.module == 1:
				defshred += 0.05 * (self.module_lvl - 1)
		newdef = defense * (1-defshred)
		atk_scale = 1.05 if self.module_dmg and self.module == 2 else 1

		if self.skill < 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill) + self.buff_atk_flat
			rate = self.skill_params[1] if self.skill == 1 else 0
			skill_scale = self.skill_params[2] if self.skill == 1 else 0
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmg2 = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			avghit = rate * hitdmg2 + (1 - rate) * hitdmg
			dps = avghit/self.atk_interval * self.attack_speed/100
			if self.talent_dmg and self.elite > 0:
				final_atk2 = self.drone_atk * (1 + self.skill_params[0]*self.skill)
				hitdmg = np.fmax(final_atk2 * atk_scale - newdef, final_atk2 * atk_scale * 0.05)
				hitdmg2 = np.fmax(final_atk2 * atk_scale * skill_scale - newdef, final_atk2 * atk_scale * skill_scale * 0.05)
				avghit = rate * hitdmg2 + (1 - rate) * hitdmg
				dps += avghit/self.drone_atk_interval

		if self.skill == 3:
			self.atk_interval = 1
			skill_scale = self.skill_params[1]
			skill_scale2 = self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			if self.module_dmg or self.skill_dmg:
				hitdmg = np.fmax(final_atk * atk_scale * skill_scale2 - newdef, final_atk * atk_scale * skill_scale2 * 0.05)	
			hitdmgTW = 0
			if self.talent_dmg:
				hitdmgTW = np.fmax(self.drone_atk * skill_scale2 - newdef, self.drone_atk * skill_scale2 * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 + hitdmgTW
		return dps

class PramanixAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("PramanixAlter",pp,[1,2,3],[2],3,1,2)
		if self.module_dmg and self.module == 2: self.name += " manyTargets"
		if self.skill == 2 and not self.skill_dmg: self.name += " iceOnly"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		if self.skill == 0: return (defense * 0)
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg * self.targets / (self.skill_cost+1) * (1 + self.sp_boost)
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			ice_scale = self.skill_params[1]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-res/100), final_atk  * skill_scale * atk_scale * 0.05)
			icedmg = np.fmax(final_atk * atk_scale * ice_scale * (1-res/100), final_atk * atk_scale * ice_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * self.targets + icedmg * self.targets
			if not self.skill_dmg:
				dps = icedmg * self.targets
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_scale = self.skill_params[5]
			newres = np.fmax(0, res - 10)
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk  * skill_scale * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+30)/100 * self.targets
		return dps

class ProjektRed(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ProjektRed", pp,[1],[2],1,1,2)
		if self.module_dmg and self.module == 2: self.name += " alone"
	
	def skill_dps(self, defense, res):
		atkbuff = 0.1 if self.module_dmg and self.module == 2 else 0
		mindmg = 0.05 if self.elite == 0 else self.talent1_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]*self.skill) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * mindmg)
		dps = hitdmg / self.atk_interval * self.attack_speed/100
		return dps

class Provence(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Provence",pp,[1,2],[1],2,1,1)
		if self.talent_dmg and self.elite > 0: self.name += " directFront"
		if self.skill == 1:
			if self.skill_dmg: self.name += " vs<1%Hp"
			else: self.name += " vsFullHp"

	def skill_dps(self, defense, res):
		crate = 0
		cdmg = self.talent1_params[2]
		if self.elite > 0:
			crate = self.talent1_params[1] if self.talent_dmg else self.talent1_params[0]	
		if self.skill < 2:
			skill_scale = 1 + self.skill_params[1] * 5 if self.skill_dmg and self.skill == 1 else 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			critdmg = np.fmax(final_atk * skill_scale * cdmg - defense, final_atk * skill_scale * cdmg * 0.05)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			critdmg = np.fmax(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		avghit =  crate * critdmg + (1-crate) * hitdmg
		dps = avghit/self.atk_interval * self.attack_speed/100
		return dps

class Pudding(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Pudding",pp,[1,2],[2],2,6,2)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0]		
		targetscaling = [0,1,2,3,4] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3]
		if self.elite < 2 and not self.skill == 2: targetscaling[4] = targetscaling[3]
		targets = min(4, self.targets)

		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 * targetscaling[targets]
		if self.skill in [0,2]:
			atkbuff += self.skill_params[0] if self.skill == 2 else 0
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.targets > 1: dps = hitdmg/self.atk_interval * self.attack_speed/100  * targetscaling[4]
		return dps

class Qiubai(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Qiubai",pp,[1,3],[1],3,1,1)
		if self.skill != 3 and not self.trait_dmg: self.name += " rangedAtk"
		if self.talent_dmg and self.skill != 3:
			if self.module == 1 and self.module_dmg and self.module_lvl > 1:
				self.name += " vsBindANDslow"
			else: self.name += " vsBind/Slow"
		if self.skill == 3:
			if not self.talent_dmg and not self.talent2_dmg: self.name += " w/o talent1"
			else:
				if self.module == 1 and self.module_lvl > 1:
					if self.module_dmg and self.talent_dmg: self.name += " vsBindAndSlow"
					elif self.talent_dmg and not self.module_dmg: self.name += " vsBindOrSlow"
					elif self.module_dmg and not self.talent_dmg: self.name += " vsSlow+selfAppliedBind"
					else: self.name += " vsSelfAppliedBind"
				else:
					if self.talent_dmg: self.name += " vsBindOrSlow"
					else: self.name += " vsSelfAppliedBind"
			if self.skill_dmg: self.name += " maxStacks"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):

		bonus = 0.1 if self.module == 1 else 0
		extrascale = self.talent1_params[0] if self.elite > 0 else 0
		dmg = 1 + 0.1 * (self.module_lvl-1) if self.module == 1 and self.module_dmg else 1
		atk_scale = 1 if self.trait_dmg else 0.8

		if self.skill  < 2:
			skill_scale = self.skill_params[0]
			if not self.talent_dmg: 
				extrascale = 0
				dmg = 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * dmg
			hitdmgarts = np.fmax(final_atk * extrascale * (1-res/100), final_atk * extrascale * 0.05) * dmg
			skilldmg = np.fmax(final_atk * (skill_scale+extrascale) * (1-res/100), final_atk * (skill_scale+extrascale) * 0.05) * dmg * self.targets
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			avghit = (hitdmg + hitdmgarts + bonusdmg) * self.skill_cost + skilldmg + bonusdmg * self.targets
			avghit = avghit/(self.skill_cost+1) if self.skill == 1 else hitdmg + hitdmgarts + bonusdmg
			dps = avghit/self.atk_interval * (self.attack_speed)/100
		####the actual skills
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[1] * self.skill_params[2] if self.skill_dmg else 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			try: extrascale *= self.skill_params[3]
			except: pass
			atk_cycle = self.atk_interval / (self.attack_speed + aspd) * 100
			bind_chance = self.talent2_params[0]
			counting_hits = int(1.5/atk_cycle) + 1
			chance_to_attack_bind = 1 - (1-bind_chance) ** counting_hits
			if not self.talent_dmg and not self.talent2_dmg: #talent not active
				extrascale = 0
				dmg = 1
			elif self.module_dmg and not self.talent_dmg: #vs slow + self applied
				dmg = (dmg - 1) * chance_to_attack_bind + 1
			elif not self.module_dmg and self.talent_dmg: #vs slow OR bind
				dmg = 1
			elif not self.module_dmg and not self.talent_dmg: #only self applied
				extrascale *= chance_to_attack_bind
				dmg = 1
			hitdmgarts = np.fmax(final_atk * (1+extrascale) * (1-res/100), final_atk * (1+extrascale) * 0.05) * dmg
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmgarts+bonusdmg)/self.atk_interval * (self.attack_speed+aspd)/100 * min(3, self.targets)
		return dps
	
class Quartz(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Quartz",pp,[1,2],[1],1,6,1)
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[1]
		if self.skill < 2:
			atkbuff += self.skill_params[0] * self.skill
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

class Raidian(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Raidian",pp,[1,2,3],[3,2],3,6,3)
		if not self.trait_dmg: self.name += " noDrones"
		elif not self.talent_dmg: self.name += " 1Drone"
		else: self.name += " 2Drones"
		if self.skill == 0: self.name = self.name.replace("S0","S0(S3)")

	def skill_dps(self, defense, res):
		drones = 2 if self.talent_dmg else 1
		if not self.trait_dmg: drones = 0
		dmg = self.skill_params[6] if self.skill == 3 and drones > 0 else 1
		hits = 3 if self.skill == 2 else 1
		skill_attack = self.skill_params[0] if self.skill in [2,3] else 0
		final_atk = self.atk * (1 + self.buff_atk + skill_attack) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg
		final_drone = self.drone_atk * (1 + self.buff_atk + skill_attack) + self.buff_atk_flat + max(self.elite - 1,0) * self.talent2_params[0] * final_atk
		hitdmgdrone = np.fmax(final_drone - defense, final_drone * 0.05) * hits if self.skill in [1,2] else np.fmax(final_drone * (1-res/100), final_drone * 0.05) * dmg
		dps = hitdmg/self.atk_interval * self.attack_speed/100 + hitdmgdrone/self.drone_atk_interval* (self.attack_speed)/100 * drones
		return dps

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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Ray",pp,[1,2,3],[1,2],3,1,1)
		if not self.trait_dmg: self.name += " outOfAmmo"
		if self.talent_dmg and self.elite > 0: self.name += " with pet"
		if self.talent2_dmg and self.elite == 2: self.name += f" After{int(max(self.talent2_params))}Hits"

	def skill_dps(self, defense, res):
		atk_scale = 1.33 if self.module == 2 else 1.2
		dmg_scale = 1 + self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		atkbuff = self.talent2_params[0] * self.talent2_params[1] if self.talent2_dmg and self.elite == 2 else 0

		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if not self.trait_dmg:
				dps = hitdmg/(self.atk_interval * self.attack_speed/100 + 1.6)
				if self.module == 1: dps = 2*hitdmg/(2 * self.atk_interval * self.attack_speed/100 + 1.6)
			dps += skilldmg /(self.skill_cost/(1+self.sp_boost)+1.2)
		if self.skill in [0,2]:
			atkbuff += self.skill_params[0] * self.skill / 2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if not self.trait_dmg:
				dps = hitdmg/(self.atk_interval * self.attack_speed/100 + 1.6)
				if self.module == 1: dps = 2*hitdmg/(2 * self.atk_interval * self.attack_speed/100 + 1.6)
		if self.skill == 3:
			atk_scale *= self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * dmg_scale
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if not self.trait_dmg:
				dps = hitdmg/(self.atk_interval * self.attack_speed/100 + 0.4)
				if self.module == 1: dps = 2*hitdmg/(2 * self.atk_interval * self.attack_speed/100 + 0.4)
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * 8 * (self.atk_interval/(self.attack_speed/100)))
		else:
			return(self.skill_dps(defense,res))
	
class ReedAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ReedAlter",pp,[1,2,3],[1],2,1,1)
		self.try_kwargs(4,["sandwich","sandwiched","nosandwich","notsandwiched","notsandwich","nosandwiched"],**kwargs)
		if not self.talent_dmg and not self.skill == 3 and self.elite > 0: self.name += " w/o cinder"
		elif not self.skill == 3 and self.elite > 0: self.name += " withCinder"
		if self.skill_dmg and self.skill == 2: self.name += " Sandwiched"
		if self.targets > 1 and self.skill > 2: self.name += f" {self.targets}targets"
		if self.skill == 3:
			final_atk = self.atk * (1 + self.skill_params[1] + self.buff_atk) + self.buff_atk_flat
			nukedmg = final_atk * self.skill_params[3] * (1+self.buff_fragile)
			self.name += f" ExplosionDmg:{int(nukedmg)}"
	
	def skill_dps(self, defense, res):
		dmg_scale = self.talent1_params[2] if (self.talent_dmg and self.elite > 1) or self.skill == 3 else 1
		
		if self.skill < 2:
			atkbuff = self.skill_params[0] * self.skill
			aspd = self.skill_params[1] * self.skill
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale
			dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_scale = self.skill_params[1]
			multiplier = 2 if self.skill_dmg else 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(1-res/100,  0.05) * final_atk * atk_scale * dmg_scale * multiplier
			dps = hitdmgarts/0.8  #/1.5 * 3 (or /0.5) is technically the limit, the /0.8 come from the balls taking 2.4 for a rotation 
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Rockrock",pp,[1,2],[1],2,1,1)
		if not self.talent_dmg and self.elite > 0: self.name += " w/o talent"
		if self.skill_dmg and self.skill == 2: self.name += " overdrive"
		elif self.skill == 2: self.name += " w/o overdrive"
		if not self.trait_dmg: self.name += " minDroneDmg"

	def skill_dps(self, defense, res):
		drone_dmg = 1.1
		if not self.trait_dmg:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		atkbuff = self.talent1_params[0] * self.talent1_params[1] if self.talent_dmg and self.elite > 0 else 0
		aspd = 5 if self.module == 1 and self.module_lvl == 3 and self.talent_dmg else 0
		aspd += self.skill_params[1] if self.skill == 2 else self.skill_params[0] * self.skill
		if self.skill_dmg and self.skill == 2: atkbuff += self.skill_params[0]
		if self.skill == 2 and self.skill_dmg and self.trait_dmg: drone_dmg *= self.skill_params[3]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		dmgperinterval = final_atk + drone_dmg * final_atk
		hitdmgarts = np.fmax(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Rosa(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Rosa",pp,[1,2,3],[1,2],2,1,1)
		self.try_kwargs(2,["heavy","vsheavy","light","vslight","vs"],**kwargs)
		if self.module == 1: self.talent_dmg = self.talent_dmg and self.module_dmg
		if self.elite > 0:
			if not self.talent_dmg: self.name += " vsLight"
			else: self.name += " vsHeavy"
		if self.module == 2 and self.module_dmg: self.name += " maxRange"
		if self.module == 2 and self.module_lvl > 2 and not self.talent2_dmg: self.name += " noTalentStacks"
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
		if self.module == 2 and self.module_dmg: atk_scale = 1.12
		if self.module == 2 and self.module_lvl > 1:
			if self.talent2_dmg: atkbuff += (0.07 + 0.04 * self.module_lvl) * 3
			elif self.skill > 0: atkbuff += (0.07 + 0.04 * self.module_lvl)

		if self.skill < 2:
			atkbuff += self.skill_params[0] * self.skill
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
		super().__init__("Rosmontis",pp,[1,2,3],[1,3],3,1,1)
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
		bonusart = 1 if self.module == 3 else 0
		defshred = self.talent1_params[0] if self.elite > 0 else 0
		newdef = np.fmax(0, defense - defshred)
	
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + self.talent2_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk  * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - newdef, final_atk * 0.5 * 0.05) * bonushits
			bonushitdmg += np.fmax(final_atk * (1-res/100), final_atk * 0.05) * bonusart
			skillhitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			sp_cost = self.skill_cost
			avghit = ((sp_cost + 1) * (hitdmg + bonushitdmg) + skillhitdmg) / (sp_cost + 1)
			if self.skill == 0: avghit = hitdmg + bonushitdmg
			dps = avghit/self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 2:
			bonushits += 2
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[1] + self.talent2_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - newdef, final_atk * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - newdef, final_atk * 0.5 * 0.05) * bonushits
			bonushitdmg += np.fmax(final_atk * (1-res/100), final_atk * 0.05) * bonusart
			dps = (hitdmg+ bonushitdmg)/3.15 * self.attack_speed/100 * self.targets
		if self.skill == 3:
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
			bonushitdmg += np.fmax(final_atk * (1-res/100), final_atk * 0.05) * bonusart
			dps = (hitdmg+ bonushitdmg)/1.05 * self.attack_speed/100 * self.targets * min(self.targets,2)
		return dps
	
class Saga(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Saga",pp,[1,2,3],[2,1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " blocking"
		if self.module == 1 and self.module_lvl > 1 and self.talent_dmg: self.name += " vsLowHp"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module_dmg and self.module == 1 else 0
		dmg = self.module_lvl * 0.05 if self.module == 1 and self.module_lvl > 1 else 0
		if self.skill < 2:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * min(self.targets,6)
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2
			dps = hitdmg/self.atk_interval * self.attack_speed/100 + skilldmg/sp_cost
		if self.skill == 3:
			self.atk_interval = 1.55
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,2)
		return dps * (1+dmg)

class SandReckoner(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SandReckoner",pp,[1,2],[1],2,1,1)
		if not self.trait_dmg: self.name += " noDrones" 
		elif not self.talent2_dmg: self.name += " 1Drone"
		else: self.name += " 2Drones"
		if self.talent_dmg: self.name += " vsMachine"
		
	def skill_dps(self, defense, res):
		drones = 2 if self.talent2_dmg else 1
		if not self.trait_dmg: drones = 0
		dmg = 1.1 + min(0.1, 0.1 * self.elite) if self.talent_dmg else 1
		aspd = self.skill_params[0] if self.skill == 1 else 0
		module_aspd = -1 + 3 * self.module_lvl if self.module == 1 and self.module_lvl > 1 else 0
		atkbuff = self.skill_params[1] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg
		dps =  hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		final_atk_drone = self.drone_atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmgdrone = np.fmax(final_atk_drone *(1-res/100) , final_atk_drone * 0.05) * dmg
		dps += hitdmgdrone/self.drone_atk_interval * (self.attack_speed + aspd + module_aspd)/100 * drones
		return dps
	
class SanktaMiksaparato(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SanktaMiksaparato",pp ,[1,2,3],[1],2,6,1)
		if self.elite > 0 and not self.talent_dmg: self.name += " noStacks"
		if self.skill == 3: self.name += " idealCase" if self.skill_dmg else " 1hit/s"
		if self.skill == 3 and self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		aspd = self.talent1_params[1] * 3 if self.elite > 0 and self.talent_dmg else 0
		if self.skill < 2:
			final_atk = self.atk * (1+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  - defense, final_atk  * 0.05)
			skillhitdmg = np.fmax(final_atk * self.skill_params[0] - defense, final_atk * self.skill_params[0] * 0.05) * 3
			avgphys = (self.skill_cost * hitdmg + skillhitdmg) / (self.skill_cost + 1)
			if self.skill == 0: avgphys = hitdmg
			dps = avgphys/(self.atk_interval/((self.attack_speed + aspd)/100))
		if self.skill == 2:
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 3:
			final_atk = self.atk * (1+ self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)	* min(self.targets,3)
			dps = hitdmg/self.atk_interval * 10 * (self.attack_speed+aspd)/100 if self.skill_dmg else hitdmg
		return dps

class Savage(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Savage",pp,[1],[1],1,5,1) #available skills, available modules, default skill, def pot, def mod
		self.name = self.name.replace("P6","P5")
		if self.elite > 0 and self.talent_dmg: self.name += " 2+RangedTiles"
		if self.module == 1 and self.module_dmg: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent1_params[1] if self.talent_dmg else 0
		targets = 3 if self.elite == 2 else 2
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmg_skill = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			avghit = (hitdmg * self.skill_cost + hitdmg_skill)/(self.skill_cost + 1)
			dps = avghit / self.atk_interval * self.attack_speed/100 * min(self.targets, targets)
		return dps

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
		final_atk_drone = self.drone_atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
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
		if self.skill < 2:
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
			avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1) if self.skill == 1 else avghit
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Shalem",pp,[1,2],[1],2,6,1)
		if self.talent_dmg: self.name += " (in IS2)"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		extra_scale = 0.1 if self.module == 1 else 0
		aspd = self.talent1_params[0] if self.talent_dmg else 0
		atkbuff = self.talent1_params[1] if self.talent_dmg else 0
		crate = self.talent2_params[0] if self.elite == 2 else 0
		newres = res * (1 + self.talent2_params[1]) if self.elite == 2 else res

		####the actual skills
		if self.skill == 0:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk -defense , final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed /100
		if self.skill == 1:
			atk_interval = self.atk_interval * (1 + self.skill_params[0])
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			countinghits = int( self.talent2_params[2] /(atk_interval/((self.attack_speed+aspd)/100))) + 1
			nocrit = (1-crate)**countinghits
			hitdmg = np.fmax(final_atk * (1+extra_scale) * (1-res/100), final_atk * (1+extra_scale) * 0.05)
			shreddmg = np.fmax(final_atk * (1+extra_scale) * (1-newres/100), final_atk * (1+extra_scale) * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit) 
			dps = avgdmg/atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,3)
		if self.skill == 2:
			hits = self.skill_params[1]
			atk_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			countinghits =  (hits * int(self.talent2_params[2] /(self.atk_interval/((self.attack_speed+aspd)/100))) + 3)/self.targets + 1
			nocrit = (1-crate)**countinghits
			hitdmg = np.fmax(final_atk * (atk_scale + extra_scale) * (1-res/100), final_atk * (atk_scale + extra_scale) * 0.05)
			shreddmg = np.fmax(final_atk * (atk_scale + extra_scale) * (1-newres/100), final_atk * (atk_scale + extra_scale) * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit)
			dps = 6 * avgdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Sharp(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Sharp",pp,[1],[],1,1,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk + self.talent1_params[0]) + self.buff_atk_flat
		skill_scale = self.skill_params[1] if self.skill == 1 else 1
		hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
		dps =  hitdmg / self.atk_interval * (self.attack_speed) / 100
		return dps

class Sideroca(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Sideroca",pp,[1,2],[2],2,6,2) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg and self.elite == 2: self.name += f" After{int(self.talent1_params[0])}kills"
		if self.module == 2 and self.module_dmg: self.name += " blocking"
	
	def skill_dps(self, defense, res):
		dmg = 1.1 if self.module == 2 and self.module_dmg else 1
		aspd = self.talent1_params[1] if self.talent_dmg and self.elite == 2 else 0
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd)/100 * dmg
		return dps

class Siege(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Siege",pp,[1,2,3],[1,2],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " blocking"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		atkbuff += self.talent1_params[0]
		if self.module == 1 and self.module_lvl > 1: atkbuff += 0.02 + 0.02 * self.module_lvl	
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		if self.skill < 2:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05) * self.targets
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)				
			dps = avghit/self.atk_interval * self.attack_speed/100
		if self.skill == 3:
			atk_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/2.05 * self.attack_speed/100
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
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat		
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			sp_cost = self.skill_cost
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
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
		atkbuff = self.talent1_params[0] + self.skill_params[0] * min(self.skill,1)
		aspd = 0 if self.skill != 1 else self.skill_params[1]
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		if self.module == 2 and self.module_dmg: aspd += 30
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
		dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		return dps

class Skalter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SkadiAlter",pp,[1,3],[1],3,1,1)
		if self.skill == 3:
			if self.module == 1 and not self.module_dmg: self.name += " noModBonus"
			if self.talent_dmg: self.name += " +Seaborn"
			if self.talent2_dmg: self.name += " AllyInRange(add+9%forAH)"
			if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		if self.skill != 3: return res * 0
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		if self.talent2_dmg: atkbuff += self.talent2_params[0]
		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		dps = final_atk * skill_scale * np.fmax(1,-defense) * self.targets
		if self.talent_dmg: dps *= 2
		return dps

class Snegurochka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Snegurochka",pp,[1,2],[1],1,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 0 and not self.talent_dmg: self.name += " gotHit"
	
	def skill_dps(self, defense, res):
		aspd = self.talent1_params[0] if self.elite > 0 and self.talent_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)

		if self.skill < 2:
			skill_scale = self.skill_params[1] if self.skill == 1 else 1
			hitdmg_skill = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avghit = (hitdmg * self.skill_cost + hitdmg_skill)/(self.skill_cost + 1)
			dps = avghit / self.atk_interval * (self.attack_speed+aspd)/100
		
		if self.skill == 2:
			aspd += self.skill_params[0]
			dps = hitdmg / self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Specter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Specter",pp,[1,2],[1],2,1,1)		
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets" 
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module_dmg and self.module == 1 else 1
		final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * min(self.skill,1)) + self.buff_atk_flat
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
		atkbuff = self.skill_params[0] * min(self.skill,1) if self.trait_dmg else 0
		if not self.trait_dmg and self.module == 1: atkbuff += 0.15
		
		if not self.trait_dmg:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			doll_scale = self.talent1_params[1]
			hitdmg = np.fmax(final_atk * doll_scale * (1-res/100), final_atk * doll_scale * 0.05)
			return hitdmg
			
		if self.skill < 2:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+self.skill_params[1])/100
		if self.skill == 3:
			dmgbonus = 1 + self.skill_params[2]
			if not self.skill_dmg: dmgbonus = 1
			final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  - defense, final_atk * 0.05) * dmgbonus
			dps = dps = hitdmg/2.2 * self.attack_speed/100 * min(self.targets,2)
		return dps

class Stainless(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Stainless",pp,[1,2,3],[1,2],3,1,1)
		if self.skill in [0,3] and not self.skill_dmg: self.name += " TurretOnly"
		if self.skill != 1 and self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		try: self.hits = kwargs['hits']
		except KeyError: self.hits = 0
		if self.skill in [0,3]: self.name += f" {round(self.hits,2)}hits/s"
		self.params = [0,2,2.1,2.2,2.3,2.4,2.5,2.6,2.8,2.85,3][pp.mastery]
		self.params2 = [0,1,1,1,1.1,1.1,1.1,1.2,1.3,1.4,1.5][pp.mastery]
	
	def skill_dps(self, defense, res):
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,2)
		if self.skill in [0,3]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]*self.skill/3) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed + self.skill_params[1]*self.skill/3)/100
			if not self.skill_dmg: dps = 0
			turret_scale = self.params
			turret_aoe = self.params2
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
		dps = (1+self.skill) * avgdmg / self.atk_interval * (self.attack_speed) / 100
		return dps * min(1+self.skill, self.targets)

class Surfer(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Surfer",pp,[1,2],[],2,1,0)
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Surtr(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Surtr", pp, [1,2,3],[1],3,1,1)
		if self.skill == 1:
			if self.skill_dmg: self.name += " KillingHitsOnly"
			else: self.name += " noKills"
		if self.module == 1 and self.module_dmg: self.name += " NotBlocking"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		atkbuff = 0
		resignore = self.talent1_params[0]
		newres = np.fmax(0, res - resignore)
		aspd = 8 if self.module == 1 and self.module_dmg else 0
			
		if self.skill == 1:
			atk_scale = self.skill_params[0]
			hits = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			avghit = (hits * hitdmgarts + skilldmgarts)/(hits + 1)
			if self.skill_dmg:
				avghit = skilldmgarts	
			dps = avghit/(self.atk_interval/((self.attack_speed+aspd)/100))
		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			atk_scale = self.skill_params[3]
			one_target_dmg = np.fmax(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			two_target_dmg = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			dps = one_target_dmg/(self.atk_interval/((self.attack_speed+aspd)/100))
			if self.targets > 1:
				dps = 2 * two_target_dmg/(self.atk_interval/((self.attack_speed+aspd)/100))
		if self.skill in [0,3]:
			atkbuff += self.skill_params[0] * self.skill/3
			maxtargets = self.skill_params[6] if self.skill == 3 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets,maxtargets)
		return dps

class Suzuran(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Suzuran", pp, [1,2,3],[1,2],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		if self.skill == 3: return res * 0
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("SwireAlter",pp,[1,2,3],[1,2,3],3,1,1)
		if not self.talent_dmg and self.elite > 0: self.name += " noStacks"
		elif self.elite > 0: self.name += f" {int(self.talent1_params[3])}Stacks"
		if self.skill_dmg and self.skill == 2: self.name += " 2HitBottles"
		if not self.skill_dmg and self.skill == 1: self.name += " heals>attacks"
		if self.module == 2 and self.talent_dmg: self.name += " maxModStacks"
		if self.skill == 3:
			atk = self.talent1_params[3] * self.talent1_params[2]
			if self.module == 2: atk += 0.2
			final_atk = self.atk * (1+self.buff_atk + atk) + self.buff_atk_flat
			nukedmg = final_atk * 10 * self.skill_params[0] * (1+self.buff_fragile)
			self.name += f" 10Coins:{int(nukedmg)}"

	def skill_dps(self, defense, res):
		atkbuff = 0
		if self.talent_dmg and self.elite > 0:
			atkbuff = self.talent1_params[3] * self.talent1_params[2]
			if self.module == 2: atkbuff += 0.2

		atkcycle = (self.atk_interval/(self.attack_speed/100))
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		if self.skill == 1:
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100))
			if not self.skill_dmg: dps = dps * (3/atkcycle-1) /(3/atkcycle)
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			if self.skill_dmg: skilldmg *= 2
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100))
			dps = dps * (3/atkcycle-1) /(3/atkcycle) + skilldmg / 3
		if self.skill in [0,3]:
			dps = hitdmg/(self.atk_interval/(self.attack_speed/100)) * (1 + self.skill/3)
		return dps

class Tachanka(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tachanka",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 1 and not self.skill_dmg: " outsideBurnZone"
		if self.skill == 1: self.skill_duration = 6
		if self.skill == 1 and self.targets > 1: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		dmg_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 0:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = 2 * hitdmg / self.atk_interval * self.attack_speed /100
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

class Tecno(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tecno",pp,[1,2],[2],2,1,2) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " noSummons"
		else:
			if self.talent_dmg: self.name += f" {int(self.talent1_params[0])}summons"
			else: self.name += " 1summon"
		if self.module == 2 and self.module_lvl > 1: self.drone_atk += 100
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		if self.trait_dmg and self.module == 2 and self.module_lvl == 3: atkbuff += 0.15
		aspd = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1 - res/100), final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		final_drone = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
		drone_hitdmg = np.fmax(final_drone * (1 - res/100), final_drone * 0.05)
		aspd_correction = 4 + self.module_lvl if self.module == 2 else 0
		drone_dps = drone_hitdmg/self.drone_atk_interval * (self.attack_speed + aspd - aspd_correction)/100
		if self.trait_dmg:
			drones = self.talent1_params[0] if self.talent_dmg else 1
			dps += drones * drone_dps
		return dps

class TexasAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("TexasAlter",pp,[1,2,3],[2],2,1,2)
		if self.talent2_dmg and self.elite == 2: self.name += " preKill"
		if self.module == 2 and not self.module_dmg: self.name += " adjacentAlly"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		if self.skill > 1:
			atkbuff = self.talent1_params[0]
			atkbuff += self.skill_params[0] if self.skill == 2 else 0
			if self.module == 2 and self.module_dmg: atkbuff += 0.1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			if self.skill == 2: nukedmg = final_atk * self.skill_params[2] * (1+self.buff_fragile)
			if self.skill == 3: nukedmg = final_atk * 2 * self.skill_params[4] * (1+self.buff_fragile)
			self.name += f" InitialAoe:{int(nukedmg)}"

	def skill_dps(self, defense, res):
		aspd = self.talent2_params[0] if self.elite == 2 and self.talent2_dmg else 0
		atkbuff = self.talent1_params[0] if self.elite > 0 else 0
		atkbuff += self.skill_params[0] if self.skill != 3 else 0
		if self.skill == 0: atkbuff = 0
		if self.module == 2 and not self.module_dmg: atkbuff += 0.1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		
		if self.skill < 2:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			artsdmg = self.skill_params[2] if self.skill == 1 else 0
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100 + np.fmax(artsdmg *(1-res/100), artsdmg * 0.05)
		if self.skill == 2:
			newres = res *(1+self.skill_params[1])
			hitdmgarts = np.fmax(final_atk *(1-newres/100), final_atk * 0.05)
			dps = 2 * hitdmgarts/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 3:
			skillscale = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * skillscale *(1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
			dps += hitdmgarts * min(self.targets, self.skill_params[2])
		return dps
	
class Tequila(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tequila",pp,[1,2],[1],2,6,1)
		if self.skill == 2: self.trait_dmg = self.trait_dmg and self.skill_dmg
		if not self.trait_dmg: self.name += " 20Stacks"   ##### keep the ones that apply
		else: self.name += " 40Stacks"
		if self.skill == 2 and not self.skill_dmg: self.name += " NotCharged"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = 2 if self.trait_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		if self.skill == 0:
			if self.hits == 0 or self.elite == 0: return res * 0
			else:
				dps = self.hits * np.fmax(final_atk * self.talent1_params[0] *(1-res/100), final_atk * self.talent1_params[0] * 0.05)
		if self.skill == 1:
			atk_scale = self.skill_params[1]
			aspd = self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_scale = self.skill_params[0]
			maxtargets = 3 if self.skill_dmg else 2
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets, maxtargets)
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
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Thorns",pp,[1,2,3],[1,3],3,1,1)
		if self.skill == 1 and not self.trait_dmg: self.name += "rangedAtk"   ##### keep the ones that apply
		if self.talent_dmg: self.name += " vsRanged"
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill == 2: self.name += f" {round(self.hits,2)}hits/s"
		if self.skill == 3 and not self.skill_dmg: self.name += " firstActivation"
		if self.module == 3: self.name += " averaged"
		if self.module == 3 and not self.module_dmg: self.name += "(vsBoss)"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe	
			
	def skill_dps(self, defense, res):
		bonus = 0.1 if self.module == 1 else 0
		arts_dot = 0 if self.elite < 2 else max(self.talent1_params)
		if not self.talent_dmg: arts_dot *= 0.5
		stacks = self.talent1_params[3] if self.module == 1 and self.module_lvl > 1 else 1
		arts_dot_dps = np.fmax(arts_dot *(1-res/100) , arts_dot * 0.05) * stacks
		
		if self.skill < 2:
			atk_scale = 1 if self.trait_dmg else 0.8
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0] * self.skill) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg)/self.atk_interval * self.attack_speed/100 + arts_dot_dps
			if self.module == 3:
				time_to_fallout = 1000/(dps*0.1) if self.module_dmg else 2000/(dps*0.1)
				if self.module_lvl == 1: dps += 6000/(time_to_fallout+10)
				else:
					fallout_dps = dps - arts_dot_dps + arts_dot
					dps = (fallout_dps * 10 + dps * time_to_fallout + 6000) / (10 + time_to_fallout)
		if self.skill == 2 and self.hits > 0:
			atk_scale = 0.8
			cooldown = self.skill_params[2]
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			if(1/self.hits < cooldown):
				dps = (hitdmg/cooldown + arts_dot_dps + bonusdmg/cooldown) * min(self.targets,4)
				if self.module == 3:
					time_to_fallout = 1000/(dps*0.1) / min(self.targets,4) if self.module_dmg else 2000/(dps*0.1) / min(self.targets,4)
					if self.module_lvl == 1: dps += 6000/(time_to_fallout+10)
					else:
						fallout_dps = dps - (arts_dot_dps + arts_dot) * min(self.targets,4)
						dps = (fallout_dps * 10 + dps * time_to_fallout + 6000) / (10 + time_to_fallout)
			else:
				cooldown = 1/self.hits
				dps = (hitdmg/cooldown + arts_dot_dps) * min(self.targets,4)
				if self.module == 3:
					time_to_fallout = 1000/(dps*0.1) / min(self.targets,4) if self.module_dmg else 2000/(dps*0.1) / min(self.targets,4)
					if self.module_lvl == 1: dps += 6000/(time_to_fallout+10)
					else:
						fallout_dps = dps - (arts_dot_dps + arts_dot) * min(self.targets,4)
						dps = (fallout_dps * 10 + dps * time_to_fallout + 6000) / (10 + time_to_fallout)
		elif self.skill == 2:
			return defense*0
		if self.skill == 3:
			bufffactor = 2 if self.skill_dmg else 1
			final_atk = self.atk * (1 + self.buff_atk + bufffactor * self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			bonusdmg = np.fmax(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmg + bonusdmg)/self.atk_interval * (self.attack_speed + bufffactor * self.skill_params[1])/100 + arts_dot_dps
			if self.module == 3:
				time_to_fallout = 1000/(dps*0.1) if self.module_dmg else 2000/(dps*0.1)
				if self.module_lvl == 1: dps += 6000/(time_to_fallout+10)
				else:
					fallout_dps = dps - arts_dot_dps + arts_dot
					dps = (fallout_dps * 10 + dps * time_to_fallout + 6000) / (10 + time_to_fallout)		
		return dps

class ThornsAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ThornsAlter",pp,[2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill != 0 and not self.trait_dmg: self.name += " unitOnly"
		if self.skill == 3: self.name += " averaged"
		if self.targets > 1 and self.skill > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = min(self.talent1_params)
		extra_duration = max(self.talent1_params)
		aspd = self.talent2_params[0] if self.elite > 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
		if self.skill != 0 and not self.trait_dmg: dps *= 0

		if self.skill == 2:
			skill_scale = self.skill_params[4]
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps += hitdmgarts * self.targets
		if self.skill == 3:
			duration = self.skill_params[2] + extra_duration
			shred_base = self.skill_params[10]
			shred_step = self.skill_params[12]
			skill_scale_base = self.skill_params[4]
			skill_scale_step = self.skill_params[6]
			dps = res * 0
			for i in range(int(duration)):
				newdef = defense * (1 + shred_base + min(i,15) * shred_step)
				newres = res * (1 + shred_base + min(i,15) * shred_step)
				skill_scale = skill_scale_base + skill_scale_step * min(i,15)
				dps += np.fmax(final_atk * skill_scale * (1-newres/100), final_atk * skill_scale * 0.05) * self.targets
				if self.trait_dmg: dps += np.fmax(final_atk - newdef, final_atk * 0.05) / self.atk_interval * (self.attack_speed + aspd) / 100
			dps = dps / duration
		return dps

class TinMan(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("TinMan",pp,[1,2],[1],1,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2: self.name += " 1UnitActive"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		dmg_bonus = self.talent2_params[0] if self.elite == 2 else 1

		duration = self.skill_params[0]
		skill_scale = self.skill_params[2]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_bonus * self.targets
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		if self.skill == 0: return hitdmg/self.atk_interval * self.attack_speed/100
		
		if self.skill == 1:
			sp_cost = self.skill_cost
			dps = sp_cost/(sp_cost + 1) * hitdmg / self.atk_interval * (self.attack_speed) / 100
			dps += duration * skilldmg / ((sp_cost + 1) * self.atk_interval/self.attack_speed*100)
		if self.skill == 2:
			dps = hitdmg / self.atk_interval * (self.attack_speed) / 100
			dps += skilldmg
		return dps

class Tippi(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tippi",pp,[1,2],[],2,6,0) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		hits = 3 if self.skill == 2 else 1
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05) * hits
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class Toddifons(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Toddifons",pp,[1,2],[1],2,1,1)
		if self.talent_dmg and self.elite > 0: self.name += " withRacism"
		if self.module_dmg and self.module == 1: self.name += " vsHeavy"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
			
	def skill_dps(self, defense, res):
		atk_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		if self.module == 1 and self.module_dmg: atk_scale *= 1.15
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 0:
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			newdef = defense * (1 + self.skill_params[1])
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			skill_scale2 = self.skill_params[2]
			hitdmg = np.fmax(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmg2 = np.fmax(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05) * self.targets
			dps = (hitdmg+hitdmg2)/3.12 * self.attack_speed/100
		return dps

class TogawaSakiko(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("TogawaSakiko",pp,[1,2,3],[2],3,1,2) #available skills, available modules, default skill, def pot, def mod
		#if not self.trait_dmg: self.name += " rangedAtk"
		if self.skill == 1 and self.skill_dmg: self.name += " maxSkillDmg"
		if self.skill == 2:
			if self.skill_dmg: self.name += " Organ"
			else: self.name += " Piano"
		if self.talent_dmg and self.elite > 0: self.name += " maxNotes"
		if not self.talent_dmg and self.elite > 0: self.name += " minNotes"
		if self.talent2_dmg and self.skill in [1,2]: self.name += " fever"
		if self.module == 2 and self.module_dmg: self.name += " vs2+Enemy"
		
		if self.targets > 1 and self.skill == 2 and not self.skill_dmg: self.name += f" {self.targets}targets" ######when op has aoe
		try:
			self.shreds = kwargs['shreds']
		except KeyError:
			self.shreds = [1,0,1,0]
	
	def skill_dps(self, defense, res):
		atk_scale = 1 #if self.trait_dmg else 0.8
		atkbuff = self.skill_params[1] if self.skill == 2 and not self.skill_dmg else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		aspd = self.talent2_params[1]
		aspd += 12 if self.module == 2 and self.module_dmg else 0
		resshred = 0
		defshred = 0
		if self.talent_dmg:
			resshred = self.talent1_params[4] * self.talent1_params[1] if self.module == 2 and self.module_lvl > 1 else self.talent1_params[4] * self.talent1_params[2]
			defshred = self.talent1_params[4] * self.talent1_params[0] if self.module == 2 and self.module_lvl > 1 else self.talent1_params[4] * self.talent1_params[1]
		if self.shreds[2] < 1 and self.shreds[2] > 0:
			res = res / self.shreds[0]
		newres = res * (1-resshred)
		if self.shreds[0] < 1 and self.shreds[0] > 0:
			defense = defense / self.shreds[0]
		newdef = defense * (1-defshred)

		if self.skill == 1:
			skill_scale = self.skill_params[0] if self.skill_dmg else self.skill_params[7]
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			skill_dmg = np.fmax(final_atk * skill_scale * (1-newres/100), final_atk * skill_scale * 0.05) * 8
			dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100
			dps += skill_dmg / self.atk_interval * (self.attack_speed + aspd) / 100 / self.skill_cost
			if self.talent2_dmg:
				dps = skill_dmg / self.atk_interval * (self.attack_speed + aspd) / 100
		
		if self.skill == 2:
			hits = 2 if self.talent2_dmg else 1
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05) * hits
			hitdmgarts = np.fmax(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05) * hits
			if self.skill_dmg:
				dps = hitdmgarts / self.atk_interval * (self.attack_speed + aspd + self.skill_params[0]) / 100
			else:
				dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * self.targets
		
		if self.skill == 3:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = 2*(hitdmg+hitdmgarts) / self.atk_interval * (self.attack_speed + aspd) / 100 

		return dps

class Tomimi(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tomimi", pp, [1,2], [2],2,6,2)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
				
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] if self.skill > 0 else 0
		final_atk = self.atk * (1+atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		if self.skill == 0:
			hitdmg = np.fmax(final_atk * (1 - res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
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
		atkbuff = self.talent1_params[0] if self.talent_dmg  else 0
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
			
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = np.fmax(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * min(self.targets,2)
			if self.skill == 0: skillhitdmg = hitdmg
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
	
class Tragodia(Operator): #todo: correct aoe dps
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Tragodia",pp,[1,2,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if not self.trait_dmg: self.name += " vsBoss"
		elif self.module == 1:
			if self.module_dmg: self.name += " vsElite"
			else: self.name += " vsMob"
		if self.skill == 2 and not self.skill_dmg: self.name += " onlyCat"
	
	def skill_dps(self, defense, res):
		nerv_factor = self.talent1_params[0]
		nerv_aoe = self.talent1_params[1]
		mod_factor = 1.18 if self.module == 1 and (not self.trait_dmg or self.module_dmg) else 1
		ele_gauge = 1000 if self.trait_dmg else 2000
		atkbuff = self.skill_params[0] if self.skill == 3 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)

		if self.skill == 0:
			ele_dps = 6000/(10 + (ele_gauge / (final_atk * nerv_factor * mod_factor / self.atk_interval * self.attack_speed / 100)))
			dps = hitdmg / self.atk_interval * self.attack_speed / 100 + ele_dps
		
		if self.skill == 1:
			skilldmg = np.fmax(final_atk * self.skill_params[0] * (1-res/100), final_atk * self.skill_params[0] * 0.05) * 2
			nerv_dps = (final_atk * nerv_factor * mod_factor * self.skill_cost + 2 * final_atk * nerv_factor * mod_factor * self.skill_params[1])/(self.skill_cost+1)/ self.atk_interval * self.attack_speed  / 100
			ele_dps = 6000/(10+ele_gauge/nerv_dps)
			dps = (skilldmg + hitdmg * self.skill_cost)/(self.skill_cost+1)/ self.atk_interval * self.attack_speed / 100 + ele_dps
		
		if self.skill == 2:
			skill_factor = self.skill_params[0]
			artsdmg = np.fmax(final_atk * skill_factor * (1-res/100), final_atk * skill_factor * 0.05)
			dps = 12 * artsdmg / 25

			if self.skill_dmg:
				ele_dps = 6000/(10 + (ele_gauge / (final_atk * nerv_factor * mod_factor / self.atk_interval * (self.attack_speed+self.skill_params[7]) / 100)))
				dps += hitdmg / self.atk_interval * (self.attack_speed+self.skill_params[7]) / 100 + ele_dps
			else:
				if 12 * 0.25 * final_atk * mod_factor < ele_gauge:
					dps += 3000 / 25
				else:
					dps += 6000 / 25

		if self.skill == 3:
			ele_dps = 6000/(6.666 + (ele_gauge / (final_atk * nerv_factor * mod_factor / self.atk_interval * self.attack_speed / 100 + final_atk * 0.1 * mod_factor)))
			dps = hitdmg / self.atk_interval * self.attack_speed / 100 + ele_dps
		return dps

class Typhon(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Typhon",pp,[1,2,3],[1,2],3,1,1)
		self.try_kwargs(2,["crit","crits","nocrit","nocrits"],**kwargs)
		self.try_kwargs(5,["heavy","vsheavy","vs","light","vslight"],**kwargs)
		self.talent2_dmg = self.talent2_dmg and self.talent_dmg
		if self.elite == 2:
			if not self.talent2_dmg: self.name += " noCrits"
			else:
				if self.skill == 3 and self.module == 2 and self.module_lvl > 1: self.name += " 2Crits/salvo"
				elif self.skill == 3: self.name += " 1Crit/salvo"
				elif self.skill == 2:
					if self.targets == 1 and not (self.module == 2 and self.module_lvl > 1): self.name += " 1/2Crits"
					else: self.name += " allCrits"
				else: self.name += " allCrits"
		if self.module_dmg and self.module == 1: self.name += " vsHeavy"
		if self.module_dmg and self.module == 2: self.name += " maxRange"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
				
	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		if self.module == 2 and self.module_dmg: atk_scale = 1.12
		crit_scale = self.talent2_params[0] if self.talent2_dmg and self.elite == 2 else 1
		def_ignore = 0 if self.elite == 0 else 5 * self.talent1_params[1]

		if self.skill < 2:
			atkbuff = self.skill_params[0] * self.skill
			aspd = self.skill_params[1] * self.skill
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat	
			hitdmg = np.fmax(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)		
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense*(1-def_ignore), final_atk * atk_scale * 0.05)
			critdmg = np.fmax(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)
			if self.targets == 1 and self.module != 2: dps = (hitdmg+critdmg)/self.atk_interval * self.attack_speed/100
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
			if self.talent2_dmg and self.module == 2 and self.module_lvl > 1:
				totaldmg = (hits-2)*hitdmg + 2*critdmg
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
			
		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
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

class Underflow(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Underflow",pp,[1,2],[1],2,6,1)
		if self.talent_dmg and self.elite > 0: self.name += " vsSeaborn"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill > 0 else 0
		aspd = self.skill_params[3] if self.skill == 2 else 0
		targets = self.skill_params[4] if self.skill == 2 else 1
		arts_dmg = self.talent1_params[2] if self.elite > 0 else 0
		if self.talent_dmg: arts_dmg *= 2
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * (self.attack_speed + aspd) / 100 * min(self.targets,targets)
		dps += np.fmax(arts_dmg * (1 - res/100), arts_dmg * 0.05) * min(self.targets,targets)
		return dps

class Utage(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Utage",pp,[1,2],[1],2,6,1)
		if self.skill != 1:
			if self.talent_dmg: self.name += " lowHP"
			else: self.name += " fullHP"

	def skill_dps(self, defense, res):
		if self.skill == 1: return 0 * res
		aspd = self.talent1_params[0] if self.talent_dmg else 0
		atkbuff = 0.01 + 0.01 * self.module_lvl if self.module == 1 and self.module_lvl > 1 and self.talent_dmg else 0
		if self.skill == 0:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk = self.atk * (1 + atkbuff + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * (self.attack_speed+aspd)/100
		return dps

class Vanilla(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vanilla",pp,[1],[],1,6,0)
	
	def skill_dps(self, defense, res):
		atkbuff = self.talent1_params[0] + self.skill_params[1] * self.skill
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class Vendela(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vendela", pp, [1,2],[1],2,1,1)
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill < 2: self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[2] if self.skill == 2 else 0
		aspd = self.skill_params[0] if self.skill == 1 else 0
		final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		if self.hits > 0 and self.skill == 2:
			arts_scale = self.skill_params[0]
			artsdmg = np.fmax(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05)
			dps += artsdmg * self.hits	
		return dps

class Vermeil(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vermeil",pp,[1,2,],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.module == 1 and self.module_dmg: self.name += " vsAerial"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.skill_params[0] * min(self.skill,1) + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2 and self.targets > 1: dps *= 2
		return dps

class Vetochki(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vetochki",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg / self.atk_interval * self.attack_speed / 100
		if self.skill == 2: dps *= min(3, self.targets)
		return dps

class Vigil(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vigil",pp,[1,2,3],[1,2],3,6,2)
		if self.talent_dmg:
			if self.trait_dmg: self.name += " vsBlocked"
			if not self.skill_dmg: self.name += " 1wolf"
		else:
			self.name += " noWolves"

	def skill_dps(self, defense, res):
		atk_scale = 1
		defignore = 0
		wolves = 0
		if self.talent_dmg:
			wolves = 3 if self.skill_dmg  else 1
			if self.trait_dmg:
				atk_scale = 1.65 if self.module == 2 else 1.5 
				defignore = self.talent2_params[0] if self.elite == 2 else 0
		newdef = np.fmax(0, defense - defignore)
		wolfdef = np.fmax(0, defense - self.talent2_params[0]) if self.elite == 2 else defense
		####the actual skills
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_wolf  = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill < 2:
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = np.fmax(final_wolf - wolfdef, final_wolf * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.talent_dmg: dps += hitdmgwolf/self.drone_atk_interval * self.attack_speed/100 * wolves

		if self.skill == 2:
			skill_scale = self.skill_params[1]
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2 #lockout
			
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = np.fmax(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgwolfskill = np.fmax(final_wolf * skill_scale - wolfdef, final_wolf * skill_scale * 0.05)
			atkcycle = self.drone_atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = hitdmgwolfskill
			if atks_per_skillactivation > 1:
				avghit = (hitdmgwolfskill + (atks_per_skillactivation - 1) * hitdmgwolf) / atks_per_skillactivation						
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.talent_dmg: dps += avghit/self.drone_atk_interval * self.attack_speed/100 * wolves
			
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			final_wolf  = self.drone_atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = np.fmax(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * 0.05)
			hitdps = 3 * hitdmg/self.atk_interval * self.attack_speed/100
			artdps = 0
			if self.talent_dmg:
				hitdps += wolves * hitdmgwolf/self.drone_atk_interval * self.attack_speed/100
				artdps = wolves * hitdmgarts/self.drone_atk_interval * self.attack_speed/100
				if self.trait_dmg:
					artdps += 3 * hitdmgarts/self.atk_interval * self.attack_speed/100
			dps = hitdps + artdps
			
		return dps

class Vigna(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vigna",pp,[1,2],[2],2,6,2)
		if self.module_dmg and self.module == 2: self.name += " vsLowHp"
			
	def skill_dps(self, defense, res):
		crate = 0 if self.elite == 0 else self.talent1_params[2]
		if self.skill == 0 and self.elite > 0: crate = self.talent1_params[1]
		cdmg = self.talent1_params[0]
		atkbuff = self.skill_params[0] * min(self.skill, 1)
		atk_interval = 1.5 if self.skill == 2 else self.atk_interval
		atk_scale = 1.1 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		final_atk_crit = self.atk * (1 + atkbuff + self.buff_atk + cdmg) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		critdmg = np.fmax(final_atk_crit * atk_scale - defense, final_atk_crit * atk_scale * 0.05)
		avgdmg = crate * critdmg + (1-crate) * hitdmg
		dps = avgdmg / atk_interval * self.attack_speed/100
		return dps

class Vina(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("VinaVictoria", pp, [1,2,3],[1,2],3,1,1)
		if self.talent_dmg:
			self.count = 8 if self.skill == 3 else 3
		else:
			self.count = 4 if self.skill == 3 else 0
		if self.elite > 0: self.name += f" {self.count}Allies"
		if self.module == 1 and self.module_dmg: self.name += " NotBlocking"
		if self.module == 2 and self.module_lvl > 1 and self.talent2_dmg: self.name += " vsFrighten"
		if self.module == 2 and self.module_dmg: self.name += " blocking"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe	
	
	def skill_dps(self, defense, res):
		value = 0.1 if self.module == 2 and self.module_dmg else 0
		fragile = max(value, self.buff_fragile)
		dmg_scale = 1 + 0.05 * self.module_lvl if self.module == 2 and self.module_lvl > 1 and self.talent2_dmg else 1
		atkbuff = self.talent1_params[1] * self.count
		aspd = 8 if self.module == 1 and self.module_dmg else 0	
		if self.skill < 2:
			skill_scale = self.skill_params[0]
			hits = self.skill_cost
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 0.05)
			skilldmgarts = np.fmax(final_atk * skill_scale *(1-res/100), final_atk * skill_scale * 1)
			if self.skill == 0: skilldmgarts = hitdmgarts
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts
			if atks_per_skillactivation > 1:
				avghit = (skilldmgarts + int(atks_per_skillactivation) * hitdmgarts) / (int(atks_per_skillactivation)+1)
			dps = avghit/(self.atk_interval/((self.attack_speed+aspd)/100))

		if self.skill == 2:
			atkbuff += self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets,2)
		if self.skill == 3:
			atk_interval = self.atk_interval + self.skill_params[0]
			atkbuff += self.skill_params[1]
			maxtargets = self.skill_params[2]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk *(1-res/100), final_atk * 1)
			hitdmg_lion = np.fmax(self.drone_atk *(1-res/100), self.drone_atk * 1)
			dps = hitdmgarts/(atk_interval/((self.attack_speed+aspd)/100)) * min(self.targets,maxtargets) + hitdmg_lion/self.drone_atk_interval * min(self.targets, self.count)
		return dps * dmg_scale * (1+fragile)/(1+self.buff_fragile)

class Virtuosa(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Virtuosa",pp,[1,2,3],[1,2],3,1,1)
		if not self.trait_dmg: self.name += " vsBoss"
		if self.skill == 3 and self.skill_dmg: self.name += " selfBuff"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		ele_gauge = 1000 if self.trait_dmg else 2000
		necro_scale = self.talent1_params[0]
		necro_fragile = max(self.talent2_params) if self.elite == 2 else 1
		ele_fragile = self.talent2_params[0] if self.module == 1 and self.module_lvl > 1 else 1
		if self.module == 2: ele_fragile = 1.1
		falloutdmg = 12000
		if self.module == 2 and self.module_lvl > 1: falloutdmg = 15 * (800 + 50 * self.module_lvl)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			necro_skill_scale = self.skill_params[1]
			sp_cost = self.skill_cost / (1 + self.sp_boost) + 1.2
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg =np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if skill_scale > 2.05:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/(self.atk_interval/(self.attack_speed/100))
			necro_dps = final_atk * necro_scale * necro_fragile
			necro_skill_dps = final_atk * necro_skill_scale * necro_fragile / sp_cost
			time_to_fallout_1 = ele_gauge / (necro_dps + necro_skill_dps) #this is meant as a rough estimate to her saving skill charges against fallout, potentially improving dps
			time_to_fallout = ele_gauge / (necro_dps + necro_skill_dps/(time_to_fallout_1)*(time_to_fallout_1 + 15))
			if skill_scale < 2.05: time_to_fallout = time_to_fallout_1
			dps += falloutdmg * ele_fragile / (15 + time_to_fallout) / (1 + self.buff_fragile)
			if self.targets > 1:
				dps += falloutdmg * ele_fragile / (15 + ele_gauge/necro_dps) / (1 + self.buff_fragile) * (self.targets -1)
		
		if self.skill == 2:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			extra_ele = final_atk * self.skill_params[1]
			ele_gauge = ele_gauge / necro_fragile
			eleApplicationTarget = final_atk * necro_scale + extra_ele / (self.atk_interval/((self.attack_speed+aspd)/100))
			eleApplicationBase = final_atk * necro_scale
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			artsdps = hitdmgarts/(self.atk_interval/((self.attack_speed+aspd)/100))
			targetEledps = falloutdmg * ele_fragile / (15 + ele_gauge/eleApplicationTarget)
			ambientEledps = falloutdmg * ele_fragile / (15 + ele_gauge/eleApplicationBase)
			dps = np.fmin(self.targets, 2) * (artsdps + targetEledps/(1 + self.buff_fragile))
			if self.targets > 2:
				dps += ambientEledps * (self.targets - 2) / (1 + self.buff_fragile)			
			
		if self.skill in [0,3]:
			if self.skill == 3: necro_fragile = self.skill_params[1] * (necro_fragile - 1) + 1
			atkbuff = self.skill_params[0]
			atkbuff += self.skill_params[3] if self.skill_dmg else 0
			if self.skill == 0: atkbuff = 0
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			necro_dps = final_atk * necro_scale * necro_fragile
			time_to_fallout = ele_gauge / necro_dps
			dps = self.targets * 12000 * ele_fragile / (15 + time_to_fallout) * np.fmax(1,-defense) / (1 + self.buff_fragile)
			if self.skill == 0:
				hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
				dps += hitdmgarts/(self.atk_interval/(self.attack_speed/100))	
		return dps
	
class Viviana(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Viviana",pp,[1,2,3],[3],3,1,3)
		if self.module == 3 and self.module_lvl > 1 and self.module_dmg and not self.talent2_dmg: self.talent_dmg = True #basically: a boss is always an elite
		if self.talent_dmg and self.elite > 0: self.name += " vsElite"
		if self.module == 3 and self.module_lvl > 1 and self.module_dmg and not self.talent2_dmg: self.name += "(boss)"
		if self.skill_dmg and self.skill == 2: self.name += " afterSteal"
		if not self.skill_dmg and self.skill == 3: self.name += " 1stActivation"
		if self.skill_dmg and self.skill == 3: self.skill_duration = 25
		if self.module == 3:
			if self.module_dmg and self.module_lvl > 1: 
				self.name += " avgBurn"
			else: self.name += " noBurn"
				
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		dmg_scale = 1 + self.talent1_params[1] * 2 if self.talent_dmg else 1 + self.talent1_params[1]
		if self.elite == 0: dmg_scale = 1
		burn_res = np.fmax(0,res-20)
		fallout_dmg = 7000
		ele_scale = 0.15
		ele_appli = self.talent1_params[0] if self.module == 3 and self.module_lvl > 1 else 0
		if self.talent_dmg: ele_appli *= 2
		ele_gauge = 1000
		if not self.talent2_dmg: ele_gauge = 2000

		if self.skill < 2:
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2 #sp lockout
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg_scale * 2
			hitdmgarts2 = np.fmax(final_atk * (1-burn_res/100), final_atk * 0.05) * dmg_scale
			skilldmg2 = np.fmax(final_atk * skill_scale * (1-burn_res/100), final_atk * skill_scale * 0.05) * dmg_scale * 2
			if self.skill == 0: 
				skilldmg = hitdmgarts
				skilldmg2 = hitdmgarts2
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			avghit2 = skilldmg2
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmgarts) / (int(atks_per_skillactivation)+1)
				avghit2 = (skilldmg2 + int(atks_per_skillactivation) * hitdmgarts2) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval * self.attack_speed/100
			if self.module == 3 and self.module_dmg and self.module_lvl > 1:
				time_to_trigger = ele_gauge / (dps*ele_appli)
				fallout_dps = (avghit2 + ele_scale * final_atk)/self.atk_interval * self.attack_speed/100
				dps = (dps * time_to_trigger + fallout_dps * 10 + fallout_dmg) / (time_to_trigger + 10)

		if self.skill == 2:
			atkbuff = self.skill_params[0]
			aspd = self.skill_params[6] if self.skill_dmg else 0
			crate = 0.2
			cdmg = self.skill_params[3]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			skilldmg = 2 * np.fmax(final_atk * cdmg * (1-res/100), final_atk * cdmg * 0.05) * dmg_scale
			avgdmg = crate * skilldmg + (1-crate) * hitdmgarts
			hitdmgarts2 = np.fmax(final_atk * (1-burn_res/100), final_atk * 0.05) * dmg_scale
			skilldmg2 = 2 * np.fmax(final_atk * cdmg * (1-burn_res/100), final_atk * cdmg * 0.05) * dmg_scale
			avgdmg2 = crate * skilldmg2 + (1-crate) * hitdmgarts2
			dps = avgdmg/self.atk_interval * (self.attack_speed+aspd)/100 * min(self.targets,2)
			if self.module == 3 and self.module_dmg and self.module_lvl > 1:
				time_to_trigger = ele_gauge / (dps*ele_appli/min(self.targets,2))
				fallout_dps = (avgdmg2 + ele_scale * final_atk)/self.atk_interval * (self.attack_speed+aspd)/100
				dps = (dps * time_to_trigger + fallout_dps * 10 + fallout_dmg) / (time_to_trigger + 10)
		if self.skill == 3:
			atkbuff = self.skill_params[1]
			hits = 3 if self.skill_dmg else 2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			hitdmgarts2 = np.fmax(final_atk * (1-burn_res/100), final_atk * 0.05) * dmg_scale
			dps = hits * hitdmgarts/1.75 * self.attack_speed/100
			if self.module == 3 and self.module_dmg and self.module_lvl > 1:
				time_to_trigger = ele_gauge / (dps*ele_appli)
				fallout_dps = hits * (hitdmgarts2 + ele_scale * final_atk)/1.75 * self.attack_speed/100
				dps = (dps * time_to_trigger + fallout_dps * 10 + fallout_dmg) / (time_to_trigger + 10)
		return dps

class Vulcan(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vulcan",pp,[1,2],[1],2,1,1)
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets"
	
	def skill_dps(self, defense, res):
		atkbuff = self.skill_params[0] if self.skill == 2 else 0
		targets = 2 if self.skill == 2 else 1
		atk_interval = 2 if self.skill == 2 else self.atk_interval
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/self.atk_interval * self.attack_speed/100 * min(self.targets,targets)
		return dps

class Vulpisfoglia(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Vulpisfoglia",pp,[1,3],[1],3,1,1) #available skills, available modules, default skill, def pot, def mod
		if self.elite > 0 and not self.talent_dmg: self.name += " w/o Talent1"
		if self.skill == 3: self.name += " averaged"
		if self.module == 1 and self.module_dmg: self.name += " blocking"
		
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		#6, 3, 7, 5, 5, 2 are skill 2 params
		arts_scale = self.talent1_params[0] if self.elite > 0 and self.talent_dmg else 0

		if self.skill < 2:
			skill_scale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff+ self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk  - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			if self.skill == 0: skilldmg = hitdmg
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = (avghit+hitdmgarts)/self.atk_interval*(self.attack_speed)/100 * self.targets
		if self.skill == 3:
			atkbuff += self.skill_params[1]
			aspd = self.skill_params[2] / 2
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat

			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05)

			dps = (hitdmg+hitdmgarts) / self.atk_interval * (self.attack_speed + aspd) / 100 * min(self.targets,2)

		return dps

class W(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("W",pp,[1,2,3],[1,2],2,1,2)
		if self.elite == 2 and self.talent2_dmg: self.name += " vsStun"
		if self.talent_dmg and self.module == 2 and self.module_lvl > 1: self.name += " noDmgTaken"
		if self.module_dmg and self.module == 1: self.name += " vsBlocked"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atk_scale = 1.1 if self.module == 1 and self.module_dmg else 1
		newdef = defense if self.module != 2 else np.fmax(0, defense - 100)
		atkbuff = 0.1 * (self.module_lvl - 1) if self.module == 2 and self.talent2_dmg else 0
		
		stundmg = self.talent2_params[0] if self.elite == 2 else 1 
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		hitdmg = np.fmax(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
		if self.talent2_dmg: hitdmg *= stundmg
		
		if self.skill < 2:
			skill_scale = self.skill_params[0] * self.skill
			sp_cost = self.skill_cost / (1 + self.sp_boost) + 1.2 #sp lockout
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05) * stundmg
			dps = (hitdmg/(self.atk_interval/(self.attack_speed/100)) + skilldmg / sp_cost) * self.targets
			
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost / (1 + self.sp_boost) + 2 #lockout
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk* atk_scale * skill_scale * 0.05) * (1+stundmg)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation) + 1)
			dps = avghit/(self.atk_interval/(self.attack_speed/100)) * self.targets
		
		if self.skill == 3:
			skill_scale = self.skill_params[1]
			targets = self.skill_params[0]
			sp_cost = self.skill_cost / (1+ self.sp_boost) + 1.2 #sp lockout
			skilldmg = np.fmax(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			dps = (hitdmg/(self.atk_interval/(self.attack_speed/100)) + skilldmg * min(targets, self.targets) / sp_cost) * self.targets
		
		return dps

class WakabaMutsumi(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("WakabaMutsumi",pp,[1,2],[2],2,1,2) #available skills, available modules, default skill, def pot, def mod
	
	def skill_dps(self, defense, res):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 2:
			skill_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = 3 * hitdmg / (self.atk_interval+self.skill_params[0]) * self.attack_speed / 100
		else:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100
		return dps

class Walter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Wisadel",pp,[1,2,3],[1],3,1,1)
		self.shadows = 0
		if self.elite == 2:
			if self.skill in [0,3]:
				if self.talent2_dmg:
					self.shadows = 3
				else:
					self.shadows = min(self.skill +1,2)
				if self.skill_params[1] == 1 and self.skill == 3:
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
	
		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg_main = np.fmax(final_atk * maintargetscale - defense, final_atk * maintargetscale * 0.05)
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			explosiondmg = np.fmax(final_atk * explosionscale - defense, final_atk * explosionscale * 0.05)
			avghit = hitdmg_main + hitdmg + explosiondmg * prob
			dps = avghit / self.atk_interval * self.attack_speed/100 * self.targets
		if self.skill == 1:
			prob2 = 1 - 0.85 ** (bonushits+2)
			skill_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			
			hitdmg_main = np.fmax(final_atk * maintargetscale - defense, final_atk * maintargetscale * 0.05)
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			bonushitdmg_main = np.fmax(final_atk * maintargetscale * 0.5 - defense, final_atk * maintargetscale * 0.5 * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - defense, final_atk  * 0.5 * 0.05)
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
			atkbuff = self.skill_params[0]
			skill_scale = self.skill_params[3]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg_main = np.fmax(final_atk * maintargetscale * skill_scale - defense, final_atk * maintargetscale * skill_scale * 0.05)
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			bonushitdmg_main = np.fmax(final_atk * maintargetscale * skill_scale * 0.5 - defense, final_atk * skill_scale * maintargetscale * 0.5 * 0.05)
			bonushitdmg = np.fmax(final_atk * 0.5 - defense, final_atk * 0.5 * 0.05)
			explosiondmg = np.fmax(final_atk * explosionscale - defense, final_atk * explosionscale * 0.05)
			dps = (hitdmg_main + bonushitdmg_main * bonushits + explosiondmg)/5 * self.attack_speed/100
			if self.targets > 1:
				dps += (hitdmg + bonushitdmg * bonushits + explosiondmg)/self.atk_interval * self.attack_speed/100 * (self.targets-1)
		
		shadowhit = np.fmax(self.drone_atk * (1-res/100), self.drone_atk * 0.05) * self.shadows
		dps += shadowhit/4.25
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * 6 * (5/(self.attack_speed/100)))
		else:
			return(super().total_dmg(defense,res))

class Warmy(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Warmy",pp,[1,2],[1],2,1,1)
		if self.skill == 1:
			if not self.trait_dmg: self.name += " no Burn"
			else:
				if self.skill_dmg: self.name += " avgBurn"
				else: self.name += " avgBurn vsBoss"
		if self.skill == 2 and self.skill_dmg: self.name += " vsBurn"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		if self.elite > 0:
			atkbuff = self.skill_params[0] if self.skill == 2 else 0
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			burn_bonus = final_atk * self.talent1_params[0]
			self.name += f" extraFalloutDmg:{int(burn_bonus)}"

	def skill_dps(self, defense, res):
		falloutdmg = 7000
		burst_scale = 1.1 if ((self.skill == 2 and self.skill_dmg) or (self.skill == 1 and self.trait_dmg)) and self.module == 1 else 1
		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
		if self.skill == 1:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			if self.elite > 0: falloutdmg += self.talent1_params[0] * final_atk
			newres = np.fmax(0,res-20)
			elegauge = 1000 if self.skill_dmg else 2000
			hitdmg1 = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
			dpsNorm = hitdmg1/self.atk_interval * (self.attack_speed+aspd)/100
			dpsFallout = hitdmg2/self.atk_interval * (self.attack_speed+aspd)/100
			timeToFallout = elegauge/(dpsNorm * 0.15)
			dps = (dpsNorm * timeToFallout + dpsFallout * burst_scale * 10 + falloutdmg)/(timeToFallout + 10)
			if not self.trait_dmg: dps = dpsNorm
			
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmgarts = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgele = final_atk * 0.5
			hitdmg = hitdmgarts + hitdmgele if self.skill_dmg else hitdmgarts
			dps = hitdmg* burst_scale/2.5 * self.attack_speed/100 * min(self.targets,3)
		return dps

class Weedy(Operator): #TODO add weight prompt and actually calc the dmg for s3
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Weedy",pp,[1,2],[1,2],2,1,1)
		if self.talent_dmg and self.elite > 0 and not (self.module == 1 and self.module_dmg and self.module_lvl > 1): self.name += " +cannon"
		if self.module == 1 and self.module_dmg and self.module_lvl > 1 and self.talent_dmg: self.name += " nextToCannon"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		atkbuff = 0
		if self.module == 1 and self.module_dmg:
			if self.module_lvl == 2: atkbuff += 0.15
			if self.module_lvl == 3: atkbuff += 0.2

		if self.skill < 2:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			sp_cost = self.skill_cost/(1+ self.sp_boost) + 1.2
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/(self.atk_interval/(self.attack_speed/100)) * self.targets

		if self.skill == 2:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(3.84/(self.attack_speed/100)) * min(self.targets, 2)

		if self.talent_dmg and self.elite > 0:
			summonhit = np.fmax(self.drone_atk - defense, self.drone_atk * 0.05)
			dps += summonhit / self.drone_atk_interval

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
		aspd = talent_buff * self.skill_params[0] if self.skill == 2 else 0.5 * talent_buff * self.skill_params[0] * self.skill
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

class Windscoot(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Windscoot",pp,[1,2],[1],2,6,1)
		if not self.trait_dmg or not self.talent_dmg: self.name += " halfStacks"   ##### keep the ones that apply
		else: self.name += " maxStacks"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		atkbuff = 2 if self.trait_dmg else 1
		final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
		extrahit = np.fmax(final_atk * self.talent1_params[0] - defense, final_atk * 0.05) if self.elite > 0 and self.trait_dmg and self.talent_dmg else 0
		if self.skill == 0:
			return res * 0

		if self.skill == 1:
			aspd = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = (hitdmg+extrahit)/self.atk_interval * (self.attack_speed+aspd)/100
		if self.skill == 2:
			atk_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = (hitdmg+extrahit)/self.atk_interval * self.attack_speed/100 * min(self.targets, 2)
		return dps

class YahataUmiri(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("YahataUmiri",pp,[1,2,3],[2],1,6,2) #available skills, available modules, default skill, def pot, def mod
		if self.talent_dmg: self.name += " vsSlow" 
		if self.skill == 1 and self.skill_dmg: self.name += " Fever"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
	
	def skill_dps(self, defense, res):
		dmg = self.talent2_params[0] if self.talent_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill == 0:
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			dps = hitdmg / self.atk_interval * self.attack_speed / 100 * self.targets
		
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skillhit = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * 5
			if self.skill_dmg: # Fever
				dps = skillhit / self.atk_interval * self.attack_speed / 100 * self.targets
			else:
				dpsnorm = hitdmg / self.atk_interval * self.attack_speed / 100
				dpsskill = skillhit / 2.1
				interval = self.atk_interval / self.attack_speed * 100
				dps = (dpsnorm * self.skill_cost * interval + dpsskill * 2.1)/(self.skill_cost * interval + 2.1) * self.targets
		
		if self.skill == 2:
			skill_scale = self.skill_params[0]
			dps = np.fmax(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * self.targets

		return dps * dmg

class YatoAlter(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("YatoAlter",pp,[1,2,3],[1],1,1,1)
		if self.skill == 0 and self.elite == 2 and not self.talent2_dmg: self.name += " after10s"
		if self.skill == 2: self.name += " totalDMG"
		if self.skill == 3: self.name += " dmgPerHit"
		if self.targets > 1 and self.skill != 1: self.name += f" {self.targets}targets" ######when op has aoe

	def skill_dps(self, defense, res):
		extra_arts = self.talent1_params[0]
		atkbuff = self.talent2_params[0] if self.elite == 2 and (self.skill != 0 or self.talent2_dmg) else 0
		try: atkbuff += self.talent2_params[2]
		except: pass
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat

		if self.skill < 2:
			aspd = self.skill_params[0]
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmgarts = np.fmax(final_atk * extra_arts * (1-res/100), final_atk * extra_arts * 0.05)
			dps = (hitdmg+hitdmgarts)/self.atk_interval * (self.attack_speed+aspd*self.skill)/100 
			if self.skill == 1: dps *= 10 / 3 
		if self.skill == 2:
			extra_arts *= self.skill_params[3]
			atk_scale = self.skill_params[1]
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * atk_scale * extra_arts * (1-res/100), final_atk * atk_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts) * self.targets * 16
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			hitdmg = np.fmax(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			hitdmgarts = np.fmax(final_atk * skill_scale * extra_arts * (1-res/100), final_atk * skill_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts) * self.targets
		return dps

class Yu(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("Yu",pp,[2],[],2,1,0)
		if self.talent_dmg and self.elite > 0: 
			self.name += " blocking"
			if not self.trait_dmg: self.name += " vsBoss"
		
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.elite < 2: self.hits = 0
		if self.hits > 0 and self.skill == 1: self.name += f" {round(self.hits,2)}hits/s"

	def skill_dps(self, defense, res):
		newres = np.fmax(0,res-20)
		atkbuff = self.skill_params[1] if self.skill == 2 else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		dps = 0
		time_to_fallout = -1
		if self.talent_dmg and self.elite > 0:
			arts_scale = self.talent1_params[1]
			ele_scale = self.talent1_params[2]
			block = 5 if self.skill == 2 else 3
			artsdmg1 = np.fmax(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05) * min(self.targets,block)
			artsdmg2 = np.fmax(final_atk * arts_scale * (1-newres/100), final_atk * arts_scale * 0.05) * min(self.targets,block)
			ele_gauge = 1000 if self.trait_dmg else 2000
			burn_dmg = final_atk * ele_scale
			time_to_fallout = ele_gauge / burn_dmg
			artsdmg = (artsdmg1 * time_to_fallout + artsdmg2 * 10)/(time_to_fallout + 10)
			artsdmg += 7000/(10+time_to_fallout) * min(self.targets,block)
			dps = artsdmg
		if self.skill == 0: hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
		else: 
			hitdmg = np.fmax(final_atk * (1-res/100), final_atk * 0.05)
			if self.talent_dmg and self.elite > 0:
				hitdmg2 = np.fmax(final_atk * (1-newres/100), final_atk * 0.05)
				hitdmg = (hitdmg * time_to_fallout + hitdmg2 * 10)/(time_to_fallout + 10)
		dps += hitdmg/self.atk_interval * self.attack_speed/100
		return dps

class YutenjiNyamu(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("YutenjiNyamu",pp,[1,2],[1],2,6,1)	
		if self.module == 1 and self.module_dmg: self.name += " 3inRange"
		if self.targets > 1: self.name += f" {self.targets}targets"

	def skill_dps(self, defense, res):
		atk_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		atkbuff = self.talent2_params[2] if self.elite > 0 else 0
		hits = 3 if self.skill == 1 else 8
		if self.skill == 0: hits = 1
		prob = self.talent1_params[0]
		duration = self.talent1_params[1]
		fragile = self.talent1_params[2]
		counting_hits = hits * int(duration/self.atk_interval) + max(1,hits/2) #only approximation, the later hits in the chain have a higher fragile chance
		fragile_chance = 1 - (1-prob)**counting_hits
		fragile = fragile * fragile_chance + (1-fragile_chance)
		fragile = max(fragile, 1+self.buff_fragile)

		if self.skill == 0:
			skill_scale = self.skill_params[0] if self.skill == 1 else 1
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			splashhitdmg = np.fmax(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			dps = hitdmg/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += splashhitdmg/self.atk_interval * self.attack_speed/100 * (self.targets - 1)
		else:
			big_scale = self.skill_params[0]
			small_scale = self.skill_params[1]
			final_atk = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
			bighitdmg = np.fmax(final_atk * atk_scale * big_scale - defense, final_atk * atk_scale * big_scale * 0.05) * int(hits/3)
			bigsplashhitdmg = np.fmax(0.5 * final_atk * atk_scale * big_scale - defense, 0.5 * final_atk * atk_scale * big_scale * 0.05) * int(hits/3)
			smallhitdmg = np.fmax(final_atk * atk_scale * small_scale - defense, final_atk * atk_scale * small_scale * 0.05) * (hits - int(hits/3))
			smallsplashhitdmg = np.fmax(0.5 * final_atk * atk_scale * small_scale - defense, 0.5 * final_atk * atk_scale * small_scale * 0.05) * (hits - int(hits/3))
			dps = (bighitdmg+smallhitdmg)/self.atk_interval * self.attack_speed/100
			if self.targets > 1:
				dps += (bigsplashhitdmg+smallsplashhitdmg)/self.atk_interval * self.attack_speed/100 * (self.targets - 1)
		return dps * fragile/(1+self.buff_fragile)

class ZuoLe(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("ZuoLe",pp,[1,2,3],[1,2],3,1,1)
		if self.talent_dmg and self.talent2_dmg: self.name += " lowHp"
		else: self.name += " fullHp"
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = 8 * self.skill_params[0] * final_atk * (1 + self.buff_fragile)
			self.name += f" total:{int(hitdmg)}"

	def skill_dps(self, defense, res):
		sp_recovery = 1
		aspd = max(self.talent1_params) if self.talent_dmg and self.talent2_dmg else 0
		if self.talent_dmg and self.talent2_dmg: sp_recovery += self.talent1_params[2]
		if self.elite == 2:
			sp_recovery += self.talent2_params[2] / self.atk_interval * (self.attack_speed+aspd)/100 if self.talent_dmg and self.talent2_dmg else self.talent2_params[0] / self.atk_interval * (self.attack_speed+aspd)/100
		tal_scale = 0.9 + 0.1 * self.module_lvl if self.module == 2 and self.talent2_dmg and self.talent_dmg else 1
		apply_rate = self.talent2_params[2] if self.talent_dmg and self.talent2_dmg and self.elite == 2 else 0.2

		if self.skill == 0:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * tal_scale - defense, final_atk * tal_scale * 0.05)
			hitdmg = hitdmg * (1-apply_rate) + hitdmg2 * apply_rate
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 1:
			atk_scale = self.skill_params[0]
			hits = 3 if self.talent_dmg and self.talent2_dmg else 1
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			hitdmg2 = np.fmax(final_atk * tal_scale - defense, final_atk * tal_scale * 0.05)
			hitdmg = hitdmg * (1-apply_rate) + hitdmg2 * apply_rate
			sp_cost = self.skill_cost / (sp_recovery + self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed + aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg * hits
			if atks_per_skillactivation > 1:
				if atk_scale > 1.41:
					avghit = (skilldmg * hits  + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation
				else:
					avghit = (skilldmg * hits  + int(atks_per_skillactivation) * hitdmg) / (int(atks_per_skillactivation)+1)
			dps = avghit/self.atk_interval * (self.attack_speed + aspd)/100
		if self.skill == 2:
			atkbuff = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * tal_scale - defense, final_atk * tal_scale * 0.05)
			hitdmg = hitdmg * (1-apply_rate) + hitdmg2 * apply_rate
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100 * min(self.targets, 2)
		if self.skill == 3:
			atk_scale = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			hitdmg = np.fmax(final_atk - defense, final_atk * 0.05)
			hitdmg2 = np.fmax(final_atk * tal_scale - defense, final_atk * tal_scale * 0.05)
			hitdmg = hitdmg * (1-apply_rate) + hitdmg2 * apply_rate
			skilldmg = np.fmax(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			skilldmg2= np.fmax(2*final_atk * atk_scale - defense, 2*final_atk* atk_scale * 0.05)
			sp_cost = self.skill_cost / (sp_recovery + self.sp_boost) + 1.2 #sp lockout
			dps = hitdmg/self.atk_interval * (self.attack_speed + aspd)/100
			dps += (6 * skilldmg + skilldmg2) / sp_cost * min(self.targets,3)
		return dps

################################################################################################################################################################################

#Add the operator with their names and nicknames here
op_dict = {"helper1": Defense, "helper2": Res, "12f": twelveF, "aak": Aak, "absinthe": Absinthe, "aciddrop": Aciddrop, "adnachiel": Adnachiel, "<:amimiya:1229075612896071752>": Amiya, "amiya": Amiya, "amiya2": AmiyaGuard, "guardmiya": AmiyaGuard, "amiyaguard": AmiyaGuard, "amiya2": AmiyaGuard, "amiyamedic": AmiyaMedic, "amiya3": AmiyaMedic, "medicamiya": AmiyaMedic, "andreana": Andreana, "angelina": Angelina, "aosta": Aosta, "april": April, "archetto": Archetto, "arene": Arene, "asbestos":Asbestos, "ascalon": Ascalon, "ash": Ash, "ashlock": Ashlock, "astesia": Astesia, "astgenne": Astgenne, "aurora": Aurora, "<:aurora:1077269751925051423>": Aurora, "ayerscarpe": Ayerscarpe,
		"bagpipe": Bagpipe, "beehunter": Beehunter, "beeswax": Beeswax, "bibeak": Bibeak, "blaze": Blaze, "<:blaze_smug:1185829169863589898>": Blaze, "blazealter": BlazeAlter, "blaze2": BlazeAlter, "<:blemi:1077269748972273764>":Blemishine, "blemi": Blemishine, "blemishine": Blemishine,"blitz": Blitz, "azureus": BluePoison, "bp": BluePoison, "poison": BluePoison, "bluepoison": BluePoison, "<:bpblushed:1078503457952104578>": BluePoison, "broca": Broca, "bryophyta" : Bryophyta,
		"cantabile": Cantabile, "canta": Cantabile, "caper": Caper, "carnelian": Carnelian, "castle3": Castle3, "catapult": Catapult, "ceobe": Ceobe, "chen": Chen, "chalter": ChenAlter, "chenalter": ChenAlter, "chenalt": ChenAlter, "chongyue": Chongyue, "ce": CivilightEterna, "civilighteterna": CivilightEterna, "eterna": CivilightEterna, "civilight": CivilightEterna, "theresia": CivilightEterna, "click": Click, "coldshot": Coldshot, "contrail": Contrail, "chemtrail": Contrail, "conviction": Conviction, "clown": Crownslayer, "cs": Crownslayer, "crownslayer": Crownslayer, "dagda": Dagda, "degenbrecher": Degenbrecher, "degen": Degenbrecher, "diamante": Diamante, "dobermann": Dobermann, "doc": Doc, "dokutah": Doc, "dorothy" : Dorothy, "durin": Durin, "god": Durin, "durnar": Durnar, "dusk": Dusk, 
		"eben": Ebenholz, "ebenholz": Ebenholz, "ela": Ela, "entelechia": Entelechia, "ente": Entelechia, "enchilada": Entelechia, "erato": Erato, "estelle": Estelle, "ethan": Ethan, "eunectes": Eunectes, "fedex": ExecutorAlter, "executor": ExecutorAlter, "executoralt": ExecutorAlter, "executoralter": ExecutorAlter, "exe": ExecutorAlter, "foedere": ExecutorAlter, "exu": Exusiai, "exusiai": Exusiai,"exia": Exusiai, "<:exucurse:1078503466353303633>": Exusiai, "<:exusad:1078503470610522264>": Exusiai, "exusiaialter": ExusiaiAlter, "exu2": ExusiaiAlter, "exualt": ExusiaiAlter, "exualter": ExusiaiAlter, "covenant": ExusiaiAlter, "eyja": Eyjafjalla, "eyjafjalla": Eyjafjalla, 
		"fang": FangAlter, "fangalter": FangAlter, "fartooth": Fartooth, "fia": Fiammetta, "fiammetta": Fiammetta, "<:fia_ded:1185829173558771742>": Fiammetta, "figurino": Figurino, "firewhistle": Firewhistle, "flamebringer": Flamebringer, "flametail": Flametail, "flint": Flint, "folinic" : Folinic,
		"franka": Franka, "frost": Frost, "frostleaf": Frostleaf, "fuze": Fuze, "gavial": GavialAlter, "gavialter": GavialAlter, "GavialAlter": GavialAlter, "gladiia": Gladiia, "gnosis": Gnosis, "gg": Goldenglow, "goldenglow": Goldenglow, "gracebearer": Gracebearer, "grace": Gracebearer, "grani": Grani, "greythroat": GreyThroat, "greyy": GreyyAlter, "greyyalter": GreyyAlter, 
		"hadiya": Hadiya, "harmonie": Harmonie, "haze": Haze, "hellagur": Hellagur, "hibiscus": Hibiscus, "hibiscusalt": Hibiscus, "highmore": Highmore, "hoe": Hoederer, "hoederer": Hoederer, "<:dat_hoederer:1219840285412950096>": Hoederer, "hool": Hoolheyak, "hoolheyak": Hoolheyak, "horn": Horn, "hoshiguma": Hoshiguma, "hoshi": HoshigumaAlter, "hoshiguma2": HoshigumaAlter, "hoshigumaalt": HoshigumaAlter, "hoshialte": HoshigumaAlter, "humus": Humus, "iana": Iana, "ifrit": Ifrit, "indra": Indra, "ines": Ines, "insider": Insider, "irene": Irene, 
		"jackie": Jackie, "jaye": Jaye, "jessica": Jessica, "jessica2": JessicaAlter, "jessicaalt": JessicaAlter, "<:jessicry:1214441767005589544>": JessicaAlter, "jester":JessicaAlter, "jessicaalter": JessicaAlter, "justiceknight": JusticeKnight,
		"kafka": Kafka, "kazemaru": Kazemaru, "kirara": Kirara, "kjera": Kjera, "kroos": KroosAlter, "kroosalt": KroosAlter, "kroosalter": KroosAlter, "3starkroos": Kroos, "kroos3star": Kroos, "laios": Laios, "lapluma": LaPluma, "pluma": LaPluma,
		"lappland": Lappland, "lappy": Lappland, "<:lappdumb:1078503487484207104>": Lappland, "lappy2": LapplandAlter, "lapp2": LapplandAlter, "lappland2": LapplandAlter, "lapplandalter": LapplandAlter, "decadenza": LapplandAlter, "lappalt": LapplandAlter, "lappalter": LapplandAlter, "laptop": LapplandAlter, "lava3star": Lava3star, "lava": Lavaalt, "lavaalt": Lavaalt,"lavaalter": Lavaalt, "lee": Lee, "leizi": LeiziAlter, "leizialter": LeiziAlter, "leiziberator": LeiziAlter, "lemuen": Lemuen, "lessing": Lessing, "leto": Leto, "logos": Logos, "lin": Lin, "ling": Ling, "lucilla": Lucilla, "lunacub": Lunacub, "luoxiaohei": LuoXiaohei, "luo": LuoXiaohei, "lutonada": Lutonada, 
		"magallan": Magallan, "maggie": Magallan, "manticore": Manticore, "marcille": Marcille, "matoimaru": Matoimaru, "may": May, "melantha": Melantha, "meteor":Meteor, "meteorite": Meteorite, "midnight": Midnight, "minimalist": Minimalist, "mint": Mint, "misschristine": MissChristine, "christine": MissChristine, "mschrstine": MissChristine, "misumiuika": MisumiUika, "uika": MisumiUika, "misumi": MisumiUika, "uikamisumi": MisumiUika, "mizuki": Mizuki, "mlynar": Mlynar, "uncle": Mlynar, "monster": Mon3tr, "mon3ter": Mon3tr, "kaltsit": Kaltsit, "mostima": Mostima, "morgan": Morgan, "mountain": Mountain, "mousse": Mousse, "mrnothing": MrNothing, "mudmud": Mudrock, "mudrock": Mudrock,
		"mumu": Muelsyse,"muelsyse": Muelsyse, "narantuya": Narantuya, "ntr": NearlAlter, "ntrknight": NearlAlter, "nearlalter": NearlAlter, "nearl": NearlAlter, "necrass": Necrass, "eblana": Necrass, "banana": Necrass, "nian": Nian, "nymph": Nymph, "odda": Odda, "pallas": Pallas, "passenger": Passenger, "penance": Penance, "pepe": Pepe, "phantom": Phantom, "pinecone": Pinecone,"pith": Pith,  "platinum": Platinum, "plume": Plume, "popukar": Popukar, "pozy": Pozemka, "pozemka": Pozemka, "pramanix": PramanixAlter, "pramanixalter":PramanixAlter, "projekt": ProjektRed, "red": ProjektRed, "projektred": ProjektRed, "provence": Provence, "pudding": Pudding, "qiubai": Qiubai,"quartz": Quartz, 
		"raidian": Raidian, "rangers": Rangers, "ray": Ray, "reed": ReedAlter, "reedalt": ReedAlter, "reedalter": ReedAlter,"reed2": ReedAlter, "rockrock": Rockrock, "rosa": Rosa, "rosmontis": Rosmontis, "saga": Saga, "bettersiege": Saga, "sandreckoner": SandReckoner, "reckoner": SandReckoner, "sankta": SanktaMiksaparato, "sanktamiksaparato": SanktaMiksaparato, "mixer": SanktaMiksaparato, "savage": Savage, "scavenger": Scavenger, "scene": Scene, "schwarz": Schwarz, "shalem": Shalem, "sharp": Sharp,
		"sideroca": Sideroca, "siege": Siege, "silverash": SilverAsh, "sa": SilverAsh, "skadi": Skadi, "<:skadidaijoubu:1078503492408311868>": Skadi, "<:skadi_hi:1211006105984041031>": Skadi, "<:skadi_hug:1185829179325939712>": Skadi, "kyaa": Skadi, "skalter": Skalter, "skadialter": Skalter, "snegurochka": Snegurochka, "sneg": Snegurochka, "snezhnaya": Snegurochka, "specter": Specter, "shark": SpecterAlter, "specter2": SpecterAlter, "spectral": SpecterAlter, "spalter": SpecterAlter, "specteralter": SpecterAlter, "laurentina": SpecterAlter, "stainless": Stainless, "steward": Steward, "stormeye": Stormeye, "surfer": Surfer, "surtr": Surtr, "jus": Surtr, "suzuran": Suzuran, "swire": SwireAlt, "swire2": SwireAlt,"swirealt": SwireAlt,"swirealter": SwireAlt, 
		"tachanka": Tachanka, "tecno": Tecno, "texas": TexasAlter, "texasalt": TexasAlter, "texasalter": TexasAlter, "texalt": TexasAlter, "texalter": TexasAlter, "tequila": Tequila, "terraresearchcommission": TerraResearchCommission, "trc": TerraResearchCommission, "thorns": Thorns, "thorn": Thorns, "thorns2": ThornsAlter, "lobster": ThornsAlter, "thornsalter": ThornsAlter, "tin": TinMan, "tinman": TinMan, "tippi": Tippi, "toddifons":Toddifons, "sakiko": TogawaSakiko,"togawa": TogawaSakiko,"togawasakiko": TogawaSakiko,"sakikotogawa": TogawaSakiko, "tomimi": Tomimi, "totter": Totter, "tragodia": Tragodia, "typhon": Typhon, "<:typhon_Sip:1214076284343291904>": Typhon, 
		"ulpian": Ulpianus, "ulpianus": Ulpianus, "underflow": Underflow, "utage": Utage, "vanilla": Vanilla, "vendela": Vendela, "vermeil": Vermeil, "vetochki": Vetochki, "veto": Vetochki, "vigil": Vigil, "trash": Vigil, "garbage": Vigil, "vigna": Vigna, "vina": Vina, "victoria": Vina, "siegealter": Vina, "vinavictoria": Vina, "virtuosa": Virtuosa, "<:arturia_heh:1215863460810981396>": Virtuosa, "arturia": Virtuosa, "viviana": Viviana, "vivi": Viviana, "vulcan": Vulcan, "ingrid": Vulpisfoglia, "vulpisfoglia": Vulpisfoglia, "suzumom": Vulpisfoglia, "vulpis": Vulpisfoglia, "w": W, "wakaba": WakabaMutsumi,"mutsumi": WakabaMutsumi,"wakabamutsumi": WakabaMutsumi,"mutsumiwakaba": WakabaMutsumi, "walter": Walter, "wisadel": Walter, "warmy": Warmy, "weedy": Weedy, "whislash": Whislash, "aunty": Whislash, "wildmane": Wildmane, "windscoot": Windscoot, 
		"yahataumiri": YahataUmiri, "umiri": YahataUmiri, "yahata": YahataUmiri, "umiriyahata": YahataUmiri, "yato": YatoAlter, "yatoalter": YatoAlter, "kirinyato": YatoAlter, "kirito": YatoAlter, "yu": Yu, "you": Yu, "yutenjinyamu": YutenjiNyamu, "Ynyamu": YutenjiNyamu, "yutenji": YutenjiNyamu, "zuo": ZuoLe, "zuole": ZuoLe}

#The implemented operators
operators = ["12F","Aak","Absinthe","Aciddrop","Adnachiel","Amiya","AmiyaGuard","AmiyaMedic","Andreana","Angelina","Aosta","April","Archetto","Arene","Asbestos","Ascalon","Ash","Ashlock","Astesia","Astgenne","Aurora","Ayerscarpe","Bagpipe","Beehunter","Beeswax","Bibeak","Blaze","BlazeAlter","Blemishine","Blitz","BluePoison","Broca","Bryophyta","Cantabile","Caper","Carnelian","Castle3","Catapult","Ceobe","Chen","Chalter","Chongyue","CivilightEterna","Click","Coldshot","Contrail","Conviction","Crownslayer","Dagda","Degenbrecher","Diamante","Dobermann","Doc","Dorothy","Durin","Durnar","Dusk","Ebenholz","Ela","Entelechia","Erato","Estelle","Ethan","Eunectes","ExecutorAlt","Exusiai","Eyjafjalla","FangAlter","Fartooth","Fiammetta","Figurino","Firewhistle","Flamebringer","Flametail","Flint","Folinic","Franka","Frost","Frostleaf","Fuze","Gavialter","Gladiia","Gnosis","Goldenglow","Gracebearer","Grani","Greythroat","GreyyAlter",
		"Hadiya","Harmonie","Haze","Hellagur","Hibiscus","Highmore","Hoederer","Hoolheyak","Horn","Hoshiguma","HoshigumaAlter","Humus","Iana","Ifrit","Indra","Ines","Insider","Irene","Jackie","Jaye","Jessica","JessicaAlt","JusticeKnight","Kafka","Kaltsit","Kazemaru","Kirara","Kjera","Kroos","Kroos3star","Laios","Lapluma","Lappland","LapplandAlter","Lava3star","LavaAlt","Lee","LeiziAlter","Lemuen","Lessing","Logos","Leto","Lin","Ling","Lucilla","Lunacub","LuoXiaohei","Lutonada","Magallan","Manticore","Marcille","Matoimaru","May","Melantha","Meteor","Meteorite","Midnight","Minimalist","Mint","MissChristine","MisumiUika","Mizuki","Mlynar","Mon3tr","Mostima","Morgan","Mountain","Mousse","MrNothing","Mudrock","Muelsyse(type !mumu for details)","Narantuya","NearlAlter","Necrass","Nian","Nymph","Odda","Pallas","Passenger","Penance","Pepe","Phantom","Pinecone","Pith","Platinum","Plume","Popukar","Pozemka","PramanixAlter","ProjektRed","Provence","Pudding","Qiubai","Quartz","Raidian","Rangers","Ray","ReedAlt","Rockrock",
		"Rosa","Rosmontis","Saga","SandReckoner","Savage","Scavenger","Scene","Schwarz","Shalem","Sharp","Sideroca","Siege","SilverAsh","Skadi","Skalter","Snegurochka","Specter","SpecterAlter","Stainless","Steward","Stormeye","Surfer","Surtr","Suzuran","SwireAlt","Tachanka","Tecno","TexasAlter","Tequila","TerraResearchCommission","Thorns","ThornsAlter","TinMan","Tippi","Toddifons","Tomimi","Totter","Tragodia","Typhon","Ulpianus","Underflow","Utage","Vanilla","Vendela", "Vermeil","Vetochki","Vigil","Vigna","VinaVictoria","Virtuosa","Viviana","Vulcan","Vulpisfoglia","W","WakabaMutsumi","Warmy","Weedy","Whislash","Wildmane","Windscoot","Wis'adel","YahataUmiri","YatoAlter","Yu","YutenjiNyamu","ZuoLe"]
