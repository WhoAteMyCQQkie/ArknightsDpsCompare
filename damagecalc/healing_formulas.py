from damagecalc.damage_formulas import Operator
from damagecalc.utils import PlotParameters

class Healer(Operator):
	def __init__(self, name, params: PlotParameters, available_skills, module_overwrite = [], default_skill = 3, default_pot = 1, default_mod = 1):
		if params.skill == 0:  params.skill = -1
		super().__init__(name,params,available_skills,module_overwrite,default_skill,default_pot,default_mod)

	def skill_hps(self, **kwargs):
		return("Operator not implemented")

class AmiyaMedic(Operator):
	def __init__(self, pp, *args, **kwargs):
		super().__init__("AmiyaMedic",pp,[1,2],[1],2,6,1) #available skills, available modules, default skill, def pot, def mod
		if self.skill == 2 and not self.skill_dmg: self.name += " noStacks"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		self.res = pp.res
		if self.elite > 0:
			try:
				self.target_hp = max(100,kwargs['hp'])
			except KeyError:
				self.target_hp = 2000
	
	def skill_hps(self,**kwargs):
		heal_scale = 0.6 if self.module == 1 else 0.5
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		self.name += ": "
		if len(self.res) > 1: self.res = self.res[1:]
		for res in self.res:
			res = max(0,res)
			if self.skill == 1:
				aspd = self.skill_params[0]
				skill_scale = self.skill_params[1]
				hitdmg = final_atk * (1-res/100)
				base_hps = heal_scale * final_atk * (1-res/100) / self.atk_interval * (self.attack_speed) / 100 * (1 + self.buff_fragile)
				skill_hps = heal_scale * final_atk * (1-res/100) / self.atk_interval * (self.attack_speed + aspd) / 100 * (1 + self.buff_fragile)
				skill_hps += skill_scale * final_atk / self.atk_interval * (self.attack_speed + aspd) / 100 * (1 + self.buff_fragile) * min(self.targets,13)
				avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
				self.name += f"{res}res: **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*   "
			if self.skill == 2:
				atkbuff = 5 * self.skill_params[1] if self.skill_dmg else 0
				final_atk_skill = self.atk * (1 + atkbuff + self.buff_atk) + self.buff_atk_flat
				hitdmg = final_atk_skill
				skill_hps = heal_scale * hitdmg / self.atk_interval * (self.attack_speed) / 100 * min(self.targets,2) * (1 + self.buff_fragile)
				base_hps = heal_scale * final_atk * (1-res/100) / self.atk_interval * (self.attack_speed) / 100 * (1 + self.buff_fragile)
				self.name += f"{res}res: **{int(skill_hps)}**/{int(base_hps)}   "
		if len(self.res) == 1: self.name = self.name.replace(" 0res: "," ")
		if self.elite > 0:
			talent_heal = self.target_hp * self.talent1_params[1]
			avg_talent = (talent_heal * self.skill_duration)/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			if self.skill == 1: self.name += f"and passive **{int(talent_heal)}**/0/*{int(avg_talent)}* per {self.target_hp}hp"
			if self.skill == 2: self.name += f"and passive **{int(talent_heal)}**/0 per {self.target_hp}hp"
		return self.name

