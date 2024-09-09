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

class Example(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=90
		lvl1atk = 1000  #######including trust
		maxatk = 2000
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 100
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"OPNAME Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"OPBNAME P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,self.targets)

		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
			
	
	def skill_hps(self, **kwargs):
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

			
		####the actual skills
		if self.skill == 1:
			final_atk_down = self.base_atk * (1+atkbuff) + self.buffs[1]
			duration = 30 + 2 * self.mastery
			sp_cost = 50 - self.mastery
			sp_cost = sp_cost / (1 + self.boost)
			
			atkbuff += 0.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			skill_scale = 1
			aspd += 10
			
			skill_hps = final_atk * skill_scale / (self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			skilldown_hps = final_atk_down /(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			avg_hps = (duration * skill_hps + sp_cost * skilldown_hps) / (duration + sp_cost)
			self.name += f": **{int(skill_hps)}**/{int(skilldown_hps)}/*{int(avg_hps)}*"
		
		return self.name

class Eyjaberry(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=90
		lvl1atk = 384  #######including trust
		maxatk = 469
		self.atk_interval = 2.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,3] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Eyjaberry Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Eyjaberry P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.buffs = buffs
		self.boost = boost
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		
		first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		####the actual skills
		if self.skill == 1:
			first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			basehpstalent = 0.3 * first_atk * (1+self.buffs[3])
			basehps += basehpstalent
			atkbuff += 0.4 if self.mastery == 3 else 0.3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			skillhpstalent = 0.3 * final_atk * (1+self.buffs[3])
			skillhps += skillhpstalent
			self.name += f": **{int(skillhps)}**/{int(basehps)}, of which {int(skillhpstalent)}/{int(basehpstalent)} come from her talent"
		if self.skill == 3:
			skill_scale = 0.45 + 0.05 * self.mastery
			skillduration = 50
			skillcost = 70 if self.mastery == 0 else 69 - 3 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			basehps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			basehpstalent = 0.3 * first_atk * (1+self.buffs[3])
			basehps += basehpstalent
			skillhps = final_atk * skill_scale/(self.atk_interval/(1+aspd/100)) * 5 * (1+self.buffs[3])
			skillhps += basehpstalent
			avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
			self.name += f": **{int(skillhps)}**/{int(basehps)}/{int(avghps)}, of which {int(basehpstalent)} comes from her talent, which can realistically be active on 5 targets for a total of **{int(skillhps + 4 * basehpstalent)}** hps"

		
		#final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		#skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		#avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
		#self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
		return self.name


class Lumen(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=90
		lvl1atk = 477  #######including trust
		maxatk = 585
		self.atk_interval = 2.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lumen Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lumen P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		healscale = 0.85
		
		first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.9 if self.mastery == 3 else 0.7 + 0.05* self.mastery
			skillduration = 30
			skillcost = 30 if self.mastery == 3 else 32
		if self.skill == 2:
			self.atk_interval -= 2.1 if self.mastery == 3 else 1.9
			skillduration = 40 if self.mastery == 3 else 36 + self.mastery
			skillcost = 100
		if self.skill == 3:
			aspd += 20 if self.mastery == 0 else 30
			atkbuff += 0.4 + 0.05 * self.mastery
			skillcost = 50 if self.mastery == 3 else 57 - 2 * self.mastery
			skill_scale = 1.5 if self.mastery == 0 else 1.55 + 0.15 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			if self.module == 2:
				
				self.name += f": **{int(skillhps)}**/{int(basehps)}"
			else:
				self.name += f": **{int(skillhps)}**/{int(basehps)} or **{int(skillhps*0.8)}**/{int(basehps*0.8)} at range"
		
		#final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		#skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		#avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
		#self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
		return self.name

class Myrtle(Healer):
	def __init__(self, pp, **kwargs):
		super().__init__("Myrtle",pp,[1,2],[1],2,6,1)
	
	def skill_hps(self, **kwargs):
		if self.elite < 2 and self.skill == 1: 
			self.name += "no heals =("
			return self.name
		if self.elite == 2 and self.skill == 1:
			self.name += f" {self.talent1_params[0]}hps to vanguards"
			return self.name
		extraheal = self.talent1_params[0]
		final_atk = self.atk * (1 + self.buff_atk) + self.buff_atk_flat
		skillhps = final_atk * self.skill_params[0] * (1+self.buff_fragile) * min(self.targets,9)
		avghps = skillhps * self.skill_duration / (self.skill_duration + self.skill_cost/(1+self.sp_boost))
		self.name += f": **{int(skillhps)}**/0/*{int(avghps)}* + {extraheal}hps to vanguards"
		return self.name

class Ptilopsis(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=80
		lvl1atk = 323  #######including trust
		maxatk = 390
		self.atk_interval = 2.85   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 21
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ptilopsis Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ptilopsis P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 47
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		spboost = 0.3
		if self.module == 1:
			if self.module_lvl == 2: spboost = 0.33
			if self.module_lvl == 3: spboost = 0.35
		self.boost = max(self.boost, spboost)
		
		first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.9 if self.mastery == 3 else 0.7 + 0.05* self.mastery
			skillduration = 30
			skillcost = 30 if self.mastery == 3 else 32
		if self.skill == 2:
			self.atk_interval -= 2.1 if self.mastery == 3 else 1.9
			skillduration = 40 if self.mastery == 3 else 36 + self.mastery
			skillcost = 100

			
		
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
		self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
		return self.name

class Purestream(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=70
		lvl1atk = 398  #######including trust
		maxatk = 489
		self.atk_interval = 2.85   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Purestream Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Purestream P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 32
				elif self.module_lvl == 2: self.base_atk += 26
				else: self.base_atk += 20
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		healboost = 0
		if self.module == 2:
			if self.module_lvl == 2: healboost = 0.1
			if self.module_lvl == 3: healboost = 0.2
		
		first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		basehpsrange = basehps * 0.8
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.6 + 0.3 * self.mastery
			skillheal = first_atk * skill_scale * (1+healboost) * (1+self.buffs[3])
			skillcost = 20 if self.mastery == 3 else 24 - self.mastery
			if self.module == 2:
				avghps = basehps + skillheal/(skillcost/(1+self.boost))
				self.name += f": **{int(skillheal)}**/{int(basehps)}/*{int(avghps)}*"
			else:
				avghps = basehps + skillheal/(skillcost/(1+self.boost))
				avghpsrange = basehpsrange + skillheal/(skillcost/(1+self.boost))
				self.name += f": **{int(skillheal)}**/{int(basehps)}/*{int(avghps)}* or **{int(skillheal)}**/{int(basehpsrange)}/*{int(avghpsrange)}* at range"
		if self.skill == 2:
			self.atk_interval = 0.342
			skillscale = 0.5 if self.mastery == 3 else 0.4 + 0.03 * self.mastery
			skillduration = 25
			skillcost = 60 if self.mastery == 3 else 64 - self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhps = skillscale * final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			skillhpsrange = skillhps * 0.8
			avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
			avghpsrange = (basehpsrange * skillcost/(1+self.boost) + skillhpsrange * skillduration)/(skillduration + skillcost/(1+self.boost))
			if self.module == 2:
				self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
			else:
				self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}* or **{int(skillhpsrange)}**/{int(basehpsrange)}/*{int(avghpsrange)}* at range"
		
		return self.name

class Quercus(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=80
		lvl1atk = 384  #######including trust
		maxatk = 463
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		#if self.pot > 3: self.base_atk += 21
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Quercus Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Quercus P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 20
				else: self.base_atk += 15
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		healfactor = 1 if self.module == 1 else 0.75
		
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4 if self.mastery == 3 else 0.3 + 0.03* self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhps = healfactor * final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			self.name += f": **{int(skillhps)}**/0"
		if self.skill == 2:
			aspd += 45 + 5 * self.mastery
			skillduration = 17 if self.mastery == 3 else 15
			skillcost = 28 - self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skillhps = healfactor * final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
			self.name += f": **{int(skillhps)}**/0/*{int(avghps)}*"
		return self.name

class Shu(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=90
		lvl1atk = 442  #######including trust
		maxatk = 529
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Shu Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Shu P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
			
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		
		#talent/module buffs
		grassheal = 75 if self.pot > 4 else 70
		if self.module == 1 and self.module_lvl > 1: grassheal += 10
		grassheal *= self.targets
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.5 + 0.1 * self.mastery
			sp_cost = 5 if self.mastery == 0 else 4
			sp_cost= sp_cost/(1+self.boost) + 1.2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skill_hps = final_atk * skill_scale * (1+ self.buffs[3])
			avg_skill_hps = final_atk * skill_scale * (1+ self.buffs[3]) / sp_cost
			self.name += f": **{int(skill_hps+grassheal)}**/{int(grassheal)}/*{int(avg_skill_hps+grassheal)}* or **{int(skill_hps+grassheal*1.15)}**/{int(grassheal)}/*{int(avg_skill_hps*1.15+grassheal)}* below 50%, {grassheal} coming from grass."
		
		if self.skill == 2:
			self.atk_interval = 2.5
			grassheal_skill = grassheal * 1.5 if self.mastery == 3 else grassheal * 1.4
			atkbuff += 0.9 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			sp_cost = 25 if self.mastery == 3 else 30
			sp_cost = sp_cost/(1+self.boost)
			duration = 25
			skill_hps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3]) * min(self.targets,2)
			avg_skill_hps = skill_hps * duration / (duration + sp_cost)
			avg_grass = (grassheal_skill * duration + grassheal * sp_cost) / (duration+sp_cost)
			self.name += f": **{int(skill_hps+grassheal_skill)}**/{int(grassheal)}/*{int(avg_skill_hps+avg_grass)}* or **{int(skill_hps*1.15+grassheal_skill)}**/{int(grassheal)}/*{int(avg_skill_hps*1.15+avg_grass)}* below 50%, {int(grassheal_skill)}/{grassheal}/{int(avg_grass)} coming from grass."
		
		if self.skill == 3:
			atkbuff = 0.34 if self.mastery == 0 else 0.32 + 0.06 * self.mastery
			duration = 30
			sp_cost = 45
			if self.mastery == 0: sp_cost = 50
			elif self.mastery != 3: sp_cost = 47
			sp_cost = sp_cost / (1 + self.boost)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skill_hps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			avg_skill_hps = skill_hps * duration / (duration + sp_cost)
			self.name += f": **{int(skill_hps+grassheal)}**/{int(grassheal)}/*{int(avg_skill_hps+grassheal)}* or **{int(skill_hps+grassheal*1.15)}**/{int(grassheal)}/*{int(avg_skill_hps*1.15+grassheal)}* below 50%."
			aspd += 25 if self.mastery > 1 else 20
			atkbuff += 0.25 if self.mastery > 1 else 0.2
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skill_hps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
			avg_skill_hps = skill_hps * duration / (duration + sp_cost)
			self.name += f" With enemies around:**{int(skill_hps+grassheal*1.15)}**/{int(grassheal)}/*{int(avg_skill_hps*1.15+grassheal)}*, {grassheal} coming from grass"

		return self.name

class Silence(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, buffs=[0,0,0,0], boost = 0.0, **kwargs):
		maxlvl=80
		lvl1atk = 460  #######including trust
		maxatk = 557
		self.atk_interval = 2.85   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Silence Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Silence P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 47
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		aspd += 14 if self.pot > 4 else 12
		if self.module == 1:
			aspd += 3 + self.module_lvl
			if self.module_lvl == 2: aspd += 3
			if self.module_lvl == 3: aspd += 5

		
		first_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		basehps = first_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.9 if self.mastery == 3 else 0.7 + 0.05* self.mastery
			skillduration = 30
			skillcost = 30 if self.mastery == 3 else 32
		if self.skill == 2:
			self.atk_interval -= 2.1 if self.mastery == 3 else 1.9
			skillduration = 10
			skillcost = 18 if self.mastery == 3 else 22 - self.mastery

			
		
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		skillhps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+self.buffs[3])
		avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
		self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
		return self.name

class Test():
	def __init__(self,pp,**kwargs) -> None:
		self.name = "the requested level: " + str(pp.level)
	def skill_hps(self, **kwargs):
		return self.name
#################################################################################################################################################


healer_dict = {"test":Test, "breeze":Breeze, "eyja": Eyjaberry, "eyjafjalla": Eyjaberry, "eyjaberry": Eyjaberry, "lumen": Lumen, "myrtle": Myrtle, "ptilopsis": Ptilopsis, "ptilo": Ptilopsis, "purestream": Purestream, "quercus": Quercus, "shu": Shu, "silence": Silence}

healers = ["Breeze","Eyjafjalla","Lumen","Myrtle","Ptilopsis","Purestream","Quercus","Shu"]

if __name__ == "__main__":
	for operator in healer_dict.values():
		for skill in [1,2,3]:
			operator(skill= skill).skill_hps()
	print("Seems to be working fine. Make sure the operator is added to the dictionary.")
	
	#Test individual operators:
	#print(Eyjaberry().skill_hps())
