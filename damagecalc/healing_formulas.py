from damagecalc.damage_formulas import Operator
from damagecalc.utils import PlotParameters

class Healer(Operator):
	def skill_hps(self, **kwargs):
		return("Operator not implemented")
		
class Breeze(Healer):
	def __init__(self, params: PlotParameters, **kwargs):
		super().__init__("Breeze",params,[1,2],[1],2,1,1)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		skilldown_hps = final_atk/self.atk_interval * self.attack_speed/100 * min(self.targets,3) * (1 + self.buff_fragile)
		skill_hps = final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 1 and self.targets > 1: skill_hps *= min(2,self.targets)
		if self.skill == 2 and self.targets > 1: skill_hps *= 1 + 0.5 * (self.targets - 1)
		avg_hps = (skill_hps * self.skill_duration + skilldown_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))

		self.name += f": **{int(skill_hps)}**/{int(skilldown_hps)}/*{int(avg_hps)}*"
		return self.name

class Eyjaberry(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("EyjafjallaAlter",pp,[1,3],[1],1,1,1)

	def skill_hps(self, **kwargs):
		talent_scale = 0 if self.elite < 1 else self.talent1_params[0] * 3
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = (final_atk/self.atk_interval * self.attack_speed/100 + final_atk * talent_scale) * (1 + self.buff_fragile)
		if self.skill == 1:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = (final_atk_skill/self.atk_interval * self.attack_speed/100 + final_atk_skill * talent_scale) * (1 + self.buff_fragile) * min(self.targets,2)
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}"
		if self.skill == 3:
			skill_scale = self.skill_params[0]
			skill_hps = (5 * skill_scale * final_atk/self.atk_interval * self.attack_speed/100 + final_atk * talent_scale * min(self.targets,5)) * (1 + self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost/(1+self.sp_boost))/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Lumen(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Lumen",pp,[1,2,3],[1,2],3,6,2)
		if self.module != 2 and not self.trait_dmg: self.name += " atRange"
	
	def skill_hps(self, **kwargs):
		range_heal = 1 if self.module == 2 or self.trait_dmg else 0.8
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk * range_heal /self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		####the actual skills
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			heal_duration = self.skill_params[1]
			skill_hps = final_atk * skill_scale * (1 + self.buff_fragile) * min(self.targets,9)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = int(sp_cost / atkcycle) + 1
			avg_hps = base_hps + skill_hps * heal_duration / (atks_per_skillactivation * atkcycle)
			self.name += f": **{int(skill_hps+base_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.skill == 2:
			skill_hps = final_atk * self.skill_params[0] * (1+self.buff_fragile) * min(self.targets,self.skill_params[1])
			avg_hps = base_hps + skill_hps / self.skill_cost * (1 + self.sp_boost)
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.skill == 3:
			aspd = self.skill_params[0]
			atkbuff = self.skill_params[3]
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = final_atk_skill * range_heal / self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}"
		return self.name