class Ansel(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Ansel",pp,[1],[],1,6,1)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		targets = 1 if self.elite == 0 or self.targets == 1 else 1 + self.talent1_params[0]
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * targets * (1 + self.buff_fragile)
		skill_hps = final_atk_skill/self.atk_interval * self.attack_speed/100 * targets * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Bassline(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Bassline",pp,[1,2],[2],1,1,2)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			skill_hps = final_atk * self.skill_params[0] * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		if self.skill == 2:
			self.atk_interval = 2.5
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk_skill / self.atk_interval * self.attack_speed/100 * (1+ self.buff_fragile)
			avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}* or **{int(skill_hps * (1+self.skill_params[2]))}**/0/*{int(avg_hps* (1+self.skill_params[2]))}* inlcuding the barrier"
		return self.name

class Blemishine(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Blemishine",pp,[1,2,3],[2,1],3,1,1)
		if self.module == 1 and self.skill != 2 and not self.module_dmg: self.name += " >50%Hp"
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.skill == 1: self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
			
		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			skill_scale = self.skill_params[1]
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = final_atk * heal_scale * skill_scale * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"

		skill_recovery = 1/self.atk_interval * self.attack_speed/100
		if self.hits > 0:
			skill_recovery += self.hits
		
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_scale = self.skill_params[1]
			skill_hps = final_atk_skill * skill_scale * min(self.targets,13)
			avg_hps = (skill_hps * self.skill_duration + self.skill_cost/skill_recovery)/ (self.skill_duration + self.skill_cost/skill_recovery)
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		
		if self.skill == 3:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_scale = self.skill_params[3]
			skill_hps = heal_scale * skill_scale * final_atk_skill/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + self.skill_cost/skill_recovery)/ (self.skill_duration + self.skill_cost/skill_recovery)
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"

		return self.name

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

class Ceylon(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Ceylon",pp,[1,2],[1],2,6,1)
		if not self.trait_dmg: self.name += " atRange"
		if self.talent_dmg: self.name += " watermap"
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[1] if self.talent_dmg else self.talent1_params[0]
		if self.elite == 0: atkbuff = 0
		range_heal = 1 if self.trait_dmg else 0.8
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		base_hps = final_atk * range_heal /self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		
		####the actual skills
		if self.skill == 1:
			skill_factor = self.skill_params[0]
			skill_heal = final_atk * skill_factor * (1 + self.buff_fragile)
			base_heal = range_heal * final_atk * (1 + self.buff_fragile)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			skill_hps = skill_heal/self.atk_interval*self.attack_speed/100
			avg_hps = avg_heal/self.atk_interval*self.attack_speed/100
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff + self.skill_params[1]) + self.buff_atk_flat
			skill_hps = final_atk_skill * range_heal /self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile) * min(self.targets,2)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Chestnut(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Chestnut",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		aspd = self.skill_params[0] if self.skill == 2 else 0
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		skill_hps = final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class CivilightEterna(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("CivilightEterna",pp,[1,2,3],[1],3,6,1)
		if self.module == 1 and not self.module_dmg: self.name += " noModBonus"
	
	def skill_hps(self, **kwargs):
		targets = 9 if self.elite == 0 else 13
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk+atkbuff) + self.buff_atk_flat
		trait_factor = self.talent1_params[5] * 6 / 8 + 1 * 2 / 8  #it's active for 6 seconds reactivated every 8 seconds
		base_hps = final_atk * 0.1 * min(self.targets,targets) * trait_factor * min(1, 4 / self.targets) #not all operators benefit from trait factor
		base_no_balls = final_atk * 0.1 * min(self.targets, targets)
		dust_heal_scale = self.talent1_params[6] if self.module == 1 and self.module_lvl > 1 else 0
		dust_heal = dust_heal_scale * final_atk / 12 * 3 / 2 * (1 + self.buff_fragile) * min(self.targets, 4)#12 second for a revolution, 3 orbs, only every second affects ops.
		base_hps += dust_heal
		if self.skill == 1:
			new_trait = self.skill_params[0]
			skill_hps = final_atk * new_trait * min(self.targets,targets) * trait_factor * min(1, 8 / self.targets)
			dust_heal *=  min(self.targets, 8) / min(self.targets, 4)
			skill_hps += dust_heal
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}"
			skill_no_balls = final_atk * new_trait * min(self.targets,targets)
			self.name += f" or **{int(skill_no_balls)}**/{int(base_no_balls)} w/o the balls"
		if self.skill == 2:
			skill_hps = final_atk * 0.1 * min(self.targets,targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.skill == 3:
			targets += 8
			new_trait = self.skill_params[0]
			skill_hps = final_atk * new_trait * min(self.targets,targets) * trait_factor
			dust_heal *= min(self.targets, targets) / min(self.targets, 4)
			skill_hps += dust_heal
			skill_no_balls =  final_atk * new_trait * min(self.targets,targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
			avg_no_balls = (skill_no_balls * self.skill_duration + base_no_balls * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f" or **{int(skill_no_balls)}**/{int(base_no_balls)}/*{int(avg_no_balls)}* w/o the balls"
		return self.name

class Doc(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Doc",pp,[1,2],[2],2,1,2)
	
	def skill_hps(self, **kwargs):
		heal_scale = self.skill_params[2] if self.skill == 1 else self.skill_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skill_hps = final_atk * heal_scale * (1+self.buff_fragile)
		avg_hps = skill_hps / self.skill_cost * (1+ self.sp_boost)
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		if self.skill == 1: self.name += " only to self"
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

class Folinic(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Folinic",pp,[1,2],[2],1,6,2)
		if self.module == 2 and self.module_dmg: self.name += " groundUnit"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_scale * final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 1:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_scale * final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 2:
			skill_hps = heal_scale * final_atk * self.skill_params[0]/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile) * min(self.targets,9)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Gavial(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Gavial",pp,[1,2],[2],1,6,2)
		if self.module_dmg and self.module == 2: self.name += " groundUnit"
		if self.elite > 0 and self.talent_dmg: self.name += f" first{int(self.talent1_params[2])}sec"
		if self.skill_dmg: self.name += " lowHp"
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0] if self.talent_dmg else 0
		heal_factor = 1.15 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		skill_duration = self.skill_params[4]
		skill_factor = self.skill_params[1] if self.skill_dmg else self.skill_params[0]
		base_hps = heal_factor * final_atk / self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		targets = min(self.targets,12) if self.skill == 2 else 1
		skill_hps = heal_factor * skill_factor * final_atk * (1 + self.buff_fragile) * targets
		avg_hps = base_hps + skill_hps * skill_duration / (self.skill_cost /(1+ self.sp_boost) + 1.2)
		self.name += f": **{int(skill_hps + base_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Gummy(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Gummy",pp,[1,2],[1],1,1,1)
		if self.module == 1 and not self.module_dmg: self.name += " >50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			skill_hps = final_atk * heal_scale * self.skill_params[0] * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
		if self.skill == 2:
			self.atk_interval = 2.76
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk_skill * heal_scale / self.atk_interval * self.attack_speed/100 * (1+ self.buff_fragile)
			avg_hps = skill_hps * 20 / (30 + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Harold(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Harold",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		atkbuff = self.skill_params[0] if self.skill == 1 else 0
		final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		aspd = self.skill_params[0] if self.skill == 2 else 0
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		skill_hps = final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Haruka(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Haruka",pp,[1,2,3],[2],2,1,2)
		if not self.skill_dmg and self.skill == 2: self.name += " 1stActivation"
	
	def skill_hps(self, **kwargs):
		targets = 2 if self.module == 2 else 1
		heal_factor = 1 if self.module == 1 else 0.75
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_bubble = 0.25 * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * min(targets,self.targets)
		if self.skill == 1:
			aspd = self.skill_params[0]
			skill_hps = heal_factor * final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * min(targets,self.targets)
			avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost)) 
			skill_bubble = 0.25 * final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * min(targets,self.targets)
			avg_bubble = (skill_bubble * self.skill_duration + self.skill_cost/(1+self.sp_boost) * base_bubble)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			if self.elite > 1: self.name += f": **{int(skill_hps+skill_bubble)}**/{int(base_bubble)}/*{int(avg_hps+avg_bubble)}* or **{int(skill_hps)}**/0/*{int(avg_hps)}* w/o bubble"
			else: self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"

		if self.skill == 2:
			if self.skill_dmg: final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			targets += self.skill_params[2]
			skill_hps = heal_factor * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * min(targets,self.targets)
			skill_bubble = 0.25 * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * min(targets,self.targets)
			if self.elite > 1: self.name += f": **{int(skill_hps+skill_bubble)}**/{int(base_bubble)} or **{int(skill_hps)}**/0 w/o bubble"
			else: self.name += f": **{int(skill_hps)}**/0"
		
		if self.skill == 3:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[2]) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/(self.atk_interval+self.skill_params[0]) * self.attack_speed/100 * (1+self.buff_fragile) * min(targets,self.targets)
			skill_bubble = 0.25 * final_atk/(self.atk_interval+self.skill_params[0]) * self.attack_speed/100 * (1+self.buff_fragile) * min(targets,self.targets)
			avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			avg_bubble = (skill_bubble * self.skill_duration + self.skill_cost/(1+self.sp_boost) * base_bubble)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			if self.elite > 1: self.name += f": **{int(skill_hps+skill_bubble)}**/{int(base_bubble)}/*{int(avg_hps+avg_bubble)}* or **{int(skill_hps)}**/0/*{int(avg_hps)}* w/o bubble"
			else: self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"

		return self.name

class Heidi(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Heidi",pp,[1,2],[1],2,1,1)
		if self.module == 1 and not self.module_dmg: self.name += " noModBonus"
	
	def skill_hps(self, **kwargs):
		targets = 9 if self.elite == 0 else 13
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		if self.skill == 1: atkbuff += self.talent1_params[0]
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		base_hps = final_atk * 0.1 * min(self.targets,targets)
		if self.skill == 1:
			self.name += f": {int(base_hps)}" 
		if self.skill == 2:
			skill_hps = final_atk * self.skill_params[3] * min(self.targets,targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Hibiscus(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Hibiscus",pp,[1],[],1,6)
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0]
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0] + atkbuff) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		skill_hps = final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Honeyberry(Healer):
	def __init__(self, params: PlotParameters, **kwargs):
		super().__init__("Honeyberry",params,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 1:
			skill_heal = final_atk * (1 + self.buff_fragile) * min(self.targets,2)
			base_heal = final_atk * (1 + self.buff_fragile)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			skill_hps = skill_heal/self.atk_interval*self.attack_speed/100
			avg_hps = avg_heal/self.atk_interval*self.attack_speed/100
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile) * min(self.targets,self.skill_params[1])
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Hung(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Hung",pp,[1,2],[2],1,1,2)
		if self.elite == 2 and self.talent_dmg: self.name += " highGroundTarget"
		try:
			self.hits = kwargs['hits']
		except KeyError:
			self.hits = 0
		if self.hits > 0: self.name += f" {round(self.hits,2)}hits/s"
	
	def skill_hps(self, **kwargs):
		heal_scale = self.talent1_params[0] if self.talent_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat

		if self.skill == 1:
			skill_hps = final_atk * heal_scale * self.skill_params[0] * (1+ self.buff_fragile)
			avg_hps = skill_hps / (self.skill_cost/self.hits) if self.hits > 0 else 0
		if self.skill == 2:
			self.atk_interval = 2.5
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk_skill * heal_scale / self.atk_interval * self.attack_speed/100 * (1+ self.buff_fragile)
			avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/self.hits) if self.hits > 0 else 0
		
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Kaltsit(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Kaltsit",pp,[1,2,3],[1,2,3],2,1,1)
		if self.module == 3:
			self.name = self.name[:-9] + f"α{self.module_lvl}"
		if self.module_dmg:
			if self.module == 1: self.name += " <50%Hp"
			if self.module == 2: self.name += " ground"
	
	def skill_hps(self, **kwargs):
		targets = 2 if self.module == 3 else 1
		heal_factor = 1.15 if self.module in [1,2] and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_factor * final_atk / self.atk_interval * (self.attack_speed)/100 * (1 + self.buff_fragile) * min(self.targets,targets)
		aspd = self.skill_params[0] if self.skill == 2 else 0
		skill_hps = heal_factor * final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile) * min(self.targets,targets)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Lancet2(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Lancet2",pp,[],[],0,6)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		self.name += f": {int(base_hps)} + {int(self.talent1_params[0])} on deploy"
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

class Mon3tr(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Mon3tr",pp,[1,2,3],[],2,1,0)
		if not self.talent_dmg or (self.skill == 2 and not self.skill_dmg): self.name += " noConstruct"

	def skill_hps(self, **kwargs):
		targets = min(self.targets,4)
		atkbuff = self.talent1_params[1] if self.talent_dmg and (self.skill != 2 or self.skill_dmg) else 0
		target_scaling = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2]
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		aspd = self.talent2_params[1] if self.elite > 0 else 0
		if self.skill == 1:
			target_scaling_skill = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2 + 0.75**3]
			heals =  (final_atk * target_scaling[targets] * self.skill_cost + final_atk * self.skill_params[0] * target_scaling_skill[targets]) / (self.skill_cost + 1)
			avg_hps = heals/self.atk_interval * (self.attack_speed + aspd)/100 * (1+self.buff_fragile)
			self.name += f": *{int(avg_hps)}*"
			return self.name
		
		base_hps = final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * target_scaling[targets]
		skill_down_duration = self.atk_interval / (self.attack_speed+aspd) * 100 * self.skill_cost
		if self.skill == 2:
			aspd *= self.skill_params[0]
			skill_hps = final_atk / self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * target_scaling[targets]
			if self.skill_dmg and self.talent_dmg: skill_hps *= 2
		if self.skill == 3: 
			final_atk = self.atk * (1 + self.buff_atk + atkbuff + self.skill_params[0]) + self.buff_atk_flat
			atk_interval = self.atk_interval + self.skill_params[4]
			target_scaling_skill = [0, 1, 2, 2.75 , 2.75 + 0.75**2]
			skill_hps = final_atk/atk_interval *(self.attack_speed+aspd)/100 * (1+self.buff_fragile) * target_scaling_skill[targets] * 0.5
		avg_hps = (skill_hps * self.skill_duration + base_hps * skill_down_duration)/(self.skill_duration + skill_down_duration)
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Mulberry(Healer):
	def __init__(self, params: PlotParameters, **kwargs):
		super().__init__("Mulberry",params,[1,2],[1],2,6,1)
		if self.elite > 0 and not self.talent_dmg: self.name += " No 2.Medic"
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0] if self.talent_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 1:
			skill_factor = self.skill_params[0]
			skill_heal = final_atk * skill_factor * (1 + self.buff_fragile)
			base_heal = final_atk * (1 + self.buff_fragile)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			skill_hps = skill_heal/self.atk_interval*self.attack_speed/100
			avg_hps = avg_heal/self.atk_interval*self.attack_speed/100
		if self.skill == 2:
			atk_interval = self.atk_interval * self.skill_params[0]
			skill_hps = final_atk/atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))

		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Myrrh(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Myrrh",pp,[1,2],[2],1,6,2)
		if self.module == 2 and self.module_dmg: self.name += " <50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_scale * final_atk/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 1:
			skill_factor = self.skill_params[0]
			skill_heal = heal_scale * final_atk * skill_factor * (1 + self.buff_fragile) * min(self.targets,2)
			base_heal = heal_scale * final_atk * (1 + self.buff_fragile)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			skill_hps = skill_heal/self.atk_interval*self.attack_speed/100
			avg_hps = avg_heal/self.atk_interval*self.attack_speed/100
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_scale * final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile) *min(self.targets,2)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.elite > 0:
			self.name += f" + {int(heal_scale * self.talent1_params[0] * final_atk * self.targets)} on deployment"
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
		skillhps = final_atk * self.skill_params[0] * (1+self.buff_fragile)
		avghps = skillhps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skillhps)}**/0/*{int(avghps)}* + {int(extraheal)}hps to vanguards"
		return self.name

class Nearl(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Nearl",pp,[1,2],[1],1,1,1)
		if self.skill == 1: self.module_dmg = True
		if self.module == 1 and not self.module_dmg: self.name += " >50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		talent_scale = self.talent1_params[0]
		if self.module == 1:
			if self.module_lvl == 2: talent_scale += 0.03
			if self.module_lvl == 3: talent_scale += 0.05

		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			skill_hps = final_atk * heal_scale * talent_scale * self.skill_params[0] * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
		if self.skill == 2:
			self.atk_interval = 2.76
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk_skill * heal_scale * talent_scale / self.atk_interval * self.attack_speed/100 * (1+ self.buff_fragile)
			avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Nightingale(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Nightingale",pp,[1,2,3],[1,2],3,1,1)
	
	def skill_hps(self, **kwargs):
		heal_factor = 0.99 + 0.02 * self.module_lvl if self.module ==1 and self.module_lvl > 1 else 1
		targets = 4 if self.module == 2 else 3
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_factor * final_atk / self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile) * min(self.targets, targets)

		if self.skill == 1:
			atkbuff = self.skill_params[0]
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk_skill/self.atk_interval * (self.attack_speed)/100 * (1 + self.buff_fragile) * min(self.targets, targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		if self.skill == 2:
			base_heal = heal_factor * final_atk * (1 + self.buff_fragile) * min(self.targets, targets)
			skill_heal =  final_atk * self.skill_params[0] + base_heal * min(self.targets, targets)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[3] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			avg_hps = avg_heal/self.atk_interval*(self.attack_speed)/100
			self.name += f": {int(base_hps)}/*{int(avg_hps)} including the shield*"
			return self.name
		if self.skill == 3:
			atkbuff = self.skill_params[0]
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk_skill/self.atk_interval * (self.attack_speed)/100 * (1 + self.buff_fragile) * min(self.targets, targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Nightmare(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Nightmare",pp,[1],[2],1,1,2)
		if self.module == 2 and self.module_dmg: self.name += " *vs elite*"
	
	def skill_hps(self, **kwargs):
		aspd = self.talent1_params[1] if self.module == 1 and self.module_lvl > 1 else 0
		if self.skill == 1:
			heal_scale = self.skill_params[0]
			sp_boost = self.sp_boost + 1/self.atk_interval*self.attack_speed/100 if self.module == 2 and self.module_dmg else self.sp_boost
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skillhps = heal_scale * final_atk/self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile) * min(self.targets, self.skill_params[1])
			avghps = (skillhps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1 + sp_boost))
			self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
		return self.name

class NineColoredDeer(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("NineColoredDeer",pp,[1,2],[1],2,1,1)
	
	def skill_hps(self, **kwargs):
		heal_factor = 1 if self.module == 1 else 0.75
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval *(self.attack_speed+self.skill_params[0])/100 * (1+self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Nowell(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Nowell",pp,[1,2],[2],2,1,2)
		if self.talent_dmg and self.elite > 0: self.name += " vsNegStat"
		if not self.module == 2 and not self.trait_dmg: self.name += " atRange"
	
	def skill_hps(self, **kwargs):
		ranged_heal = 1 if self.module == 2 or self.trait_dmg else 0.8
		heal_scale = self.talent1_params[0] if self.talent_dmg and self.elite > 0 else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * ranged_heal
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = final_atk/self.atk_interval * (self.attack_speed+self.skill_params[1])/100 * (1+self.buff_fragile) * ranged_heal * heal_scale
			avg_hps = (base_hps * self.skill_cost / (1+ self.sp_boost) + skill_hps * self.skill_duration)/ (self.skill_duration + self.skill_cost / (1+ self.sp_boost))
		if self.skill == 2:
			skill_scale = self.skill_params[3]
			skill_hps = skill_scale * heal_scale * final_atk * (1 + self.buff_fragile) * min(self.targets, self.skill_params[0]) + base_hps
			skill_uptime = min(1, 12 / (self.skill_cost / (1+ self.sp_boost) + 1.2))
			avg_hps = skill_hps * skill_uptime + base_hps * (1 - skill_uptime)
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
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

class Papyrus(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Papyrus",pp,[1,2],[],2,6,0)
	
	def skill_hps(self, **kwargs):
		targets = min(self.targets,4)
		target_scaling = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2]
		target_scaling_skill = [0, 1, 1.75, 1.75 + 0.75**2, 1.75 + 0.75**2 + 0.75**3]
		shield_scale = self.talent1_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[1]) + self.buff_atk_flat

		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * target_scaling[targets]
		base_hps_shield = base_hps + shield_scale * final_atk /self.atk_interval * self.attack_speed/100 * min(self.targets,3)

		if self.skill == 1:
			shield_scale *= self.skill_params[1]
			skill_scale = self.skill_params[0]
			skill_hps = skill_scale * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * target_scaling[targets]
			skill_hps_shield = skill_hps + shield_scale * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * min(self.targets,3)
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/self.attack_speed*100
			atks_per_skillactivation = sp_cost / atkcycle
			avg_hps = skill_hps
			avg_hps_shield = skill_hps_shield
			if atks_per_skillactivation > 1:
				avg_hps = (skill_hps + (atks_per_skillactivation - 1) * base_hps) / atks_per_skillactivation
				avg_hps_shield = (skill_hps_shield + (atks_per_skillactivation - 1) * base_hps_shield) / atks_per_skillactivation
		if self.skill == 2:
			atk_interval = self.atk_interval + self.skill_params[0]
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[1]) + self.buff_atk_flat
			skill_hps = final_atk_skill/atk_interval *self.attack_speed/100 * (1+self.buff_fragile) * target_scaling_skill[targets]
			skill_hps_shield = skill_hps + shield_scale * final_atk/atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * targets
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost/(1+self.sp_boost))/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			avg_hps_shield = (skill_hps_shield * self.skill_duration + base_hps_shield * self.skill_cost/(1+self.sp_boost))/(self.skill_duration + self.skill_cost/(1+self.sp_boost))

		self.name += f": **{int(skill_hps_shield)}**/{int(base_hps_shield)}/*{int(avg_hps_shield)}* or **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}* without the shield"
		return self.name

class Perfumer(Healer):
	def __init__(self, params: PlotParameters, **kwargs):
		super().__init__("Perfumer",params,[1,2],[2],2,6,2)
	
	def skill_hps(self, **kwargs):
		targets = 4 if self.module == 2 else 3
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		aspd = self.skill_params[1] if self.skill == 2 else 0

		base_hps = final_atk/self.atk_interval * self.attack_speed/100 * min(self.targets,targets) * (1 + self.buff_fragile)
		skill_hps = final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 *  min(self.targets,targets) * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))

		heal_factor = self.talent1_params[0]
		if self.module == 2 and self.module_lvl > 1: heal_factor += 0.005 * self.module_lvl
		aura_heal = final_atk * heal_factor * self.targets if self.elite > 0 else 0
		aura_heal_skill = final_atk_skill * heal_factor * self.targets if self.elite > 0 else 0
		aura_heal_avg = (aura_heal_skill * self.skill_duration + aura_heal * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))

		self.name += f": **{int(skill_hps+aura_heal_skill)}**/{int(base_hps+aura_heal)}/*{int(avg_hps+aura_heal_avg)}*  (**{int(aura_heal_skill)}**/{int(aura_heal)}/*{int(aura_heal_avg)}* from global aura heal)"
		return self.name

class Podenco(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Podenco",pp,[1],[1],1,6,1)
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0]
		aspd = self.talent1_params[1] if self.module == 1 and self.module_lvl > 1 else 0
		if self.skill == 1:
			atkbuff += self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skillhps = final_atk/self.atk_interval *(self.attack_speed+aspd)/100 * (1+self.buff_fragile)
			avghps = (skillhps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
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
			max_targets = 18 if self.elite > 0 else 12
			skill_hps = final_atk * skill_scale * heal_scale * (1+self.buff_fragile) * min(self.targets,max_targets)
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

class RecordKeeper(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Recordkeeper",pp,[1,2],[1],2,6,1)
		if self.module == 1 and not self.module_dmg: self.name += " vs>50%"
		if self.skill == 2 and not self.talent_dmg: self.name += " talentInactive"
	
	def skill_hps(self, **kwargs):
		aspd = self.talent1_params[0] if self.elite > 0 else 0
		if self.skill == 2 and not self.talent_dmg: aspd = 0
		module_heal = 1.15 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk * module_heal /self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
		restore = 1 if self.elite > 0 else 0

		####the actual skills
		if self.skill == 1:
			skill_factor = self.skill_params[0]
			skill_heal = final_atk * skill_factor * (1 + self.buff_fragile) * module_heal * min(self.targets,2)
			base_heal = module_heal * final_atk * (1 + self.buff_fragile)
			sp_cost = (self.skill_cost-restore)/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[2] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			skill_hps = skill_heal/self.atk_interval*(self.attack_speed+aspd)/100
			avg_hps = avg_heal/self.atk_interval*(self.attack_speed+aspd)/100
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[2]) + self.buff_atk_flat
			skill_hps = final_atk_skill * module_heal /self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile) * min(self.targets,2)
			if not self.talent_dmg:
				skill_hps = final_atk_skill * module_heal /self.atk_interval * (self.attack_speed + (self.talent1_params[0] * self.talent1_params[1]/25))/100 * (1 + self.buff_fragile) * min(self.targets,2)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class RoseSalt(Healer):
	def __init__(self, params: PlotParameters, **kwargs):
		super().__init__("RoseSalt",params,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0]
		healing_bonus = self.talent1_params[1]
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			normal_heal = final_atk * (1 + self.buff_fragile) * healing_bonus
			skill_heal = skill_scale * final_atk * (1 + self.buff_fragile) * healing_bonus
			avg_heal = skill_heal
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/(self.attack_speed/100)
			atks_per_skillactivation = sp_cost / atkcycle
			if atks_per_skillactivation > 1:
				if self.skill_params[1] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * normal_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * normal_heal) / (int(atks_per_skillactivation)+1)
			skilldown_hps = normal_heal/self.atk_interval * self.attack_speed/100 * min(self.targets,3)
			skill_hps = skill_heal/self.atk_interval * self.attack_speed/100 * min(self.targets,3)
			avg_hps = avg_heal/self.atk_interval * self.attack_speed/100 * min(self.targets,3)
		if self.skill == 2:
			atk_interval = self.atk_interval + self.skill_params[2]
			skilldown_hps = final_atk/self.atk_interval * self.attack_speed/100 * min(self.targets,3) * (1 + self.buff_fragile) * healing_bonus
			skill_hps = final_atk/atk_interval * self.attack_speed/100 * min(self.targets,3) * (1 + self.buff_fragile) * healing_bonus
			avg_hps = (skill_hps * self.skill_duration + skilldown_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))

		self.name += f": **{int(skill_hps)}**/{int(skilldown_hps)}/*{int(avg_hps)}*"
		return self.name

class Saileach(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Saileach",pp,[1,2],[1],2,1,1)
	
	def skill_hps(self, **kwargs):
		if self.skill == 1: 
			self.name += ": No heals =("
			return self.name
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skillhps = final_atk * self.skill_params[1]
		avghps = skillhps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
		return self.name

class Saria(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Saria",pp,[1,2,3],[1,2],1,1,1)
		if self.skill == 1: self.module_dmg = True
		if self.elite > 0 and not self.talent_dmg: self.name += " noStacks"
		if self.module == 1 and not self.module_dmg: self.name += " >50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		atkbuff = 5 * self.talent1_params[2] if self.talent_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat

		if self.skill == 1: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			skill_hps = final_atk * heal_scale * self.skill_params[0] * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
		if self.skill == 2: #TODO when the skill doesnt hold charges, the skill healing drops as it has to align with atk cycle
			sp_cost= self.skill_cost/(1+self.sp_boost) + 1.2
			skill_hps = final_atk * heal_scale * self.skill_params[0] * (1+ self.buff_fragile) * min(self.targets,21)
			avg_hps = skill_hps / sp_cost
		if self.skill == 3:
			skill_hps = final_atk * heal_scale * self.skill_params[0] * (1+ self.buff_fragile) * min(self.targets,25)
			avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Senshi(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Senshi",pp,[1,2],[2],1,6,2)
	
	def skill_hps(self, **kwargs):
		skill_scale = self.skill_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		if self.skill == 1:#TODO self buff with atk is possible and can actually be active with an sp boost from ptilo... ugh
			sp_cost= self.skill_cost/(1+self.sp_boost) + 3
			skill_hps = final_atk * skill_scale * (1+ self.buff_fragile)
			avg_hps = skill_hps / sp_cost
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}* "
		if self.skill == 2:
			skill_scale_2 = self.skill_params[1]
			skill_hps = final_atk * skill_scale * (1+ self.buff_fragile) * min(self.targets,9)
			extra_heal = final_atk * skill_scale_2 * (1+ self.buff_fragile) * min(self.targets,9)
			avg_hps = (extra_heal + skill_hps * 10) / (10 + self.skill_cost/(1+self.sp_boost))
			self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}* (*inlcuding the final heal of* **{int(extra_heal)}**)"
		return self.name

class Shining(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Shining",pp,[1,2,3],[2,1],2,1,1)
		if self.module_dmg:
			if self.module == 1: self.name += " <50%Hp"
			if self.module == 2: self.name += " ground"
	
	def skill_hps(self, **kwargs):
		heal_factor = 1.15 if self.module != 0 and self.module_dmg else 1
		aspd = self.talent2_params[0]
		atkbuff = 0
		if self.skill == 2 and self.module == 1 and self.module_lvl > 1: atkbuff += 0.05 + 0.1 * self.module_lvl
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		base_hps = heal_factor * final_atk / self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)

		if self.skill == 1:
			atkbuff += self.skill_params[0]
			aspd += self.skill_params[1]
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		if self.skill == 2:
			base_heal = heal_factor * final_atk * (1 + self.buff_fragile)
			skill_heal =  final_atk * self.skill_params[1] + base_heal
			sp_cost = self.skill_cost/(1+self.sp_boost) + 1.2 #sp lockout
			atkcycle = self.atk_interval/((self.attack_speed+aspd)/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avg_heal = skill_heal
			if atks_per_skillactivation > 1:
				if self.skill_params[3] > 1:
					avg_heal = (skill_heal + (atks_per_skillactivation - 1) * base_heal) / atks_per_skillactivation
				else:
					avg_heal = (skill_heal + int(atks_per_skillactivation) * base_heal) / (int(atks_per_skillactivation)+1)
			avg_hps = avg_heal/self.atk_interval*(self.attack_speed+aspd)/100
			self.name += f": {int(base_hps)}/*{int(avg_hps)} including the shield*"
			return self.name
		if self.skill == 3:
			atkbuff += self.skill_params[1]
			sp_boost = self.sp_boost
			if self.module == 1 and self.module_lvl > 1: sp_boost += 0.15 + 0.15 * self.module_lvl
			final_atk_skill = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ sp_boost))/(self.skill_duration + self.skill_cost /(1+ sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
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
			self.name += f": **{int(skill_hps)}**/{int(grassheal)}/*{int(avg_hps+grassheal)}*"
		
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
			skill_hps = self.drone_atk * min(self.targets,8) * 2
			avg_hps = skill_hps * min(1, 10 / self.skill_cost * (1 + self.sp_boost))
			skill_hps += base_hps
			avg_hps += base_hps
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class SilenceAlter(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("SilenceAlter",pp,[1,2,3],[1,2],2,6,1)
	
	def skill_hps(self, **kwargs):
		targets = 2 if self.module == 2 else 1
		heal_factor = 1 if self.module == 1 else 0.75
		if self.skill in [1,3]:
			final_atk = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile) * min(self.targets,targets)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval *(self.attack_speed+self.skill_params[0])/100 * (1+self.buff_fragile) * min(self.targets,targets)
		avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		if self.elite == 2:
			aura_heal_skill = final_atk * self.talent2_params[1] * min(self.targets,16)
			aura_heal_base = (self.atk * (1 + self.buff_atk) + self.buff_atk_flat) * self.talent2_params[1] * min(self.targets,16)
			aura_heal_avg = (aura_heal_skill * self.skill_duration + aura_heal_base * self.skill_cost/(1+self.sp_boost))/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
			self.name += f" + **{int(aura_heal_skill)}**/{int(aura_heal_base)}/*{int(aura_heal_avg)}* if allies have <50%HP (double for Rhinelab)"
		return self.name

class Skalter(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("SkadiAlter",pp,[1,2],[1],2,1,1)
		if self.elite == 2 and self.talent2_dmg and self.talent_dmg: self.name += " AHinRange"
		if self.module == 1 and not self.module_dmg: self.name += " noModBonus"
	
	def skill_hps(self, **kwargs):
		targets = 9 if self.elite == 0 else 8+13
		atkbuff = self.talent2_params[0] if self.elite == 2 else 0
		if self.module == 1 and self.module_dmg: atkbuff += 0.08
		if self.elite == 2 and self.talent_dmg and self.talent2_dmg: atkbuff = self.talent2_params[1]
		final_atk = self.atk * (1 + self.buff_atk+atkbuff) + self.buff_atk_flat
		base_hps = final_atk * 0.1 * min(self.targets,targets)
		if self.skill == 1:
			skill_hps = final_atk * self.skill_params[1] * min(self.targets,targets)
			avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.skill == 2:
			skill_hps = final_atk * self.skill_params[2] * min(self.targets,targets)
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}"
		return self.name

class Sora(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Sora",pp,[1],[1],1,1,1)
		if self.module == 1 and not self.module_dmg: self.name += " noModBonus"
	
	def skill_hps(self, **kwargs):
		targets = 9 if self.elite == 0 else 13
		atkbuff = 0.08 if self.module == 1 and self.module_dmg else 0
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		if self.elite == 0: self.talent1_params[1] = 0
		base_hps = final_atk * 0.1 * min(self.targets,targets)
		if self.skill == 1:
			skill_hps = final_atk * self.skill_params[0] * min(self.targets,targets)
			skill_cost = self.skill_cost if self.elite == 0 else self.skill_cost * ((1 - self.talent1_params[0]) + self.talent1_params[0] * self.talent1_params[1])
			avg_avg_hps = (skill_hps * self.skill_duration + base_hps * skill_cost /(1+ self.sp_boost))/(self.skill_duration + skill_cost /(1+ self.sp_boost))
			max_avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost *(1-self.talent1_params[1]) /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost *(1-self.talent1_params[1]) /(1+ self.sp_boost))
			min_avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_avg_hps)}* ranging from *{int(min_avg_hps)}* to *{int(max_avg_hps)}*"
		return self.name

class Spot(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Spot",pp,[1],[],1,6,0)
	
	def skill_hps(self, **kwargs):
		self.atk_interval = 2.5
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		skill_hps = final_atk_skill / self.atk_interval * self.attack_speed/100 * (1+ self.buff_fragile)
		avg_hps = skill_hps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Sussurro(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Sussurro",pp,[1,2],[1],2,6,1)
		if self.elite > 0 and self.talent_dmg: self.name += " ≤10DP"
		if self.module_dmg and self.module == 1: self.name += " <50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_factor_talent = self.talent1_params[1] if self.elite > 0 and self.talent_dmg else 1
		heal_factor = 1.15 if self.module == 1 and self.module_dmg else 1

		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_factor * heal_factor_talent * final_atk / self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
		if self.skill == 1:
			skill_hps = heal_factor * heal_factor_talent * final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		if self.skill == 2:
			aspd = self.skill_params[1]
			skill_hps = heal_factor * heal_factor_talent * final_atk_skill/self.atk_interval * (self.attack_speed+aspd)/100 * (1 + self.buff_fragile)
		avg_hps = (skill_hps * self.skill_duration + base_hps * self.skill_cost /(1+ self.sp_boost))/(self.skill_duration + self.skill_cost /(1+ self.sp_boost))
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class SwireAlter(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("SwireAlter",pp,[1],[1,2],1,1,1)
		if not self.talent_dmg: self.name += " noCoinStacks"
		if self.module == 2 and not self.module_dmg: self.name += " noModStacks"
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[3] * self.talent1_params[2] if self.talent_dmg else 0
		if self.module == 2 and self.module_dmg: atkbuff += 0.2
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		skill_hps = final_atk * self.skill_params[0] * (1+ self.buff_fragile)
		self.name += f": **{int(skill_hps)}**/0/*{int(skill_hps/3)}*"
		return self.name

class ThornsAlter(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("ThornsAlter",pp,[1,2],[1],1,1,1)
	
	def skill_hps(self, **kwargs):
		atkbuff = self.talent1_params[0] if self.module == 1 and self.module_lvl > 1 else min(self.talent1_params)
		aspd = self.talent2_params[0] if self.elite > 2 else 0
		extra_duration = max(self.talent1_params)
		final_atk = self.atk * (1 + self.buff_atk + atkbuff) + self.buff_atk_flat
		base_hps = 0
		heal_scale = self.skill_params[0] if self.skill == 1 else self.skill_params[9]
		duration = self.skill_params[1] if self.skill == 1 else self.skill_params[8]
		sp_cost = self.skill_cost/(1 + self.sp_boost) + 1.2
		if self.skill == 1: sp_cost += sp_cost % (self.atk_interval/(self.attack_speed+aspd)*100) #thorns doesnt hold charges
		skill_hps = final_atk * heal_scale * min(self.targets,9)
		avg_hps = skill_hps * (duration + extra_duration)/sp_cost
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Tsukinogi(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Tsukinogi",pp,[1,2],[1],1,1,1)
	
	def skill_hps(self, **kwargs):
		heal_factor = 1 if self.module == 1 else 0.75
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk/self.atk_interval *self.attack_speed/100 * (1+self.buff_fragile)
		if self.skill == 2:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = self.skill_params [2] * final_atk * min(self.targets, 16)
		avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name

class Tuye(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Tuye",pp,[1,2],[2],2,6,2)
		if self.skill == 2: self.module_dmg = True
		if self.module == 2 and self.module_dmg: self.name += " <50%Hp"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 2 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = heal_scale * final_atk/self.atk_interval * self.attack_speed/100 * (1+self.buff_fragile)
		if self.skill == 1:
			skill_scale = self.skill_params[0]
			skill_hps = final_atk * (heal_scale * (1+self.buff_fragile) + skill_scale) 
			avg_hps = base_hps + skill_hps / self.skill_cost * (1+ self.sp_boost)
			if self.elite > 0:
				base_hps_ideal = final_atk * self.talent1_params[1] / 4 * (1+self.buff_fragile)
				skill_hps_ideal = final_atk * (self.talent1_params[1]* heal_scale * (1+self.buff_fragile) +skill_scale) 
				avg_hps_ideal = base_hps_ideal + skill_hps_ideal / self.skill_cost * (1+ self.sp_boost)
				self.name += f": ideal talent usage **{int(skill_hps_ideal)}**/{int(base_hps_ideal)}/*{int(avg_hps_ideal)}*, realistic"
			self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_scale * final_atk_skill/ self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
			if self.elite > 0:
				base_hps_ideal = heal_scale * final_atk * self.talent1_params[1] / 4 * (1+self.buff_fragile)
				skill_hps_ideal = heal_scale * self.talent1_params[1] * final_atk_skill/ 4 * (1 + self.buff_fragile)
				self.name += f": ideal talent usage **{int(skill_hps_ideal)}**/{int(base_hps_ideal)}, realistic"
			self.name += f": **{int(skill_hps)}**/{int(base_hps)} + up to 3 emergency heals of {int(final_atk_skill * heal_scale * self.skill_params[2])}"
		return self.name

class UOfficial(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("UOfficial",pp,[],[],0,6)
	
	def skill_hps(self, **kwargs):
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk * 0.1 * min(self.targets,9)
		self.name += f": *{int(base_hps)}*"
		return self.name

class Wanqing(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Wanqing",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		print(self.skill_params)
		if self.skill == 1: 
			self.name += ": No heals =("
			return self.name
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skillhps = final_atk * self.skill_params[1] * (1+self.buff_fragile) * min(self.targets,9)
		avghps = skillhps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
		return self.name

class Warfarin(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Warfarin",pp,[1,2],[1],1,1,1)
		if self.module == 1 and not self.module_dmg: self.name += " >50%Hp"
		if self.skill == 1:
			try:
				self.target_hp = max(100,kwargs['hp'])
			except KeyError:
				self.target_hp = 1000 * (self.elite + 1)
			self.name += f" {int(self.target_hp)}Hp target"
	
	def skill_hps(self, **kwargs):
		heal_scale = 1.15 if self.module == 1 and self.module_dmg else 1
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk * heal_scale /self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)

		if self.skill == 1:
			base_heal = heal_scale * final_atk * (1 + self.buff_fragile)
			skill_heal =  self.skill_params[0] * self.target_hp * heal_scale * (1 + self.buff_fragile) + base_heal
			avg_heal = (base_heal * self.skill_cost + skill_heal)/(self.skill_cost+1)
			skill_hps = skill_heal/self.atk_interval * self.attack_speed/100
			avg_hps = avg_heal/self.atk_interval * self.attack_speed/100

		if self.skill == 2:
			final_atk_skill = self.atk * (1 + self.buff_atk + self.skill_params[0]) + self.buff_atk_flat
			skill_hps = heal_scale * final_atk_skill/self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
			avg_hps = (skill_hps * 15 + base_hps * (self.skill_cost /(1+ self.sp_boost) - 15)) / (self.skill_cost /(1+ self.sp_boost))
			if (self.skill_cost /(1+ self.sp_boost)) <= 15: avg_hps = skill_hps
		self.name += f": **{int(skill_hps)}**/{int(base_hps)}/*{int(avg_hps)}*"
		return self.name

class Whisperain(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Whisperain",pp,[1,2],[1],2,1,1)
		if not self.trait_dmg: self.name += " atRange"
	
	def skill_hps(self, **kwargs):
		range_heal = 1 if self.trait_dmg else 0.8
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		base_hps = final_atk * range_heal /self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
		passive_heal = 0 if self.elite == 0 else self.talent1_params[0] * final_atk
		
		####the actual skills
		if self.skill == 1:
			base_heal = range_heal * final_atk * (1 + self.buff_fragile)
			skill_heal =  final_atk * self.skill_params[0] * range_heal + passive_heal * self.skill_params[1]
			avg_heal = (base_heal * self.skill_cost + skill_heal)/(self.skill_cost+1)
			avg_hps = avg_heal/self.atk_interval * self.attack_speed/100
			self.name += f": *{int(avg_hps)}*"
			if self.module == 1:
				self.name += f" + {int(passive_heal)} passive to self"

		if self.skill == 2:
			atk_interval = self.atk_interval * 0.8 
			duration = self.skill_params[1]
			up_time = duration / atk_interval * self.attack_speed/100
			passive_heal_skill = passive_heal * self.skill_params[3] 
			skill_hps = final_atk* range_heal / self.atk_interval * self.attack_speed/100 * (1 + self.buff_fragile)
			self.name += f": **{int(skill_hps + passive_heal_skill * min(self.targets,up_time))}**/{int(base_hps)}"
			if self.module == 1:
				self.name += f" + **{int(passive_heal_skill)}**/{int(passive_heal)} passive to self"
		return self.name

class Xingzhu(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Xingzhu",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		heal_factor = 1 if self.module == 1 else 0.75
		if self.skill == 1:
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			max_targets = 16 if self.elite > 0 else 12
			skill_hps = final_atk * self.skill_params[0] * heal_factor * (1+self.buff_fragile) * min(self.targets,max_targets)
			avg_hps = skill_hps / self.skill_cost * (1+ self.sp_boost)
		if self.skill == 2:
			aspd = self.skill_params[0]
			final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
			skill_hps = heal_factor * final_atk * min(self.targets, 2) / self.atk_interval * (self.attack_speed+aspd)/100 * (1+self.buff_fragile)
			skill_hps += final_atk * self.skill_params[3] * min(self.targets,2)
			avg_hps = (skill_hps * self.skill_duration)/(self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skill_hps)}**/0/*{int(avg_hps)}*"
		return self.name
#################################################################################################################################################


healer_dict = {"amiya": AmiyaMedic, "amiyamedic": AmiyaMedic, "medicamiya": AmiyaMedic, "ansel": Ansel, "bassline": Bassline, "blemishine": Blemishine, "breeze": Breeze, "ceylon": Ceylon, "chestnut": Chestnut, "ce": CivilightEterna, "civilighteterna": CivilightEterna, "eterna": CivilightEterna, "civilight": CivilightEterna, "theresia": CivilightEterna, "doc": Doc, "eyja": Eyjaberry, "eyjaalter": Eyjaberry, "eyjafjallaalter": Eyjaberry, "eyjafjalla": Eyjaberry, "eyjaberry": Eyjaberry,
			   "folinic": Folinic, "gavial":Gavial, "gummy": Gummy, "harold": Harold, "haruka": Haruka, "heidi": Heidi, "hibiscus": Hibiscus, "honey": Honeyberry, "honeyberry": Honeyberry, "hung": Hung, "kaltsit": Kaltsit, "lancet2": Lancet2, "lumen": Lumen, "mon3tr": Mon3tr, "m3": Mon3tr, "mulberry": Mulberry, "myrrh": Myrrh, "myrtle": Myrtle,"nearl":Nearl,"nightingale":Nightingale, "nightmare":Nightmare,"ncd": NineColoredDeer, "ninecoloreddeer": NineColoredDeer, "nowell": Nowell,
			   "paprika": Paprika,"papyrus": Papyrus, "perfumer": Perfumer, "podenco": Podenco, "ptilopsis": Ptilopsis, "ptilo": Ptilopsis, "purestream": Purestream, "quercus": Quercus, "recordkeeper": RecordKeeper, "keeper": RecordKeeper, "rosesalt": RoseSalt, "saileach":Saileach,"saria": Saria, "senshi": Senshi, "shining": Shining, "shu": Shu, "silence": Silence, "silencealter": SilenceAlter, "silence2": SilenceAlter,
			   "skadi": Skalter, "skalter": Skalter, "skaldialter": Skalter, "sora": Sora, "spot":Spot, "sussurro": Sussurro, "sus": Sussurro, "amongus": Sussurro, "swire": SwireAlter, "swirealt": SwireAlter, "swirealter": SwireAlter, "thorns": ThornsAlter, "thornsalter": ThornsAlter, "lobster": ThornsAlter, "tsukinogi": Tsukinogi, "tuye": Tuye, "uofficial": UOfficial, "eureka": UOfficial, "wanqing": Wanqing, "warfarin":Warfarin,"whisperain":Whisperain, "xingzhu": Xingzhu}

healers = ["Amiya","Ansel","Bassline","Blemishine","Breeze","Ceylon","Chestnut","CivilightEterna","Doc","Eyjafjalla","Folinic","Gavial","Gummy","Harold","Haruka","Heidi","Hibiscus","Honeyberry","Hung","Kaltsit","Lancet2","Lumen","Mon3tr","Mulberry","Myrrh","Myrtle","Nearl","Nightingale","Nightmare","NineColoredDeer","Nowell","Paprika","Papyrus","Perfumer","Podenco","Ptilopsis","Purestream","Quercus","RecordKeeper","RoseSalt","Saileach","Saria","Senshi","Shining","Shu","Silence","SilenceAlter","Skalter","Sora","Spot","Sussurro","SwireAlt","Thorns","Tsukinogi","Tuye","UOfficial","Wanqing","Warfarin","Whisperain","Xingzhu"]