class Myrtle(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Myrtle",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		if self.elite < 2 and self.skill == 1: 
			self.name += ": No heals =("
			return self.name
		if self.elite == 2 and self.skill == 1:
			self.name += f": {int(self.talent1_params[0])}hps to vanguards"
			return self.name
		extraheal = self.talent1_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skillhps = final_atk * self.skill_params[0] * (1+self.buff_fragile) * min(self.targets,9)
		avghps = skillhps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skillhps)}**/0/*{int(avghps)}* + {int(extraheal)}hps to vanguards"
		return self.name

class Paprika(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Paprika",pp,[1,2],[],2,1,0)
		if self.elite > 0:
			if self.skill == 2:
				if self.talent_dmg: self.name += " <40%Hp"
				elif self.skill_dmg: self.name += f" 40-{int(100*self.skill_params[2])}%Hp"
				else: self.name += f" >{int(100*self.skill_params[2])}%Hp"
			else:
				if self.talent_dmg: self.name += " <40%Hp"
				else: self.name += " >40%Hp"
	
	def skill_hps(self, **kwargs):
		targets = min(self.targets,4)
		target_scaling = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2]
		target_scaling_skill = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2 + 0.75**3]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		aspd = self.skill_params[0] if self.skill == 1 else 0
		final_atk_skill = final_atk if self.skill == 1 else self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		bonus_heal = self.talent1_params[1] if self.elite > 0 else 0
		base_hps = final_atk/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile) * target_scaling[targets]
		if self.talent_dmg: base_hps += bonus_heal/self.atk_interval *self.attack_speed/100 * min(self.targets,3) * (1+self.buff_fragile)
		if self.skill == 1:
			skill_hps = final_atk/self.atk_interval *(self.attack_speed+aspd)/100 * (1+self.buff_fragile) * target_scaling[targets]
			if self.talent_dmg: skill_hps += bonus_heal/self.atk_interval *(self.attack_speed+aspd)/100 * (1+self.buff_fragile) * min(self.targets,3)
		else:
			skill_hps = final_atk_skill/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile) * target_scaling_skill[targets]
			if self.talent_dmg or self.skill_dmg:
				skill_hps += bonus_heal/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile) * min(self.targets,4)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost/(1+self.sp_boost))/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name


class Ptilopsis(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Ptilopsis",pp,[1,2],[1],2,1,1)
	
	def skill_hps(self, **kwargs):
		sp_boost = self.talent1_params[0] if self.elite > 0 else 0
		sp_boost = max(self.sp_boost, sp_boost)
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile) * min(self.targets,3)

		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		atk_interval = self.atk_interval + self.skill_params[0] if self.skill == 2 else self.atk_interval
		final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		skill_hps = final_atk_skill/atk_interval * self.attack_speed/100 * min(self.targets,3) * (1+self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost/(1+sp_boost))/(self.skill_duration + self.skill_cost/(1+sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Purestream(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Purestream",pp,[1,2],[2],2,6,2)
		if not self.module == 2 and not self.trait_dmg: self.name += " atRange"
	
	def skill_hps(self, **kwargs):
		ranged_heal = 1 if self.module == 2 or self.trait_dmg else 0.8
		heal_scale = 1
		if self.module == 2:
			if self.module_lvl == 2: heal_scale = 1.1
			if self.module_lvl == 3: heal_scale = 1.2
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * ranged_heal
		skill_scale = self.skill_params[0]
		if self.skill == 1:
			skill_hps = final_atk * skill_scale * heal_scale * (1+self.buff_fragile) * self.targets
			avg_hps = base_hps + skill_hps / self.skill_cost * (1+ self.sp_boost)
		if self.skill == 2:
			atk_interval = self.atk_interval * 0.12
			skill_hps = skill_scale * ranged_heal * heal_scale * final_atk/ atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
			avg_hps = (base_hps * self.skill_cost/(1+self.sp_boost) + skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Quercus(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Quercus",pp,[1,2],[1],1,1,1)
	
	def skill_hps(self, **kwargs):
		heal_factor = 1 if self.module == 1 else 0.75
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile)
			self.name += f": **{int(skill_hps)}**/0"
		if self.skill == 2:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skillhps = heal_factor * final_atk/self.atk_interval *(self.attack_speed+aspd)/100 * (1+self.buff_fragile)
			avghps = (skillhps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
		return self.name

class Shu(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Shu",pp,[1,2,3],[1],3,1,1)
		if self.skill == 1: self.module_dmg = True
		if self.elite == 2 and self.talent2_dmg: self.name += " maxTalent2"
		if self.skill == 3 and not self.skill_dmg: self.name += " noEnemies"
		if self.module == 1 and not self.module_dmg: self.name += " >50%Hp"
	
	def skill_hps(self, **kwargs):
		grassheal = 0 if self.elite < 1 else self.talent1_params[0] * self.targets
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		aspd = self.talent2_params[1] if self.elite == 2 and self.talent2_dmg else 0
		atkbuff = self.talent2_params[2] if self.elite == 2 and self.talent2_dmg else 0
		sp_boost = self.sp_boost + 0.25 if self.elite == 2 and self.talent2_dmg else self.sp_boost
			
		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			skill_scale = self.skill_params[0]
			sp_cost = self.skill_cost
			sp_cost= sp_cost/(1+sp_boost) + 1.2
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = final_atk * heal_scale * skill_scale * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
			self.name += f": **{int(skill_hps+grassheal)}**/{int(grassheal)}/*{int(avg_hps+grassheal)}*"
		
		if self.skill == 2:
			self.atk_interval = 2.5
			grassheal_skill = grassheal * self.skill_params[1]
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0] + atkbuff) + self.buff_atk_flat
			skill_hps = heal_scale * final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * min(self.targets,2) + grassheal_skill
			avg_hps = (skill_hps * self.skill_duration + grassheal*self.skill_cost/(1+sp_boost))/ (self.skill_duration + self.skill_cost/(1+sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(grassheal)}/*{int(avg_hps)}*"
		
		if self.skill == 3:
			atkbuff += self.skill_params[0]
			if self.skill_dmg:
				aspd += self.skill_params[2]
				atkbuff += self.skill_params[1]
			print(atkbuff,aspd,self.atk)

			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = heal_scale* final_atk_skill/self.atk_interval * (self.attack_speed + aspd)/100 * (1 + self.buff_fragile)
			avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+sp_boost))
			self.name += f": **{int(skill_hps+grassheal)}**/{int(grassheal)}/*{int(avg_hps+grassheal)}*"

		return self.name

class Silence(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Silence",pp,[1,2],[1],2,1,1)
		if self.module_dmg and self.module == 1: self.name += " healingMelee"
	
	def skill_hps(self, **kwargs):
		aspd = self.talent1_params[0] if self.elite > 0 else 0
		heal_factor = 1.15 if self.module == 1 and self.module_dmg else 1

		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_factor * final_atk / self.atk_interval * (self.attack_speed + aspd)/100 * (1 + self.buff_fragile)

		if self.skill == 1:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		if self.skill == 2:
			skill_hps = self.drone_atk * min(self.targets,8)
			avg_hps = skill_hps * min(1, 10 / self.skill_cost * (1 + self.sp_boost))
			skill_hps += base_hps
			avg_hps += base_hps
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

#################################################################################################################################################


healer_dict = {"breeze":Breeze, "eyja": Eyjaberry, "eyjafjalla": Eyjaberry, "eyjaberry": Eyjaberry, "lumen": Lumen, "myrtle": Myrtle, "paprika": Paprika, "ptilopsis": Ptilopsis, "ptilo": Ptilopsis, "purestream": Purestream, "quercus": Quercus, "shu": Shu, "silence": Silence}

healers = ["Breeze","Eyjafjalla","Lumen","Myrtle","Paprika","Ptilopsis","Purestream","Quercus","Shu","Silence"]