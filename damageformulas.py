import math #fu Kjera
import numpy as np
import pylab as pl

class Operator:
	
	def avg_dps(self,defense,res):
		print("The operator has not implemented the avg_dps method")
		return -100
		
	def skill_dps(self, defense, res):
		print("The operator has not implemented the skill_dps method")
		return -100
	
	def total_dmg(self,defense,res):
		return (self.skill_dps(defense,res))
	
	def get_name(self):
		return self.name
		


class Blueprint(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
		
		if not self.trait: self.name += "w/o trait"   ##### keep the ones that apply
		if not self.talent1: self.name += " w/o talent"
		if not self.talent2: self.name += " w/o talent2"
		if self.skilldmg: self.name += " overdrive"
		if self.moduledmg and self.module == 1: self.name += " aerial target"
		
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

		if self.module == 1:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.02
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4
			atk_scale = 1
			aspd += 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps



class Absinthe(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 601  #######including trust
		maxatk = 703
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Absinthe Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Absinthe P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		#if(kwargs['bonus']): self.name += " it works"

		self.talent1 = TrTaTaSkMo[1]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
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
		if self.skill == 2 and self.module == 1 and self.module_lvl > 1: self.talent1= True
		if self.talent1: self.name += " lowHpTarget"

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		dmg_scale = 1
		#talent/module buffs
		if self.talent1:
			dmg_scale = 1.24
			if self.pot > 4: dmg_scale += 0.06
			if self.module == 1:
				if self.module_lvl == 2: dmg_scale += 0.05
				if self.module_lvl == 3: dmg_scale += 0.08
		newres = res
		if self.module == 1:
			newres = max(0,res-10)

			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)*dmg_scale	
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atk_scale = 0.75 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)*dmg_scale	
			dps = 4*hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 1: return(self.skill_dps(defense,res))
		else:
			return(self.skill_dps(defense,res) * (27 + self.mastery))

class Aciddrop(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 645  #######including trust
		maxatk = 815
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Aciddrop Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Aciddrop P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += f"ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent: self.name += " directFront"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		mindmg = 0.25
		if self.module == 1:
			aspd += 2 + self.module_lvl
			mindmg += 0.05 * (self.module_lvl - 1)
		if self.talent:
			mindmg += 0.15
			
		####the actual skills
		if self.skill == 1:
			aspd += 70 if self.mastery == 3 else 50 + 6 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * mindmg)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.32 if self.mastery == 0 else 0.31 + 0.03 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * mindmg)
			dps = 2*hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Amiya(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 584  #######including trust
		maxatk = 682
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Amiya Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Amiya P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		####the actual skills
		if self.skill == 1:
			aspd += 60 + 10 * self.mastery		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atk_scale = 0.45 + 0.05 * self.mastery
			hits = 7 if self.mastery == 0 else 8		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hits * hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			atkbuff += 2.3 if self.mastery == 3 else 1.6 + 0.2 * self.mastery	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			dps = final_atk/(self.atk_interval/(1+aspd/100))			
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3: return(self.skill_dps(defense,res) * 30)
		else:
			return(self.skill_dps(defense,res))
	
class AmiyaGuard(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 577  #######including trust
		maxatk = 702
		self.atk_interval = 1.25   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Guardmiya Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Guardmiya P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.skilldmg = TrTaTaSkMo[3]

		if self.skill == 2:
			if self.skilldmg: self.name += " 3kills"
			else: self.name += " no kills"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		atkbuff += 0.14
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-res/100), final_atk * 0.05)
			dps = 2*hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			if self.skilldmg:
				atkbuff += 3 * (0.25 + 0.05 * self.mastery)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			dps = final_atk/(self.atk_interval/(1+aspd/100))
		return dps
		
class Andreana(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 917  #######including trust
		maxatk = 1110
		self.atk_interval = 2.7   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Andreana Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Andreana P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 91
				elif self.module_lvl == 2: self.base_atk += 81
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg: self.name += " atMaxRange"

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		aspd += 12
		if self.pot > 4: aspd += 2

		if self.module == 1:
			if self.module_lvl == 3 : aspd += 8
			elif self.module_lvl == 2: aspd += 5
			if self.moduledmg: atk_scale = 1.15
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6+ 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 1.9+ 0.15 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))	
		
		return dps

class Angelina(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 524  #######including trust
		maxatk = 617
		self.atk_interval = 1.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Angelina Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Angelina P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 20
				elif self.module_lvl == 2: self.base_atk += 15
				else: self.base_atk += 10
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		aspd += 8 if self.pot == 6 else 7
		if self.module == 1:
			aspd += 3 + self.module_lvl
			if self.module_lvl == 2: aspd += 3
			if self.module_lvl == 3: aspd += 5
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.8 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			self.atk_interval = 0.285
			skill_scale = 0.45 if self.mastery == 3 else 0.4
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 1.05 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 5)
		return dps

class April(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 507  #######including trust
		maxatk = 603
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"April Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"April P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 32
				elif self.module_lvl == 2: self.base_atk += 28
				else: self.base_atk += 23
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg: self.name += " groundEnemies"

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs

		if self.module == 2 and self.moduledmg:
			aspd += 8
			
		####the actual skills
		if self.skill == 1:
			sp_cost = 4 if self.mastery == 0 else 3
			atk_scale = 2 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skilldmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			avgdmg = (sp_cost * hitdmg + skilldmg) / (sp_cost + 1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Archetto(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 48
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 32
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 24
				elif self.module_lvl == 2: self.base_atk += 22
				else: self.base_atk += 17
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.module_lvl > 1 and self.talent1 and self.skill != 3: self.name += " +2ndSniper"
		
		if self.moduledmg and self.module == 1: self.name += " aerial target"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			aoedmg = max(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05)
			
			#figuring out the chance of the talent to activate during downtime
			base_cycle_time = (sp_cost+1)/(1+aspd/100)
			talents_per_base_cycle = base_cycle_time / recovery_interval
			failure_rate = 1.8 / (sp_cost + 1)  #1 over sp cost because thats the time the skill would technically be ready, the bonus is for sp lockout. (basis is a video where each attack had 14 frames, but it was 25 frames blocked)
			talents_per_base_cycle *= 1-failure_rate
			new_spcost = max(1,sp_cost - talents_per_base_cycle)
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			targets = min(5, self.targets)
			totalhits = [5,9,12,14,15]
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + sprecovery/sp_cost * skilldmg * totalhits[targets-1]
		
		if self.skill == 3:
			atkbuff += 0.15 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * 3
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 2)
		return dps

class Arene(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 573  #######including trust
		maxatk = 695
		self.atk_interval = 1.3  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 18
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Arene Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Arene P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 39
				else: self.base_atk += 33
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 1 and self.talent1:
			self.trait = False
		
		if not self.trait and self.skill == 1: self.name += " rangedAtk"   ##### keep the ones that apply
		if self.talent1: self.name += " vsDrones"
		if self.module == 2 and self.targets == 1 and self.moduledmg: self.name += " +12aspd(mod)"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atk_scale = 1.43 if self.pot > 4 else 1.4
			if self.module == 2:
				if self.module_lvl == 2: atk_scale += 0.1
				if self.module_lvl == 3: atk_scale += 0.15
		if self.module == 2 and (self.targets > 1 or self.moduledmg): aspd += 12
		
		if not self.trait and self.skill != 2:
			atk_scale *= 0.8
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.5 if self.mastery == 3 else 1.3 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)

			dps = 2*hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			skill_scale = 1.6 if self.mastery == 3 else 1.4 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * skill_scale * atk_scale  * (1-res/100), final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(2,self.targets)
		return dps

class Asbestos(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 546  #######including trust
		maxatk = 673
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1

		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Asbestos Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Asbestos P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1

		####the actual skills
		if self.skill == 1:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.6 + 0.1 * self.mastery
			self.atk_interval = 2.0
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps

class Ascalon(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 763  #######including trust
		maxatk = 954
		self.atk_interval = 3.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		#if self.pot > 3: self.base_atk += 100
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ascalon Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ascalon P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 53
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " 1Stack"
		else: self.name += " 3Stacks"
		if not self.talent2: self.name += " NoRangedTiles"
		else: self.name += " nextToRangedTile"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		talentstacks = 3 if self.talent1 else 1
		talentscale = 0.11 if self.module == 1 and self.module_lvl == 3 else 0.1

		aspd += 14 if self.talent2 else 8
		if self.pot > 4: aspd += 2
		
		final_atk = 0
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.7 + 0.1 * self.mastery
			if self.mastery == 2: skill_scale = 1.8
			if self.mastery == 3: skill_scale += 0.1
			sp_cost = 8 if self.mastery < 2 else 7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * 2
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			atkbuff += 0.9 + 0.1 * self.mastery
			if self.mastery > 1: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			self.atk_interval = 2.0
			atkbuff += 0.2 + 0.1 * self.mastery	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		dps += self.targets * final_atk * talentstacks * talentscale * max(1-res/100, 0.05)
		return dps

class Ash(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 522  #######including trust
		maxatk = 624
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ash Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ash P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 22
				elif self.module_lvl == 2: self.base_atk += 19
				else: self.base_atk += 14
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if self.skilldmg and self.skill == 2: self.name += " vsStunned"
		if self.moduledmg:
			if self.module == 1: self.name += " aerial target"
			if self.module == 2: self.name += " groundEnemy"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs

		if self.moduledmg:
			if self.module == 1: atk_scale = 1.1
			if self.module == 2: aspd += 8
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.15 if self.mastery == 3 else 0.11 + self.mastery * 0.01	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * 2
		if self.skill == 2:
			self.atk_interval = 0.2	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.skilldmg:
				skill_scale = 2.5 if self.mastery == 3 else 2.1 + 0.1 * self.mastery
				bonusdmg = 1
				if self.module == 1:
					if self.module_lvl == 2: bonusdmg = 1.07
					if self.module_lvl == 3: bonusdmg = 1.1
				hitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05) * bonusdmg
				dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		return dps

class Ashlock(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 767  #######including trust
		maxatk = 915
		self.atk_interval = 2.8   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ashlock Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ashlock P{self.pot} S{self.skill}"
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
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " LowTalent"

		if self.moduledmg: self.name += " blockedTarget"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 0.08
		if self.pot > 4: atkbuff += 0.02
		if self.talent1:
			atkbuff += 0.08
		
		if self.module == 1:
			if self.moduledmg: atk_scale = 1.1
			if self.talent1:
				if self.module_lvl == 3: atkbuff += 0.04
			else:
				if self.module_lvl > 1: atkbuff += 0.02
		
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			if self.mastery == 3: interval = self.atk_interval * 0.35
			else: interval = self.atk_interval * 0.5
			atkbuff += 0.4 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(interval/(1+aspd/100)) * self.targets
			
			
		return dps

class Astesia(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 564  #######including trust
		maxatk = 690
		self.atk_interval = 1.25  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Astesia Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Astesia P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]

		
		
		if self.talent1: self.name += " maxStacks"
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			aspd += 25
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.5 if self.mastery == 3 else 0.4 + 0.03 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.8 if self.mastery == 3 else 0.6 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		
		return dps

class Astgenne(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 597  #######including trust
		maxatk = 705
		self.atk_interval = 2.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 4: self.base_atk += 28
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Astgenne Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Astgenne P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 74
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " maxStacks"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			aspd += 20
			if self.module == 2:
				aspd += 4 * (self.module_lvl - 1)
		
		targetscaling = [0,1,2,3,4] if self.module == 2 else [0, 1, 1.85, 1.85+0.85**2, 1.85+0.85**2+0.85**3]
		targets = min(4, self.targets)
		####the actual skills
		if self.skill == 1:
			sp_cost = 7 if self.mastery == 3 else 8
			
			atk_scale = 1.1 + 0.05 * self.mastery
			aspd += 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg * targetscaling[targets] * min(targets,2) + (atks_per_skillactivation - 1) * hitdmg * targetscaling[targets]) / atks_per_skillactivation	
			
			dps = avghit/(self.atk_interval/(1+aspd/100))

		
		if self.skill == 2:
			atkbuff += 0.25 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = hitdmg/(self.atk_interval/(1+aspd/100)) * 2 * targetscaling[targets]
		return dps

class Aurora(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skilldmg =  max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			avgdmg = hitdmg
			if self.skilldmg: avgdmg = 2/3 * hitdmg + 1/3 * skilldmg
						
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps
		
class Bagpipe(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 578  #######including trust
		maxatk = 671
		self.atk_interval = 1  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Bagpipe Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Bagpipe P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 73
				elif self.module_lvl == 2: self.base_atk += 64
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 2: self.name += " lowHpTarget"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		crate = 0.25
		if self.pot > 2: crate += 0.03
		cdmg = 1.3
		if self.module == 2:
			cdmg += 0.05 * (self.module_lvl -1)
			if self.module_lvl == 2: crate += 0.05
			if self.module_lvl == 3: crate += 0.08
			if self.moduledmg: atk_scale = 1.15

			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			if self.mastery == 3: atkbuff+= 0.02
			aspd += 45 if self.mastery == 3 else 35

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			critdmg = max(final_atk *atk_scale *cdmg - defense, final_atk* atk_scale * cdmg * 0.05)
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			sp_cost = 4 if self.mastery == 3 else 5
			if self.mastery == 3: skill_scale = 2
			else: skill_scale = 1.6 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			critdmg = max(final_atk *atk_scale *cdmg - defense, final_atk* atk_scale * cdmg * 0.05)
			
			skillhit = max(final_atk *atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skillcrit = max(final_atk *atk_scale * skill_scale *cdmg - defense, final_atk* atk_scale * skill_scale * cdmg * 0.05)
			
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			avgskill = crate * skillcrit * min(2, self.targets) + (1-crate) * skillhit
			avgskill *= 2
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			
			avghit = avgskill
			if atks_per_skillactivation > 1:
				avghit = (avgskill + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		
		
		if self.skill == 3:
			atkbuff += 0.9 + 0.1 * self.mastery
			self.atk_interval = 1.7
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			critdmg = max(final_atk *atk_scale *cdmg - defense, final_atk* atk_scale * cdmg * 0.05)
			avgdmg = crate * critdmg * min(2, self.targets) + (1-crate) * hitdmg
			dps = 3*avgdmg/(self.atk_interval/(1+aspd/100)) 
		return dps
	
class Beehunter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Bibeak(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 543 
		maxatk = 682
		self.atk_interval = 1.3  
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 22
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Bibeak Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Bibeak P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(2,max(1,targets))
		self.talent1 = TrTaTaSkMo[1]

		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3:
					self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " w/0 talent"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		dmg_multiplier = 1
		#talent/module buffs
		if self.talent1:
			buffcount = 5
			if self.pot > 4: buffcount += 1
			if self.module == 1:
				if self.module_lvl > 1:
					buffcount += 1
				if self.module == 2: atkbuff += buffcount*0.01
				if self.module == 3: atkbuff += buffcount*0.02
			aspd += buffcount * 6

		if self.module == 1:
			dmg_multiplier = 1.1
			
		####the actual skills
		if self.skill == 1:
			atk_scale = 1.5 + 0.1 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)*dmg_multiplier
			skillartsdmg = max(final_atk* atk_scale *(1-res/100), final_atk * atk_scale * 0.05)*dmg_multiplier
			sp_cost = 2 if self.mastery == 3 else 3
			
			avgphys = 2 * (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avgarts = 0 if self.targets == 1 else skillartsdmg/(sp_cost +1)
			
			dps = (avgphys+avgarts)/(self.atk_interval/(1+aspd/100))
		else:
			atk_scale = 1.7 + 0.1 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillartsdmg = max(final_atk* atk_scale *(1-res/100), final_atk * atk_scale * 0.05)*dmg_multiplier
			sp_cost = 10 - self.mastery
			
			avgarts = skillartsdmg/sp_cost * min(self.targets, 6)
			
			dps = (hitdmg+avgarts)/(self.atk_interval/(1+aspd/100))
		return dps
	
class Blaze(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 641  #######including trust
		maxatk = 825
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Blaze Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Blaze P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(3,max(1,targets))
		self.talent2 = TrTaTaSkMo[2]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 86
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.talent2 and not self.skill == 2: self.name += " w/0 talent2"
		
		if self.module == 1:
			if self.moduledmg: self.name += " vsBlocked"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		if self.moduledmg and self.module == 1: atk_scale = 1.1
		
		#talent/module buffs
		if (self.talent2 or self.skill == 2) and self.module == 1: #talent buff is active when s2 gets activated
			if self.module_lvl == 2:
				atkbuff += 0.04
				aspd += 6
			if self.module_lvl == 3:
				atkbuff += 0.06
				aspd += 12
			

			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.25 + 0.2 * self.mastery
			if self.mastery == 3: skill_scale += 0.05
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) * min(self.targets, 3)
			
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * min(self.targets,3)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Blemishine(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 492  #######including trust
		maxatk = 581
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Blemishine Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Blemishine P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.talent2 = TrTaTaSkMo[2]
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 69
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 53
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 43
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if self.talent2: self.name += " vsSleep"
		else: self.name += " w/o sleep"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2:
			atk_scale = 1.4
			if self.pot > 4: atk_scale += 0.04
			if self.module == 2:
				atk_scale += 0.1 * (self.module_lvl - 1)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.2 + 0.1 * self.mastery
			if self.mastery == 3: skill_scale += 0.1
			sp_cost = 5 if self.mastery == 0 else 4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			artsfactor = 0.7 + 0.1 * self.mastery
			artsdmg = hitdmgarts = max(final_atk * atk_scale * artsfactor * (1-res/100), final_atk * atk_scale * artsfactor * 0.05)
			dps = (hitdmg+artsdmg)/(self.atk_interval/(1+aspd/100))
		return dps
	
class BluePoison(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 513  #######including trust
		maxatk = 610
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"BluePoison Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"BluePoison P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 26
				else: self.base_atk += 20
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg and self.module == 2: self.name += " GroundTargets"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		artsdmg = 85 if self.pot > 4 else 75
		if self.module == 2:
			artsdmg += (self.module_lvl -1) * 10
			aspd += 1 + self.module_lvl
			if self.moduledmg:
				aspd += 8
		artsdps = max(artsdmg * (1 - res/100), artsdmg * 0.05)
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.55 + 0.15 * self.mastery		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			
			avgphys = (sp_cost * hitdmg + skillhitdmg * min(2,self.targets)) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100)) + artsdps * min(2,self.targets)
		if self.skill == 2:
			atkbuff += 0.2 + self.mastery * 0.1
			if self.mastery == 0: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			targets = min(4, self.targets+1) if self.mastery > 0 else min(3, self.targets)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * targets + artsdps * min(3, self.targets)
			
		return dps
		
class Broca(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 42
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
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

			hitdmgarts = max(final_atk *atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) *min(3, self.targets)
		
		if self.skill == 2:
			self.atk_interval = 1.98
			atkbuff += 1.4 + 0.2 * self.mastery
			if self.mastery > 1: atkbuff -= 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * atk_scale *(1-res/100), final_atk* atk_scale * 0.05)
			
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(3,self.targets)
		return dps
	
class Cantabile(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 489  #######including trust
		maxatk = 590
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 100
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Cantabile Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Cantabile P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]

		
		if self.talent1: self.name += " melee"
		else: self.name += " ranged"
		

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.pot > 3: aspd += 5
		if self.talent1:
			atkbuff += 0.14 if self.pot > 4 else 0.12
		else:
			aspd += 14 if self.pot > 4 else 12
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.28 + 0.04 * self.mastery
			aspd += 34 + 4 * self.mastery
			if self.mastery > 1: aspd += 2
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Caper(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * cdmg* atk_scale - defense, final_atk * cdmg * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skillcritdmg = max(final_atk * cdmg* atk_scale *skill_scale - defense, final_atk* cdmg* atk_scale * skill_scale * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			skillhitdmg = skillcritdmg * crate + (1-crate) * skillhitdmg
			sp_cost = 3 if self.mastery == 3 else 4
			
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			
			interval = 20/13.6 if not self.trait else (self.atk_interval/(1+aspd/100))
			dps = avgphys/interval
		
		if self.skill == 2:
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			hitdmg = critdmg * crate + (1-crate) * hitdmg
			
			interval = 20/13.6 if not self.trait else (self.atk_interval/(1+aspd/100))
			dps = 2* hitdmg/interval
		return dps

class Carnelian(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 76
				else: self.base_atk += 66
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 95
				elif self.module_lvl == 2: self.base_atk += 85
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			self.atk_interval = 0.9 if self.mastery == 3 else 1.2
			if self.skilldmg: atkbuff += 0.2 if self.mastery > 1 else 0.15

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
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
				damage += max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05) * (1+ min(bonusscaling,i) * 0.2)
				
			dps = damage/totalduration * self.targets
		return dps

class Ceobe(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 643  #######including trust
		maxatk = 757
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ceobe Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ceobe P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 56
				elif self.module_lvl == 2: self.base_atk += 49
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.module_lvl > 1:
			if self.talent1: self.name += " maxTalent1"
			else: self.name += " minTalent1"
		
		if not self.talent2: self.name += " adjacentAlly"
		
		if self.module == 2 and self.skill == 1:
			if self.moduledmg: self.name += " vsElite"
		
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		newres= max(0, res-10) if self.module == 1 else res
		
		bonus_arts_scaling = 0.4
		if self.pot > 4: bonus_arts_scaling += 0.04
		if self.module == 1 and self.module_lvl > 1:
			bonus_arts_scaling += 0.05 * (self.module_lvl-1)
			if self.talent1:
				bonus_arts_scaling += 0.25
		
		if self.talent2:
			atkbuff += 0.08
			aspd += 8
			if self.module == 2:
				if self.module_lvl == 2:
					atkbuff += 0.04
					aspd += 4
				if self.module_lvl == 3:
					atkbuff += 0.07
					aspd += 7
		
		
			
		####the actual skills
		if self.skill == 1:
			sp_cost = 6 if self.mastery == 3 else 7
			skill_scale = 1.8 + 0.1 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			skilldmgarts = max(final_atk *atk_scale *skill_scale *(1-newres/100), final_atk * atk_scale * skill_scale * 0.05)
			defbonusdmg = max(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			
			atkcycle = self.atk_interval/(1+aspd/100)
			if self.module == 2 and self.moduledmg:
				sp_cost = sp_cost / (1+1/atkcycle) + 1.2 #bonus sp recovery vs elite mobs + sp lockout
			else:
				sp_cost = sp_cost + 1.2 #sp lockout
			
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmgarts
			if atks_per_skillactivation > 1:
				avghit = (skilldmgarts + (atks_per_skillactivation - 1) * hitdmgarts) / atks_per_skillactivation	
			dps = (avghit+defbonusdmg)/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			self.atk_interval = 0.576
			if self.mastery == 0: self.atk_interval = 0.64
			if self.mastery == 3: self.atk_interval = 0.528
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			defbonusdmg = max(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			
			dps = (hitdmgarts + defbonusdmg)/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 1.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			atk_scale *= 1.1
			aspd += 10
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			defbonusdmg = max(defense * bonus_arts_scaling *(1-newres/100), defense * bonus_arts_scaling * 0.05)
			
			dps = (hitdmg + defbonusdmg)/(self.atk_interval/(1+aspd/100))
		return dps
	
class Chen(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 52
				self.name += f"{self.module_lvl}"
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
			newdef = max(0, defense -70)
			if self.module_lvl == 2: atkbuff += 0.06
			if self.module_lvl == 3: atkbuff += 0.1
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4
			atk_scale = 1
			aspd += 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			skill_scale = 4.1 + 0.3 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * skill_scale -newdef, final_atk * skill_scale * 0.05) * dmg
			hitdmgarts = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05) * dmg
			dps = hitdmg + hitdmgarts
			
		if self.skill == 3:
			skill_scale = 2.6 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * skill_scale - newdef, final_atk *skill_scale * 0.05) * dmg
			dps = 10 * hitdmg
		return dps

class ChenAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 729  #######including trust
		maxatk = 853
		self.atk_interval = 2.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 33
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Chalter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Chalter P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2] + 8 #im not going to include the water buff for now
		atk_scale = 1.5 #from trait, may need rework after module release
			
		####the actual skills
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery 
			def_shred = 200 if self.mastery == 0 else 220
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			newdefense = max(0, defense- def_shred)
			hitdmg = max(final_atk * atk_scale - newdefense, final_atk* atk_scale * 0.05)
			
			dps = 2*hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps
			
class Chongyue(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
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
			normalhit = max(final_atk-defense, final_atk*0.05)
			normalcrit = normalhit * cdmg
			skillhit = max(final_atk*atk_scale-defense, final_atk*atk_scale*0.05)
			skillcrit = skillhit * cdmg
			avgnormal = normalcrit*normalcrate+normalhit*(1-normalcrate)
			avgskill = (skillcrit*skillcrate+skillhit*(1-skillcrate)) * self.targets
			avgdmg = (2 * avgnormal * normalhits + 2 * avgskill)/(normalhits +1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Click(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 18
				elif self.module_lvl == 2: self.base_atk += 15
				else: self.base_atk += 13
				self.name += f"{self.module_lvl}"
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
		
		hitdmgarts = max(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps

class Coldshot(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 53
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.trait:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))
			elif self.module == 1:
				hitdmg2 = max(final_atk * atk_scale2 - defense, final_atk * atk_scale2 * 0.05)
				dps = (hitdmg+hitdmg2)/(2*(self.atk_interval/(1+aspd/100))+1.6)
			else:
				dps = hitdmg/((self.atk_interval/(1+aspd/100))+1.6)
		
		if self.skill == 2:
			atkbuff += 1 + 0.15 * self.mastery
			if self.mastery > 1: atkbuff -= 0.05
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.trait:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))
			elif self.module == 1:
				hitdmg2 = max(final_atk * atk_scale2 - defense, final_atk * atk_scale2 * 0.05)
				dps = (hitdmg+hitdmg2)/(2*(self.atk_interval/(1+aspd/100))+1.6)
			else:
				dps = hitdmg/((self.atk_interval/(1+aspd/100))+2.4)
		return dps

class Conviction(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg1 = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skilldmg2 = max(final_atk * atk_scale * skill_scale2 - defense, final_atk* atk_scale * skill_scale2 * 0.05)
			
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * skill_scale * atk_scale * (1-res/100), final_atk * skill_scale * atk_scale * 0.05) * self.targets
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.skilldmg: 
				dps += skilldmg / sp_cost
			else:
				dps *= (sp_cost -5)/sp_cost
		return dps

	
class Dagda(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Degenbrecher(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 44
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
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
			
			hitdmg1 = max(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05) * dmg
			hitdmg2 = max(final_atk * atk_scale * last_scale - newdef, final_atk * atk_scale * last_scale * 0.05) * dmg
			
			dps = (10 * hitdmg1 + hitdmg2) * min(self.targets,6)
		return dps

class Dobermann(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 535  #######including trust
		maxatk = 632
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Dobermann Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Dobermann P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 53
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait: self.name += " blocking"   ##### keep the ones that apply
		if self.module == 2 and self.module_lvl > 1 and self.talent: self.name += " +3star"
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1.2 if self.trait else 1
		
		#talent/module buffs
		if self.module == 2:
			aspd +=5
			if self.talent and self.module_lvl > 1: aspd += 5 * self.module_lvl
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			sp_cost = 3 if self.mastery == 3 else 4
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Doc(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 551  ##including trust
		maxatk = 657 
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [1] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Doc Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Doc P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 35
				elif self.module_lvl == 2: self.base_atk += 30
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait: self.name += " blocking"   ##### keep the ones that apply
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		defignore = 140 if self.pot > 4 else 120
		if self.module == 2 and self.module_lvl > 1:
			defignore += 30 * (self.module_lvl -1)
		newdef = max(0, defense-defignore)
		if self.trait: atk_scale = 1.2
			
		####the actual skills
		if self.skill == 1:
			self.atk_interval = 0.35
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Dorothy(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 57
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 42
				self.name += f"{self.module_lvl}"
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
			hitdmgmine = max(final_atk * mine_scale - defense * defshred, final_atk * mine_scale * 0.05) * cdmg
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
			hitdmg = max(final_atk - defense * defshred, final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		
		
		if self.skill == 2:
			mine_scale = 3 if self.mastery == 3 else 2.6 + 0.1 * self.mastery
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgmine = max(final_atk * mine_scale - defense, final_atk * mine_scale * 0.05) * cdmg
			minedps = 0
			if self.trait: minedps = hitdmgmine/5 if self.talent1 else hitdmgmine/sp_cost
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		if self.skill == 3:
			mine_scale = 3.5 if self.mastery == 3 else 2.8 + 0.2 * self.mastery
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgmine = max(final_atk * mine_scale * (1-res/100), final_atk * mine_scale * 0.05) * cdmg
			minedps = 0
			if self.trait: minedps = hitdmgmine/5 if self.talent1 else hitdmgmine/sp_cost
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + minedps * self.targets
		return dps

class Durin(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=39
		lvl1atk = 268  #######including trust
		maxatk = 370
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.name = "Durin"
		self.buffs = buffs
	def skill_dps(self, defense, res):
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Dusk(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 82
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 51
				self.name += f"{self.module_lvl}"
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
			freehit = max(final_freeling - defense, final_freeling * 0.05)
			freedps = freehit/(freeling_interval/(1+aspd/100))
		
		if self.module == 2: aspd += 4 + self.module_lvl
		
		if self.talent1:
			atkbuff += 0.02 * self.stacks
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.1 if self.mastery == 0 else 2.05 + 0.15 * self.mastery
			sp_cost = 5 if self.mastery == 3 else 6
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			skilldmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			
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

			hitdmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			self.atk_interval = 2.9 * 1.4
			atkbuff += 1 if self.mastery == 0 else 1.05 + 0.05* self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		
		return dps+freedps

class Ebenholz(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 58
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 135
				elif self.module_lvl == 2: self.base_atk += 112
				else: self.base_atk += 88
				self.name += f"{self.module_lvl}"
			elif self.module == 3:
				self.name += " ModD"
				if self.module_lvl == 3: self.base_atk += 124
				elif self.module_lvl == 2: self.base_atk += 102
				else: self.base_atk += 76
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			bonusdmg = max(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
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
			
			hitdmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus_scale * (1-res/100), final_atk * bonus_scale * 0.05)
			
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 556  #######including trust
		maxatk = 668
		self.atk_interval = 0.85  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ela Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ela P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.talent2 = TrTaTaSkMo[2]
		
		self.module = module if module in [0,3] else 3 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 3:
				self.name += " ModZ"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 36
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		
		if self.talent2: self.name += " MineDebuff"
		else: self.name += " w/o mines"

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		
		#talent/module buffs
		crate = 0.3
		cdmg = 1.5
		if self.pot > 4: cdmg += 0.1
		if self.module == 3:
			crate += 0.1 * (self.module_lvl -1)
			cdmg += 0.1 * (self.module_lvl -1)
		if self.talent2:
			crate = 1.0
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			defshred = 500 + 100 * self.mastery
			newdef = max(0, defense - defshred)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - newdef, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - newdef, final_atk * cdmg * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
			
		if self.skill == 3:
			self.atk_interval = 0.5
			fragile = 0.25 + 0.05 * self.mastery
			if self.mastery > 2: fragile -= 0.05
			if not self.talent2: fragile = 0
			#if self.buffs[3] >= fragile: fragile = 0
			fragile = max(fragile, self.buffs[3])
			#print(self.buffs[3], fragile)
			atkbuff += 0.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05) * (1+fragile)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * (1+fragile)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) /(1+self.buffs[3])
			
		return dps
	
class Estelle(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 524  #######including trust
		maxatk = 690
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Estelle Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Estelle P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 52
				elif self.module_lvl == 2: self.base_atk += 43
				else: self.base_atk += 32
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
			
		####the actual skills
		if self.skill == 1: atkbuff += 0.5 + 0.1 * self.mastery
		else: atkbuff += 1.5 if self.mastery == 3 else 1.15 + 0.1 * self.mastery	

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
		hitdmg = max(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		return dps

class Eunectes(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 905  #######including trust
		maxatk = 1077
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Eunectes Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Eunectes P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 105
				elif self.module_lvl == 2: self.base_atk += 95
				else: self.base_atk += 80
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 80
				else: self.base_atk += 70
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if not self.talent1: self.name += " <50%hp"
		if self.moduledmg and self.module == 2: self.name += " WhileBlocking"

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atk_scale = 1.15
			if self.pot > 4 : atk_scale += 0.02
			if self.module == 2:
				if self.module_lvl == 2: atk_scale += 0.05
				if self.module_lvl == 3: atk_scale += 0.08
		
		if self.moduledmg and self.module == 2:
			atkbuff += 0.15
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.25 if self.mastery == 3 else 0.18 + 0.02 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			self.atk_interval = 2
			atkbuff += 1.8 if self.mastery == 3 else 1.3 + 0.15 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			atkbuff += 1.7 + 0.2 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class ExecutorAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
			newdef = max(0, defense - defignore)
			critdef = max(0, defense - defignore - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - newdef, final_atk * 0.05)
			critdmg =  max(final_atk - newdef, final_atk * 0.05) + max(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			atkbuff += 0.6 if self.mastery == 0 else 0.65 + 0.05 * self.mastery
			critdef = max(0, defense - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg =  max(final_atk - defense, final_atk * 0.05) + max(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 3:
			self.atk_interval = 1.8
			atkbuff += 1.5 + 0.1 * self.mastery
			scaling = 0.06 if self.mastery == 3 else 0.05
			atkbuff += self.ammo * scaling 
			
			critdef = max(0, defense - critdefignore)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg =  max(final_atk - defense, final_atk * 0.05) + max(final_atk - critdef, final_atk * 0.05)
			avgdmg = crate * critdmg + (1-crate) * hitdmg
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		return dps
	
class Exusiai(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 427  #######including trust
		maxatk = 630
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Exusiai Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Exusiai P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"


		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 41
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 27
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg and self.module == 1: self.name += " aerial target"
			
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0] + 0.06
		aspd = self.buffs[2] + 12
		atk_scale = 1
		
		if self.pot > 2:
			aspd += 3
		if self.pot == 6:
			atkbuff += 0.02
		
		#talent/module buffs

		if self.module == 1 and self.module_lvl == 3:
			atkbuff += 0.02
		
		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.21 + 0.08 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 4
			avgphys = (sp_cost * hitdmg + 3 * skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			
		elif self.skill == 2:
			skill_scale = 1.1 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale * skill_scale - defense, final_atk* atk_scale* skill_scale * 0.05)
			dps = 4*hitdmg/(self.atk_interval/(1+aspd/100))
			
		else:
			skill_scale = 1 + 0.03 * self.mastery
			if self.mastery > 1: skill_scale += 0.01
			self.atk_interval = 0.78 if self.mastery == 3 else 0.84
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale * skill_scale - defense, final_atk* atk_scale* skill_scale * 0.05)
			dps = 5*hitdmg/(self.atk_interval/(1+aspd/100))
		
		return dps
		
class Eyjafjalla(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 625  #######including trust
		maxatk = 735
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Eyjafjalla Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Eyjafjalla P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.skilldmg = TrTaTaSkMo[3]

		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.skilldmg:
			if self.skill == 1: self.name += " 2ndSkilluse"
			if self.skill == 2: self.name += " permaResshred"
		if not self.skilldmg and self.skill == 2: self.name += " minResshred"
		

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		self.atk_interval = 1.6
		atk_scale = 1
		atkbuff += 0.14
		resignore = 0
		if self.pot == 6: atkbuff += 0.02
		if self.module == 1: 
			atkbuff += 0.04 * (self.module_lvl - 1)
			resignore = 10
		newres = max(0, res - resignore)
		
		####the actual skills
		if self.skill == 1:
			aspd += 45 + 5 * self.mastery
			if self.skilldmg: atkbuff += 0.45 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atk_scale = 3.1 + 0.2 * self.mastery
			sp_cost = 5 if self.mastery == 3 else 6
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			resshred = 0.25 if self.mastery == 3 else 0.2
			newres2 = max(0, res*(1-resshred)-resignore)
			
			hitdmg = max(final_atk  * (1-newres2/100), final_atk * 0.05)
			if not self.skilldmg: hitdmg = max(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * (1-newres2/100), final_atk* atk_scale * 0.05)
			aoeskilldmg = max(0.5 * final_atk * atk_scale * (1-newres/100), 0.5 * final_atk* atk_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg + (self.targets - 1) * aoeskilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (self.targets - 1) * aoeskilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation						
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
			
		if self.skill == 3:
			self.atk_interval = 0.5
			atkbuff += 0.85 + 0.15 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			maxtargets = 6 if self.mastery == 3 else 5
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, maxtargets)
			 
		return dps

class FangAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			
			skillhit = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)

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
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class Fartooth(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1080  #######including trust
		maxatk = 1296
		self.atk_interval = 2.7   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 40
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Fartooth Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Fartooth P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 100
				elif self.module_lvl == 2: self.base_atk += 85
				else: self.base_atk += 70
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 120
				elif self.module_lvl == 2: self.base_atk += 100
				else: self.base_atk += 80
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		   ##### keep the ones that apply
		if not self.talent1: self.name += " w/o talent"
		if self.skilldmg and self.skill == 3: 
			self.name += " farAway"
			self.moduledmg = True
		if self.moduledmg and self.module == 1: self.name += " maxModuleBonus"

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.module == 1:
			aspd += 4 + self.module_lvl
			if self.moduledmg: atk_scale = 1.15	
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.15
			if self.pot > 4: atkbuff += 0.03
			if self.module == 1:
				if self.module_lvl == 2: atkbuff+= 0.05
				if self.module_lvl == 3: atkbuff+= 0.07
			if self.module == 2:
				if self.module_lvl == 2: aspd += 4
				if self.module_lvl == 3: aspd += 7

		if self.skill == 1:
			atkbuff += 0.34 + 0.03
			if self.mastery == 3: atkbuff += 0.02
			aspd += 45 if self.mastery == 3 else 35
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			aspd += 90 + 5 * self.mastery
			if self.mastery == 3: aspd += 5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 3:
			atkbuff += 1 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			dmgscale = 1
			if self.skilldmg:
				dmgscale = 1.4 if self.mastery == 3 else 1.3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)*dmgscale
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Fiammetta(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 771  #######including trust
		maxatk = 961
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Fiammetta Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Fiammetta P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 48
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.talent1: self.name += " w/o vigor"
		elif not self.talent2: self.name += " half vigor"
		if self.skilldmg and self.skill == 3: self.name += " central hit"
		elif self.skill == 3: self.name += " outer aoe"
		if self.moduledmg and self.module == 1: self.name += " blockedTarget"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg: atk_scale = 1.1
		def_shred = 100 if self.module == 2 else 0
		newdef = max(0, defense - def_shred)
		
		if self.module == 2:
			if self.module_lvl == 2: aspd += 5
			if self.module_lvl == 3: aspd += 10
		
		
		if self.talent1 and self.talent2:
			atkbuff += 0.5
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.03
				if self.module_lvl == 3: atkbuff += 0.1
		elif self.talent1:
			atkbuff += 0.25
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.03
				if self.module_lvl == 3: atkbuff += 0.05
				
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 3:
			skill_scale = 1.25 if self.mastery == 3 else 1.15
			if self.skilldmg:
				if self.mastery == 0: skill_scale = 1.85
				elif self.mastery == 1: skill_scale = 1.9
				elif self.mastery == 2: skill_scale = 2.0
				elif self.mastery == 3: skill_scale = 2.2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps
	
class Firewhistle(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 58
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 42
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " meelee"
		if self.moduledmg: self.name += " vsBlocked"
		
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
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgskill = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			hitdmgarts = max(final_atk * atk_scale * fire_scale * (1-res/100), final_atk * 0.05)
			avgdmg = 3/4 * self.targets * hitdmg + 1/4 * hitdmgskill * self.targets + hitdmgarts / 4
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			skill_scale = 0.65 if self.mastery == 0 else 0.7 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgarts
			dps = dps * self.targets
		return dps

class Flamebringer(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 806  #######including trust
		maxatk = 963
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Flamebringer Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Flamebringer P{self.pot} S{self.skill}"
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
				self.name += " ModY"
				self.name += f"{self.module_lvl}"
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
		if self.module == 2:
			aspd += 4
			if self.module_lvl > 1: aspd += 1
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.9 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 3 if self.mastery > 1 else 4
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.7 if self.mastery == 3 else 0.5 + 0.05 * self.mastery
			aspd += 30 + 5 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Flametail(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 58
				else: self.base_atk += 44
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " blocking"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		if self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		self.atk_interval = 0.35
		#talent/module buffs
		if self.moduledmg and self.module == 1: atkbuff += 0.08
		cdmg = 1
		if self.module == 1 and self.module_lvl > 1: cdmg = 1.2 if self.module_lvl == 3 else 1.15
		critrate = 0
		if self.buffs[4] > 0:
			dodgerate = 0.8 * self.buffs[4]
			atkrate = (self.atk_interval/(1+aspd/100))
			critrate = min(1, dodgerate*atkrate)
			
		####the actual skills
		if self.skill == 3:
			atkbuff += 0.6 + 0.1 * self.mastery
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05) * 2 * min(3, self.targets)
			avghit = critrate * critdmg + (1 - critrate) * hitdmg
			dps = avghit/(self.atk_interval/(1+aspd/100)) 
		return dps

class Flint(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 516  #######including trust
		maxatk = 620
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Flint Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Flint P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 1 and not self.talent: self.name += " blocking"
		if self.module == 1 and self.moduledmg: self.name += " >50%Hp"
		
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 1 and self.moduledmg: aspd += 10
		dmgscale = 1.45 if self.pot > 4 else 1.4
		if self.module == 1: dmgscale += 0.05 * (self.module_lvl -1)
		if self.skill == 1 and not self.talent: dmgscale = 1
		
		
		####the actual skills
		
		if self.skill == 1:
			skill_scale = 2.3 if self.mastery == 3 else 1.9 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 4
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.4 + 0.05 * self.mastery
			aspd += 40 + 5 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps*dmgscale

class Folinic(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 433  #######including trust
		maxatk = 529
		self.atk_interval = 2.85   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Folinic Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Folinic P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
		if self.module == 2:
			aspd += 3 + self.module_lvl
			
		####the actual skills
		if self.skill == 2:
			skill_scale = 2 if self.mastery == 3 else 1.6 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Franka(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 851  #######including trust
		maxatk = 1011
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Franka Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Franka P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"


		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 95
				elif self.module_lvl == 2: self.base_atk += 80
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
  ##### keep the ones that apply

		if self.moduledmg: self.name += " vsBlocked"

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.moduledmg and self.module == 1:
			atk_scale = 1.15
		
		crate = 0.2
		if self.module == 1:
			if self.module_lvl == 2: crate = 0.25
			if self.module_lvl == 3: crate = 0.28
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			aspd += 35
			if self.mastery == 3:
				aspd += 10
				atkbuff += 0.02
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk* atk_scale - defense, final_atk *atk_scale * 0.05)
			critdmg = final_atk *atk_scale
			avghit = crate * critdmg + (1-crate) * hitdmg	
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery
			crate *= 2.5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk* atk_scale - defense, final_atk *atk_scale * 0.05)
			critdmg = final_atk * atk_scale
			avghit = crate * critdmg + (1-crate) * hitdmg	
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
		return dps
	
class Fuze(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 644  #######including trust
		maxatk = 835
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Fuze Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Fuze P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		if self.buffs[0]>0: self.name += f" atk+{int(100*self.buffs[0])}%"
		if self.buffs[1]>0: self.name += f" atk+{self.buffs[1]}"
		if self.buffs[2]>0: self.name += f" aspd+{self.buffs[2]}"
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
			
		####the actual skills
		aspd += 75 + 5 * self.mastery
		atkbuff += 0.15 + 0.05 * self.mastery
		if self.mastery < 2: atkbuff += 0.02

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
		hitdmg = max(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		return dps

class GavialAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 73
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
		
		if self.skill == 2:
			atkbuff += 1.4 if self.mastery == 0 else 1.35 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
		if self.skill == 3:
			atkbuff += 1.4 if self.mastery == 3 else 1.0 + 0.1 * self.mastery
			aspd += 100 if self.mastery == 3 else 80
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, block)
			
		return dps

class Gladiia(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 59
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			
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
			
			hitdmg = max(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:

			skill_scale = 1 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale * skill_scale * (1-res/100), final_atk * atk_scale * skill_scale * 0.05)
			dps = hitdmg/1.5 * self.targets
		return dps

class Goldenglow(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 338  #######including trust
		maxatk = 391
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Goldenglow Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Goldenglow P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 38
				elif self.module_lvl == 2: self.base_atk += 32
				else: self.base_atk += 22
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if self.trait: self.name += " maxDroneDmg"
		else: self.name += " minDroneDmg"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		resshred = 18 if self.pot == 6 else 15
		newres = max(res-resshred,0)
		drone_dmg = 1.1
		drone_explosion = 3
		if self.pot > 2: drone_explosion += 0.15
		if self.module == 1: 
			if self.module_lvl == 3 : drone_explosion += 0.6
			if self.module_lvl == 2 : drone_explosion += 0.4
		
		drones = 2
		if not self.trait:
			drone_dmg = 0.35 if self.module == 1 else 0.2
		
		
		if self.skill == 1:
			atkbuff += 0.32 + 0.02 * self.mastery
			if self.mastery == 3: atkbuff += 0.02
			aspd += 38 + 4 * self.mastery
		elif self.skill == 2:
			atkbuff += 0.45 + 0.05 * self.mastery
		else:
			atkbuff += 0.5 + 0.1 * self.mastery
			if self.mastery == 0: atkbuff += 0.05
			drones = 3
		
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		drone_atk = drone_dmg * final_atk
		drone_explosion = final_atk * drone_explosion * self.targets
		
		dmgperinterval = final_atk*(3-drones) + drones * drone_atk * 0.9 + drones * drone_explosion * 0.1
		
		hitdmgarts = max(dmgperinterval *(1-newres/100), dmgperinterval * 0.05)
		dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps

class Grani(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		hitdmg = max(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps


class GreyThroat(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 33
				elif self.module_lvl == 2: self.base_atk += 29
				else: self.base_atk += 24
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * atk_scale * cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * 2
			skillcrit = max(final_atk * atk_scale * skill_scale * cdmg - defense, final_atk* atk_scale * skill_scale * cdmg * 0.05) * 2
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
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * atk_scale * cdmg - defense, final_atk * atk_scale * cdmg * 0.05)
			avgnorm = crate * critdmg + (1-crate) * hitdmg
			dps = 3 * avgnorm/(self.atk_interval/(1+aspd/100))
		return dps

class Haze(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 543  #######including trust
		maxatk = 643
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Haze Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Haze P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 30
				else: self.base_atk += 20
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		resshred = 0.23 if self.pot > 4 else 0.2
		resignore = 0
		if self.module == 1:
			resignore = 10
			if self.module_lvl == 2: resshred += 0.04
			if self.module_lvl == 3: resshred += 0.07
		newres = max(0, res-resignore) * (1-resshred)

		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
		if self.skill == 2:
			atkbuff += 0.45 + 0.05 * self.mastery
			aspd += 45 + 5 * self.mastery
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = max(final_atk * (1-newres/100), final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
	
class Hellagur(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * 2
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05) * 2
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
		return dps

class Hibiscus(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05) * dmg
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			scale = 1.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * scale * (1-res/100), final_atk * scale * 0.05) * dmg
			dps = hitdmg * min(self.targets,2 )
		return dps

class Highmore(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 606  #######including trust
		maxatk = 710
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Highmore Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Highmore P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent: self.name += " in IS3"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]		
		#talent/module buffs
		
		if self.module == 1:
			aspd += 3 + self.module_lvl
		if self.talent:
			aspd += 25
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.35 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		else:
			atkbuff += 0.6 if self.mastery == 3 else 0.5 + 0.03 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
			
		return dps

class Hoederer(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1403  #######including trust
		maxatk = 1656
		self.atk_interval = 2.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 45
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Hoederer Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Hoederer P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		
		if self.talent1 or (self.skilldmg and self.skill == 2): self.name += " vsStun/Bind"
		
		
		if self.skill == 2 and not self.skilldmg: " defaultState"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1.1
		if self.talent1 or (self.skilldmg and self.skill == 2): atk_scale = 1.4
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2 + 0.2 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 2:
			maxtargets = 3 if self.skilldmg else 2
			if self.skilldmg: self.atk_interval = 3 
			atkbuff += 0.28 + 0.04 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,maxtargets)
		if self.skill == 3:
			atkbuff += 0.9 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + 200
			dps = dps * min(2, self.targets)
		return dps
	
class Hoolheyak(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 45
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 32
				self.name += f"{self.module_lvl}"
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
		newres = max(res-10,0) if self.module == 1 else res
		dmg_scale = 1
		if self.module == 2 and self.talent2:
			dmg_scale += 0.1 * (self.module_lvl -1)
			
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.4 + 0.2 * self.mastery
			sp_cost = 8 if self.mastery == 0 else 7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05) * dmg_scale
			skilldmg = max(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale

			
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
			
			hitdmgarts = max(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = 9 * hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			self.atk_interval = 3
			skill_scale = 3.8 if self.mastery == 0 else 3.9 + 0.1 * self.mastery
			if not self.skilldmg: skill_scale *= 2/3	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * atk_scale * skill_scale * (1-newres/100), final_atk * atk_scale * skill_scale * 0.05) * dmg_scale
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
		return dps
	
class Horn(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 846  #######including trust
		maxatk = 1006
		self.atk_interval = 2.8 #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Horn Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Horn P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 100
				elif self.module_lvl == 2: self.base_atk += 85
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
		else: self.module = 0
		
		if self.talent2: self.name += " afterRevive"
		if self.skilldmg and not self.skill == 1: self.name += " overdrive"
		elif not self.skill == 1: self.name += " no overdrive"
		if self.moduledmg and self.module == 1: self.name += " blockedTarget"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		self.atk_interval = 2.8
		atk_scale = 1.1 if self.module == 1 and self.moduledmg else 1
		
		#talent/module buffs
		atkbuff += 0.2
		if self.pot > 2: atkbuff += 0.03
		if self.module == 1:
			if self.module_lvl == 2: atkbuff += 0.05
			if self.module_lvl == 3: atkbuff += 0.08
			
		if self.talent2:
			aspd += 18
			if self.pot >4: aspd += 3

			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.2 + 0.2 * self.mastery
			sp_cost = 6 if self.mastery == 0 else 5
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			
			sp_cost = sp_cost + 1.2 #sp lockout
			atkcycle = self.atk_interval/(1+aspd/100)
			atks_per_skillactivation = sp_cost / atkcycle
			avghit = skilldmg
			if atks_per_skillactivation > 1:
				avghit = (skilldmg + (atks_per_skillactivation - 1) * hitdmg) / atks_per_skillactivation	
				
			dps = avghit/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			skill_scale = 1.8 + 0.2 * self.mastery
			if self.mastery == 0: skill_scale += 0.1
			arts_scale = 0
			if self.skilldmg:
				if self.mastery == 0: arts_scale = 0.4
				elif self.mastery == 3: arts_scale = 0.6
				else: arts_scale = 0.5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			artsdmg = max(final_atk * atk_scale * arts_scale * (1-res/100), final_atk * atk_scale * arts_scale * 0.05)
			dps = (hitdmg+artsdmg)/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			self.atk_interval = 1.0
			atkbuff += 0.4 + 0.1 * self.mastery
			if self.skilldmg: atkbuff += 0.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) 			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
			
		return dps

class Hoshiguma(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		if self.skill == 2 and self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
				
		if self.skill == 2:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.buffs[4] > 0:
				skill_scale = 1 if self.mastery == 3 else 0.8 + 0.05 * self.mastery
				reflectdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
				dps += reflectdmg * self.buffs[4]	
		if self.skill == 3:
			atkbuff += 0.95 + 0.15 * self.mastery		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps


class Humus(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 541  #######including trust
		maxatk = 646
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 35

		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Humus Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Humus P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent = TrTaTaSkMo[1] and TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.base_atk += 5 + 5 * self.module_lvl
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skilldmg: self.name += " >80%Hp"
		else: self.name += " <50%Hp"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]		
		#talent/module buffs
		
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.2 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		else:
			if self.skilldmg: atkbuff += 0.72 + 0.06 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
			
		return dps

class Iana(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05) * (1+fragile)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) /(1+self.buffs[3])
		return dps

class Ifrit(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 72
				elif self.module_lvl == 2: self.base_atk += 64
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg and self.module == 1: self.name += " maxRange"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
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
			hitdmgarts = max(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 2:
			sp_cost = 8 if self.mastery == 0 else 7
			skill_scale = 1.9 + 0.25 * self.mastery
			if self.mastery > 1: skill_scale -= 0.15
			burn_scale = 0.99
			newres = res * (1-resshred)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			skilldmgarts = max(final_atk *atk_scale *skill_scale *(1-newres/100), final_atk * atk_scale * skill_scale * 0.05)
			burndmg = max(final_atk *burn_scale *(1-newres/100), final_atk * burn_scale * 0.05)
			
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
			newres = max(0, res-flatshred)
			newres = newres * (1-resshred)
			hitdmgarts = max(final_atk *atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
		return dps

class Indra(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 504  #######including trust
		maxatk = 605
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Indra Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Indra P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " >50% HP"
		

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.moduledmg and self.module == 1:
			aspd += 10
			
		####the actual skills
		if self.skill == 1:
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			atkbuff += 1.1 + 0.1 * self.mastery
			newdef = defense * (1 - (0.45 + 0.05 * self.mastery)) 
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			skilldmg = max(final_atk - newdef, final_atk * 0.05)

			dps = 0.2*(4*hitdmg + skilldmg)/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.75 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		return dps

class Ines(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 532  #######including trust
		maxatk = 639
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ines Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ines P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		
		if self.skill == 2:
			if self.skilldmg: self.name += " maxSteal"
			else: self.name += " noSteal"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		if self.pot > 3: aspd += 8
		atk_scale = 1
		
		stolenatk = 90 if self.pot < 5 else 100
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 0.5 + 0.1 * self.mastery 
			if self.mastery < 3: skill_scale += 0.5
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1] + stolenatk
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 3
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + skillhitdmg * min(1, (1+aspd/100)*3/4)
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			aspdsteal = 7 if self.mastery == 3 else 6
			aspd += aspdsteal * 10 if self.skilldmg else aspdsteal
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1] + stolenatk	
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 1.2 if self.mastery == 0 else 1.3 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1] + stolenatk
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))	
		return dps

class Irene(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 564  #######including trust
		maxatk = 701
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Irene Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Irene P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 59
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
	
		if not self.talent1: self.name += " vsLevitateImmune"
		if self.module == 2 and self.module_lvl > 1 and self.talent2: self.name += " vsSeaborn"
		
		if self.skill == 3 and not self.skilldmg and self.talent1: self.name += " vsHeavy"
		if self.skill == 3: self.name += " totalDMG"
		
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		newdef = defense
		if self.module == 2:
			newdef = max(0, defense -70)
			if self.module_lvl == 2:
				atkbuff += 0.06 if self.talent2 else 0.03
			if self.module_lvl == 3:
				atkbuff += 0.1 if self.talent2 else 0.05
		newdef2 = newdef * 0.5
		
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4
			atk_scale = 1
			aspd += 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 3:
			skill_scale1 = 2.5 if self.mastery == 0 else 3
			hits = 10 if self.mastery == 0 else 12
			skill_scale = 2.3 if self.mastery == 0 else 2.2 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			initialhit1 = max(final_atk * skill_scale1 - newdef, final_atk *skill_scale1 * 0.05)
			initialhit2 = max(final_atk * skill_scale1 - newdef2, final_atk * skill_scale1 * 0.05)
			hitdmg1 = max(final_atk * skill_scale - newdef, final_atk *skill_scale * 0.05)
			hitdmg2 = max(final_atk * skill_scale - newdef2, final_atk *skill_scale * 0.05)
			dps = 0.5*initialhit1 + 0.5* initialhit2
			levduration = 4 if self.mastery == 3 else 3
			if not self.talent1: return (dps + hits * (0.5*hitdmg1+0.5*hitdmg2))
			else:
				if not self.skilldmg:
					levduration = levduration /2
			flyinghits = min(hits, int(levduration / 0.3))
			dps += flyinghits * hitdmg2 + (hits-flyinghits) * (0.5*hitdmg1+0.5*hitdmg2)
			dps *= self.targets
		return dps

class JessicaAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 493  #######including trust
		maxatk = 582
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Jessicat Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Jessicat P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 57
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
		else: self.module = 0

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1

		if self.skill == 1:
			atkbuff += 0.55 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.6 + 0.05 * self.mastery
			self.atk_interval = 0.3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 2.7 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			self.atk_interval = 1.8
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Kafka(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 54
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Kazemaru(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 647  #######including trust
		maxatk = 772
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		lvl1atk2 = 633
		maxatk2 = 772
		self.clone_atk = lvl1atk2 + (maxatk2-lvl1atk2) * (level-1) / (maxlvl-1)
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Kazemaru Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Kazemaru P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.skilldmg = TrTaTaSkMo[3]

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.skilldmg: self.name += " w/o doll"

		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		

		if self.module == 1:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.02
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.75
			if self.mastery == 1: skill_scale = 3
			if self.mastery == 2: skill_scale = 3.3
			if self.mastery == 3: skill_scale = 3.5	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + 2* skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.9 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_atk2 = self.clone_atk * (1.9 + 0.1 * self.mastery)
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg2 = max(final_atk2 - defense, final_atk * 0.05)

			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.skilldmg: dps += hitdmg2/(self.atk_interval/(1+aspd/100))
		return dps
	
class Kjera(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 28
				elif self.module_lvl == 2: self.base_atk += 23
				else: self.base_atk += 18
				self.name += f"{self.module_lvl}"
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
			hitdmgarts = max(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.4 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			drone_atk = drone_dmg * final_atk
			dmgperinterval = final_atk + 2 * drone_atk
			res2 = max(0,res-15)
			hitdmgarts = max(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
			hitdmgfreeze = max(dmgperinterval *(1-res2/100), dmgperinterval * 0.05)
			damage = hitdmgfreeze * self.freezeRate + hitdmgarts * (1 - self.freezeRate)
			dps = damage/(self.atk_interval/(1+aspd/100))
			
		return dps
	
class Kroos(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=55
		lvl1atk = 308  #######including trust
		maxatk = 425
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 21
		
		if level != maxlvl: self.name = f"Kroos Lv{level} P{self.pot} S1Lv7" #####set op name
		else: self.name = f"Kroos P{self.pot} S1Lv7"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		crate = 0.2
		cdmg = 1.6 if self.pot > 4 else 1.5

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
		hitdmg = max(final_atk - defense, final_atk * 0.05)
		hitcrit = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
		skilldmg = max(final_atk * 1.4 - defense, final_atk * 1.4 * 0.05) * 2
		skillcrit =  max(final_atk * 1.4 * cdmg - defense, final_atk * 1.4 * cdmg * 0.05) * 2
		avghit = crate * hitcrit + (1-crate) * hitdmg
		avgskill = crate * skillcrit + (1-crate) * skilldmg

		dps = 0.2 * (4* avghit + avgskill)/(self.atk_interval/(1+aspd/100))
		return dps

class KroosAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 486  #######including trust
		maxatk = 577
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"KroosAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"KroosAlt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 31
				elif self.module_lvl == 2: self.base_atk += 27
				else: self.base_atk += 22
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if self.skill == 2:
			if self.skilldmg: self.name += " 4hits"
			else: self.name += " 2hits"
		if self.moduledmg and self.module == 1: self.name += " aerial target"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		self.atk_interval = 1.0
		atk_scale = 1
		crit_scale = 1.5
		if self.pot > 4: crit_scale += 0.1
		if self.moduledmg and self.module == 1:
			atk_scale = 1.1
		if self.module == 1:
			if self.module_lvl == 2: crit_scale += 0.1
			if self.module_lvl == 3: crit_scale += 0.15
		
		hits = 2
		if self.skill == 2:
			self.atk_interval = 0.625 if self.mastery == 3 else 0.7
			if self.skilldmg: hits = 4
		if self.skill == 1:
			atkbuff += 0.3 + 0.03 * self.mastery
			if self.mastery == 3: atkbuff+= 0.01

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		
		normalhit = max(final_atk * atk_scale -defense, final_atk * atk_scale * 0.05)
		crithit = max(final_atk * atk_scale * crit_scale -defense, final_atk * atk_scale * crit_scale * 0.05)

		dps = hits*(0.2*crithit+0.8*normalhit)/(self.atk_interval/(1+aspd/100))
		return dps

class LaPluma(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 627  #######including trust
		maxatk = 725
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1

		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"La Pluma Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"La Pluma P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 24
				else: self.base_atk += 18
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " maxStacks"
		else: self.name += " noStacks"
		if self.skilldmg and self.skill == 2: self.name += " lowHpTarget"

		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]		
		#talent/module buffs
		if self.talent1:
			aspd += 36
			if self.module == 1:
				atkbuff += 0.05
				if self.module_lvl == 3: atkbuff += 0.03
				
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.35 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + 2 * skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		else:
			self.atk_interval = 1.3
			if self.mastery == 0: self.atk_interval *= 0.65
			elif self.mastery == 3: self.atk_interval *= 0.5
			else: self.atk_interval *= 0.5
			atkbuff += 0.55 + 0.05 * self.mastery
			if self.skilldmg:
				atkbuff += 0.5 if self.mastery == 3 else 0.4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
			
		return dps
	
class Lappland(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 629  #######including trust
		maxatk = 760
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lappland Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lappland P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 32
				else: self.base_atk += 22
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait and self.skill == 1: self.name += " rangedAtk"   ##### keep the ones that apply
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if not self.trait and self.skill == 1:
			atk_scale = 0.8
		bonus = 0.1 if self.module == 1 else 0
		if self.module == 1:
			aspd += 3 + self.module_lvl
		
		fragile = 0
		if self.module == 1:
			fragile = 0.04 * (self.module_lvl -1)
		fragile = max(fragile, self.buffs[3])
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.55 + 0.05* self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + bonusdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.9 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(2,self.targets) + bonusdmg/(self.atk_interval/(1+aspd/100)) * min(2,self.targets)
		return dps*(1+fragile)/(1+self.buffs[3])
	
class Lavaalt(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 760  #######including trust
		maxatk = 888
		self.atk_interval = 2.9   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"LavaAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"LavaAlt P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 62
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 43
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skilldmg and self.skill==2: self.name += " overlap"
		if self.skilldmg and self.skill==1 and self.targets > 1: self.name += " overlap"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs

			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.14 + 0.02 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
			if self.skilldmg and self.targets > 1:
				dps *= 2
				
		if self.skill == 2:
			atk_scale = 0.5 if self.mastery == 3 else 0.4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmgarts = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
			if self.skilldmg:
				dps *= 2	
		return dps
	
class Lessing(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 951  #######including trust
		maxatk = 1129
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lessing Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lessing P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 24
				else: self.base_atk += 17
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		
		if self.skill == 3 and self.module == 1:
			self.skilldmg = self.skilldmg and self.moduledmg
			self.moduledmg = self.skilldmg
		
		if not self.talent2: self.name += " w/o talent2"
		
		if self.moduledmg and self.module == 1 and not self.skill == 3: self.name += " vsBlocked"
		elif self.skill == 3 and self.skilldmg: self.name += " vsBlocked"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.module == 1 and self.moduledmg:
			atk_scale = 1.15
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 0.12
			if self.pot > 4: atkbuff += 0.04
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.05
				if self.module_lvl == 3: atkbuff += 0.08


			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.25 + 0.2 * self.mastery
			if self.mastery == 3: skill_scale += 0.05
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1) * min(self.targets, 3)
			
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.35 if self.mastery == 0 else 0.3 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = 2 * hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			if self.skilldmg: atk_scale *= 2.2 if self.mastery == 3 else 1.8 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps =  hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
	
class Leto(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 59
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(2, self.targets)
		
		return dps

class Lin(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 800  #######including trust
		maxatk = 919
		self.atk_interval = 2.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lin Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lin P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 77
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 62
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		if self.skill == 1:
			self.atk_interval = 3
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 2:
			aspd += 130 if self.mastery == 3 else 90 + 10 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			atkbuff += 1.6 + 0.15 * self.mastery
			if self.mastery > 1: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps

class Ling(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 441  #######including trust
		maxatk = 508
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ling Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ling P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		#Dragonstats:
		dragonlvl1 = 1318
		dragonlvl90 = 1481
		self.dragoninterval = 2.3
		if self.skill == 3 and not self.skilldmg:
			dragonlvl1 = 732
			dragonlvl90 = 823
			self.dragoninterval = 1.5
		elif self.skill == 2:
			dragonlvl1 = 361
			dragonlvl90 = 406
			self.dragoninterval = 1.6
		elif self.skill == 1:
			dragonlvl1 = 489
			dragonlvl90 = 549
			self.dragoninterval = 1.25	 
		self.dragon_atk = dragonlvl1 + (dragonlvl90-dragonlvl1) * (level-1) / (maxlvl-1)
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		if self.module == 2 and self.module_lvl ==3:
			if self.skill == 3: self.dragon_atk += 60
			if self.skill == 2: self.dragon_atk += 35
			if self.skill == 1: self.dragon_atk += 45
		
		if not self.trait: self.name += " noDragons"   ##### keep the ones that apply
		elif not self.talent1: self.name += " 1Dragon"
		else: self.name += " 2Dragons"
		if self.skill == 3 and self.trait:
			if self.skilldmg: self.name += "(Chonker)"
			else: self.name += "(small)"			
		if not self.talent2: self.name += " noTalent2Stacks"
		
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 0.15
		
		dragons = 2 if self.talent1 else 1
		if not self.trait: dragons = 0

		####the actual skills
		if self.skill == 1:
			atkbuff += 0.38 + 0.04 * self.mastery
			aspd += 38 + 4 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_dragon = self.dragon_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrag = max(final_dragon * (1-res/100), final_dragon * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrag/(self.dragoninterval/(1+aspd/100)) * dragons
		if self.skill == 2:
			skill_scale = 3.7 if self.mastery == 0 else 3.6 + 0.3 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_dragon = self.dragon_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrag = max(final_dragon * (1-res/100), final_dragon * 0.05)
			skilldmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			skilldmgdrag = max(final_dragon * skill_scale * (1-res/100), final_dragon * skill_scale * 0.05)
			sp_cost = 16 - self.mastery + 1.2 #sp lockout
			dpsskill = (skilldmg + dragons * skilldmgdrag) * min(self.targets,2) / sp_cost			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrag/(self.dragoninterval/(1+aspd/100)) * dragons + dpsskill
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_dragon = self.dragon_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			block = 4 if self.skilldmg else 2
			hitdmgdrag = max(final_dragon - defense, final_dragon * 0.05) * min(self.targets, block)
			skilldmg = hitdmg * 0.2
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrag/(self.dragoninterval/(1+aspd/100)) * dragons + skilldmg * 2 * dragons * self.targets
		return dps

class Logos(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModD"
				if self.module_lvl == 3: self.base_atk += 67
				elif self.module_lvl == 2: self.base_atk += 54
				else: self.base_atk += 36
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 1:
			final_atk = self.base_atk * (1+buffs[0] + 0.7 + 0.1 * self.mastery) + buffs[1]
			limit = final_atk * (1.2 + 0.1 * self.mastery)
			self.name += f" Death@{int(limit)}HP"
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
		newres = max(0,res-10)
		shreddmg = 165 if self.pot > 2 else 150	
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-newres/100), final_atk * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (max(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
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
			hitdmg = max(final_atk * scaling * (1-newres/100), final_atk * scaling * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (max(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
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
			hitdmg = max(final_atk * (1-newres/100), final_atk * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)
			bonusdmg = (max(final_atk * bonusdmg * (1-newres/100), final_atk * bonusdmg * 0.05) + max(shreddmg * (1-newres/100), shreddmg * 0.05)) * bonuschance
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

class Lunacub(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 887  #######including trust
		maxatk = 1074
		self.atk_interval = 2.7   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lunacub Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lunacub P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,2] else 2 #### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 68
				elif self.module_lvl == 2: self.base_atk += 63
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atk_shorter = 0.15
		if self.module == 2:
			atk_shorter += 0.05 * (self.module_lvl - 1)
		self.atk_interval = 2.7 * (1-atk_shorter)
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 1 if self.mastery == 3 else 0.6 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			aspd += 110 + 10 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Lutonada(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 616  #######including trust
		maxatk = 790
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Lutonada Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Lutonada P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		####the actual skills
		if self.skill == 1:
			skill_scale = 2 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skillhitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			sp_cost = 3 if self.mastery == 3 else 4
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			skill_scale = 0.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			dps = hitdmg / 2 * self.targets
		return dps
	
class Magallan(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 34
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = max(final_drone * (1-res/100), final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+(aspd+bonusaspd)/100)) * drones * self.targets
		if self.skill == 3:
			atkbuff += 1.5 if self.mastery == 3 else 1 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_drone = self.drone_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = max(final_drone - defense, final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+(aspd+bonusaspd)/100)) * drones * self.targets
		return dps

class Manticore(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 716  #######including trust
		maxatk = 871
		self.atk_interval = 3.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Manticore Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Manticore P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 72
				else: self.base_atk += 58
				self.name += f"{self.module_lvl}"
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
		atkbuff += 0.5
		if self.pot > 4: atkbuff += 0.04
		
		if self.module == 1:
			atkbuff += 0.05 * (self.module_lvl -1)
		
		if aspd > 3: atkbuff = self.buffs[0]
			
		####the actual skills
		if self.skill == 2:
			self.atk_interval = 5.2
			atkbuff += 0.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps

class Matoimaru(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 45
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps


class Melantha(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=55
		lvl1atk = 648 #######including trust
		maxatk = 803
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 25

		if level != maxlvl: self.name = f"Melantha Lv{level} P{self.pot} S1Lv7" #####set op name
		else: self.name = f"Melantha P{self.pot} S1Lv7"
		
		self.buffs = buffs
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]	
		atkbuff += 0.58
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = max(final_atk - defense, final_atk * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Meteor(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 446  #######including trust
		maxatk = 530
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Meteor Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Meteor P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 27
				else: self.base_atk += 22
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1: self.talent1 = self.talent1 and self.moduledmg
		if self.talent1: self.name += " vsAerial"

		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		talentscale = 1
		if self.talent1:
			talentscale = 1.4 if self.pot > 4 else 1.35

		if self.module == 1:
			if self.talent1: 
				atk_scale = 1.1
				if self.module_lvl == 3: talentscale += 0.15
				elif self.module_lvl == 2: talentscale += 0.05
			
			
		####the actual skills
		if self.skill == 1:
			sp_cost = 4 
			skill_scale = 1.5 + 0.1 * self.mastery
			defshred = 0.35 if self.mastery == 3 else 0.3 + 0.01 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale * talentscale - defense * (1-defshred), final_atk * atk_scale * talentscale * 0.05)
			skilldmg = max(final_atk * atk_scale * talentscale * skill_scale - defense * (1-defshred), final_atk * atk_scale * talentscale * skill_scale * 0.05)
			avgdmg = (sp_cost * hitdmg + skilldmg) / (sp_cost + 1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		
		return dps

class Meteorite(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 37
				self.name += f"{self.module_lvl}"
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
			newdef = max(0, defense - 100)
			crate += 0.1 * (self.module_lvl - 1)

		skill_scale = 1.7 + 0.15 * self.mastery
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
		hitdmg = max(final_atk - newdef, final_atk * 0.05)
		hitcrit = max(final_atk * cdmg - newdef, final_atk * cdmg * 0.05)
		skillhitdmg = max(final_atk * skill_scale - newdef, final_atk * skill_scale * 0.05)
		skillcritdmg = max(final_atk * cdmg *skill_scale - newdef, final_atk * cdmg * skill_scale * 0.05)
		sp_cost = 3 if self.mastery == 3 else 4
		avghit = crate * hitcrit + (1-crate) * hitdmg
		avgskill = crate * skillcritdmg + (1-crate) * skillhitdmg
		avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1) * self.targets	
		dps = avgphys/(self.atk_interval/(1+aspd/100))
		return dps

class Mizuki(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitbonus = max(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			skillbonus = max(final_atk * bonusdmg * skill_scale * (1-res/100), final_atk * bonusdmg * skill_scale * 0.05)
			
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
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgarts = max(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets + hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, bonustargets)
		
		if self.skill == 3:
			atkbuff += 1.05 + 0.15 * self.mastery
			bonustargets += 2
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgarts = max(final_atk * bonusdmg * (1-res/100), final_atk * bonusdmg * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets + hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets, bonustargets)
		
		return dps

class Mlynar(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 331  #######including trust
		maxatk = 385
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mlynar Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Mlynar P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		
		if not self.trait: self.name += " -10stacks"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		self.buffs = buffs
		if self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"
		
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		final_atk = 0
		atk_scale = 1.1 
		if self.pot > 2: atk_scale += 0.03
		if self.talent1: atk_scale += 0.05
		
		stacks = 40
		if not self.trait: stacks -= 10
		
		atkbuff += stacks * 0.05
		
		if self.skill == 1:
			atk_scale *= 1.7 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			finaldmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = finaldmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			self.atk_interval = 1.5
			atk_scale *= 1.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			finaldmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = 2 * finaldmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 3:
			atkbuff += stacks * 0.05
			atk_scale *= 1.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			truedmg = final_atk * 0.12 if self.mastery == 3 else final_atk * 0.11
			finaldmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = (finaldmg + truedmg)/(self.atk_interval/(1+aspd/100))
			dps = dps * min(self.targets, 5)
		if self.buffs[4] > 0:
			truescaling = 0.15 if self.pot < 5 else 0.18
			dps += final_atk * truescaling * self.buffs[4]
		
		return dps

class Mon3tr(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1149  #######including trust
		maxatk = 1402
		self.atk_interval = 2.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)

		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mon3tr Lv{level} S{self.skill}" #####set op name
		else: self.name = f"Mon3tr S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		if not self.talent2 and self.module == 2 and self.module_lvl > 1: self.name += " NotInKalRange"
		if self.skill == 3:
			skillduration = 20
			if self.mastery == 2: skillduration = 19
			if self.mastery < 2: skillduration = 18
			self.name += f" TrueDmg with decay over {skillduration}s"

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		if self.module == 2 and self.talent2:
			if self.module_lvl == 2: aspd += 12
			if self.module_lvl == 3: aspd += 20
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			if self.mastery == 2: atkbuff += 0.05
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))*min(self.targets,3)
		
		if self.skill == 3:
			atkbuff += (1.9 + 0.2 * self.mastery) * (1 - res/120)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			dps = final_atk/(self.atk_interval/(1+aspd/100))
		return dps

class Morgan(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 826  #######including trust
		maxatk = 980
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Morgan Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Morgan P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 82
				elif self.module_lvl == 2: self.base_atk += 74
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " lowHp"
		else: self.name += " fullHp"
		if self.moduledmg and self.module == 1: self.name += " vsBlocked"
		
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.52 if self.pot > 4 else 0.5
			if self.module == 1:
				if self.module_lvl == 3: atkbuff += 0.08
				elif self.module_lvl == 2: atkbuff += 0.05

		if self.module == 1 and self.moduledmg:
			atk_scale = 1.15
			
		####the actual skills
		skill_scale = 1.6 + 0.1 * self.mastery
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		hitdmg = max(skill_scale * final_atk * atk_scale - defense, skill_scale * final_atk * atk_scale * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))

		return dps

class Mountain(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 520  #######including trust
		maxatk = 632
		self.atk_interval = 0.78   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mountain Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Mountain P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1:
			if self.moduledmg: self.name += " >50% hp"				
			else: self.name += " <50% hp"
		
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		crate = 0.2
		cdmg = 1.6
		if self.module == 1:
			if self.module_lvl == 2: 
				crate += 0.03
				cmg += 0.05
			if self.module_lvl == 3: 
				crate += 0.05
				cdmg += 0.1
			if self.moduledmg:
				aspd += 10
		if self.pot > 4: cdmg += 0.1
		
		
		####the actual skills
		if self.skill == 1:

			atk_scale = 2 + 0.1 * self.mastery
			hits = 3 if self.mastery == 3 else 4

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			normalhitdmg = max(final_atk-defense, final_atk*0.05)
			crithitdmg = max(final_atk*cdmg-defense, final_atk*cdmg*0.05)
			avghit = crate * crithitdmg + (1-crate) * normalhitdmg
			
			normalskilldmg = max(final_atk * atk_scale -defense, final_atk*0.05)
			critskilldmg = max(final_atk * atk_scale * cdmg - defense, final_atk * cdmg * atk_scale * 0.05)
			avgskill = crate * critskilldmg + (1-crate) * normalskilldmg
			avgskill = avgskill * min(self.targets,2)
			
			avgdmg = (hits * avghit + avgskill) / (hits + 1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			normalhitdmg = max(final_atk - defense, final_atk * 0.05)
			crithitdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avgdmg = normalhitdmg * (1-crate) + crithitdmg * crate
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets , 2)
		if self.skill == 3:
			self.atk_interval = 0.78 * 1.7
			atkbuff += 0.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			normalhitdmg = max(final_atk-defense, final_atk*0.05)
			crithitdmg = max(final_atk*cdmg-defense, final_atk*cdmg*0.05)
			crate = 0.55 + 0.05 * self.mastery
			if self.mastery == 3: crate += 0.05
			avgdmg = normalhitdmg * (1-crate) + crithitdmg * crate
			dps = 2 * avgdmg/(self.atk_interval/(1+aspd/100))

		return dps

class Mousse(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 550  #######including trust
		maxatk = 679
		self.atk_interval = 1.25   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Mousse Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Mousse P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		#talent/module buffs
		crate = 0.23 if self.pot > 4 else 0.2
			
		####the actual skills
		if self.skill == 1:
			sp_cost = 4 if self.mastery == 3 else 5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			
			atkbuff += 0.6 + 0.05 * self.mastery
			final_atk2 = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg2 = max(final_atk2 * (1-res/100), final_atk2 * 0.05)
			
			avgdmg = (hitdmg * sp_cost + hitdmg2) / (sp_cost + 1)
			
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * (1+crate)
		
		if self.skill == 2:
			atkbuff += 0.45 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * (1+crate)
		return dps
			
class Mudrock(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 80
				elif self.module_lvl == 2: self.base_atk += 70
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.buffs = buffs
		if self.skill == 2 and self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.skill == 2:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)	
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
			if self.buffs[4] > 0:
				atk_scale = 2.1 + 0.2 * self.mastery
				skilldmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)	
				spcost = 5 if self.mastery == 0 else 4
				skillcycle = spcost / self.buffs[4] + 1.2
				dps += skilldmg / skillcycle * self.targets
				
		
		if self.skill == 3:
			self.atk_interval = 0.7*1.6
			atkbuff += 1 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			hitdmg = max(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		return dps
	
class Muelsyse(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 25
				elif self.module_lvl == 2: self.base_atk += 20
				else: self.base_atk += 15
				self.name += f"{self.module_lvl}"
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
		hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		
		main = 1 if self.talent1 else 0
		final_summonatk = summonatk * (1+atkbuff) + self.buffs[1]
		if not self.ranged and self.talent2: final_summonatk += 250
		summondamage = max(final_summonatk * (1-res/100), final_summonatk * 0.05) if self.arts else max(final_summonatk - defense, final_summonatk * 0.05)
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Dorothy(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Dorothy)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuEbenholz(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Ebenholz(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Ebenholz)" + self.name[8:]
		self.ranged = True
		self.arts = True
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuCeobe(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Ceobe(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Ceobe)" + self.name[8:]
		self.ranged = True
		self.arts = True
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)
		
class MumuMudrock(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Mudrock(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Mudrock)" + self.name[8:]
		self.ranged = False
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuRosa(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Rosa(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Rosa)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuSkadi(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Skadi(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Skadi)" + self.name[8:]
		self.ranged = False
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class MumuSchwarz(Muelsyse):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		super().__init__(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		operator = Schwarz(lvl,pot,skill,mastery,module,module_lvl,targets,TrTaTaSkMo,buffs)
		self.name = "Muelsyse(Schwarz)" + self.name[8:]
		self.ranged = True
		self.arts = False
		self.summon_interval = operator.atk_interval
		self.summon_atk = operator.base_atk
		S123 = skill if skill in [1,2,3] else 3
		self.name += name_addition(S123,self.ranged,TrTaTaSkMo)

class NearlAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 968  #######including trust
		maxatk = 1149
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"NTRKnight Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"NTRKnight P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 105
				elif self.module_lvl == 2: self.base_atk += 95
				else: self.base_atk += 70
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 79
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg: 
			if self.module == 1: self.name += " blockedTarget"
			if self.module == 2: self.name += " afterRevive"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		def_shred = 0.2
		if self.pot > 4: def_shred += 0.03
		if self.module == 1:
			if self.module_lvl == 2: def_shred += 0.05
			elif self.module_lvl == 3: def_shred += 0.08
		
		if self.moduledmg:
			if self.module == 1: atk_scale = 1.15
			if self.module == 2: aspd += 30
			
		if self.skill == 1:
			atkbuff += 0.55 + 0.05 * self.mastery
			aspd += 38 + 4 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - (defense * (1-def_shred)), final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 1.2
			if self.mastery == 1: atkbuff += 0.1
			elif self.mastery == 2: atkbuff += 0.25
			elif self.mastery == 3: atkbuff += 0.4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - (defense * (1-def_shred)), final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			atkbuff += 1
			if self.mastery == 1: atkbuff += 0.1
			elif self.mastery == 2: atkbuff += 0.25
			elif self.mastery == 3: atkbuff += 0.4
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - (defense * (1-def_shred)), final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))  
			
		return dps

class Nian(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1 and self.module_lvl > 1 and self.moduledmg: self.name += " 3shieldsBroken"
		
		self.buffs = buffs
		if self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"
			
	
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
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atk_scale = 0.7 if self.mastery == 0 else 0.6 + 0.1 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps += hitdmg * self.buffs[4]
		
		if self.skill == 3:
			atkbuff += 1.2 if self.mastery == 3 else 0.8 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps


class Odda(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			splashhitdmg = max(0.5 * final_atk * atk_scale - defense, 0.5 * final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			splashskillhitdmg = max(0.5 * final_atk * atk_scale * skill_scale - defense, 0.5 * final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			avgsplash = (sp_cost * splashhitdmg + splashskillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps += avgsplash/(self.atk_interval/(1+aspd/100)) * (self.targets - 1)
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery	
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
	
class Pallas(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 627  #######including trust
		maxatk = 737
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 25
		
		self.skill = skill if skill in [1,2,3] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Pallas Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Pallas P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(3,max(1,targets))
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 83
				elif self.module_lvl == 2: self.base_atk += 73
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"

		else: self.module = 0
		
		if not self.trait: self.name += " w/o trait"   ##### keep the ones that apply
		if not self.talent1: self.name += " w/o vigor"

		
		if self.skill == 3 and self.skilldmg: self.name += " selfbuffS3"
		
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.25
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.02
				if self.module_lvl == 3: atkbuff += 0.05
		
		if self.module == 2: aspd += 2 + self.module_lvl
		
		if self.trait: 
			atk_scale = 1.3 if self.module == 1 else 1.2
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.45 + 0.1 * self.mastery			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + 2* skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))	
		
		if self.skill == 3:
			atkbuff += 0.7 + 0.1 * self.mastery
			if self.skilldmg:
				atkbuff += 0.4 + 0.05 * self.mastery
				if self.mastery == 3: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
				
		return dps

class Penance(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 723  #######including trust
		maxatk = 916
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Penance Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Penance P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 43
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 2 and self.moduledmg: self.name += " alone"
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
		if self.buffs[4] > 0: self.name += f" {round(self.buffs[4],2)}hits/s"

			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.module == 2 and self.moduledmg:
			atkbuff += 0.08
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.4
			if self.mastery == 3: atk_scale = 2
			elif self.mastery == 2: atk_scale = 1.95
			elif self.mastery == 1: atk_scale = 1.9
			elif self.mastery == 0: atk_scale = 1.8

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgarts = max(final_atk *atk_scale *(1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			hitsbetween = 3 if self.mastery == 3 else 4
			dps += hitdmgarts/(hitsbetween*self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atk_scale = 1.1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *atk_scale *(1-res/100), final_atk * atk_scale * 0.05)
			dps = hitdmgarts * self.targets
		
		if self.skill == 3:
			self.atk_interval = 2.5
			atkbuff += 3.2 + 0.3 * self.mastery
			if self.mastery > 1: atkbuff -= 0.1

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.buffs[4] > 0:
			arts_scale = 0.5 if self.pot < 5 else 0.53
			if self.module == 2:
				if self.module_lvl == 2: arts_scale += 0.05
				if self.module_lvl == 3: arts_scale += 0.08
			artsdmg = max(final_atk * arts_scale * (1-res/100), final_atk * arts_scale * 0.05)
			dps += artsdmg * self.buffs[4]		
		
		return dps
			
class Phantom(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 73
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: 
					self.base_atk += 75
					self.clone_atk += 60
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
			selfhit += max(final_atk - defense, final_atk * 0.05)
			clonehit += max(final_clone - defense, final_clone * 0.05)
						
		
		dps = selfhit /(self.atk_interval/(1+aspd/100)) / count
		if self.talent:
			dps += clonehit /(self.atk_interval/(1+aspd/100)) / count
		return dps

class Pinecone(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 615  #######including trust
		maxatk = 722
		self.atk_interval = 2.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Pinecone Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Pinecone P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]

		
		if self.skill == 1 and not self.trait: self.name += " maxRange"   ##### keep the ones that apply
		
		if self.skill == 1 and self.talent1: self.name += " withSPboost"
		if self.skill == 2:
			if self.skilldmg: self.name += " 3rdActivation"
			else: self.name += " 1stActivation"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.trait: atk_scale = 1.5
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2 if self.mastery == 3 else 1.8 + 0.05 * self.mastery
			defignore = 250 if self.mastery == 3 else 210 + 10 * self.mastery
			newdef = max(0, defense - defignore)
			sp_cost = 9 if self.mastery == 3 else 10
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			sp_cost += 1.2 #sp lockout
			sprec_boost = 0.5 if self.pot > 4 else 0.45
			if self.talent1: sp_cost = sp_cost / (1+ sprec_boost)

			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets + skilldmg / sp_cost * self.targets
		
		if self.skill == 2:
			atkbuff += 0.6 if self.mastery == 3 else 0.4 + 0.05 * self.mastery
			atkbuff += 0.6 if self.skilldmg else 0.2
			atk_scale = 1.5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * self.targets
		return dps

class Platinum(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 489  #######including trust
		maxatk = 580
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Platinum Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Platinum P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		if self.moduledmg: self.name += " aerial target"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if self.module == 1 and self.moduledmg: atk_scale = 1.1
		talent_windup = 2.5
		talent_scale = 1
		max_talent_scale = 1.8
		if self.pot > 4: max_talent_scale += 0.1
		if self.module == 1:
			max_talent_scale += 0.1 * (self.module_lvl - 1)
		
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
		if self.skill == 2:
			atkbuff += 0.7 + 0.1 * self.mastery
			aspd -= 20
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		atkcycle = self.atk_interval/(1+aspd/100)
		actual_scale = atkcycle/talent_windup * (max_talent_scale - 1) + 1
		if atkcycle > talent_windup: actual_scale = max_talent_scale
		hitdmg = max(final_atk * atk_scale * actual_scale - defense, final_atk * atk_scale * actual_scale * 0.05)
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps
	
class Pozemka(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3:
					self.base_atk += 75
					self.typewriter_atk += 70				
				elif self.module_lvl == 2:
					self.base_atk += 65
					self.typewriter_atk += 50
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
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
		if self.moduledmg:
			atk_scale = 1.05
			
			
			
		if self.skill == 3:
			self.atk_interval = 1
			skill_scale = 1.7 + 0.1 * self.mastery
			skill_scale2 = 2.1 + 0.15 * self.mastery
			if self.mastery < 2: skill_scale2 += 0.05

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			if self.moduledmg or self.skilldmg:
				hitdmg = max(final_atk * atk_scale * skill_scale2 - newdef, final_atk * atk_scale * skill_scale2 * 0.05)	
			
			hitdmgTW = 0
			if self.talent1:
				hitdmgTW = max(self.typewriter_atk * skill_scale2 - newdef, self.typewriter_atk * skill_scale2 * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgTW

		return dps

class ProjektRed(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 488  #######including trust
		maxatk = 605
		self.atk_interval = 0.93   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 2: self.base_atk += 20
		
		self.skill = skill if skill in [1] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Projekt Red Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Projekt Red P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 74
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
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
		
		mindmg = 0.3
		if self.pot > 4: mindmg += 0.03
		if self.module == 2:
			aspd += 4
			if self.module_lvl == 2: mindmg += 0.07
			if self.module_lvl == 3: mindmg += 0.1
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.65 + 0.05* self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * mindmg)

			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Provence(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f"ModX{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avghit =  crate * critdmg + (1-crate) * hitdmg
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 1.6 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * cdmg - defense, final_atk * cdmg * 0.05)
			avghit =  crate * critdmg + (1-crate) * hitdmg
			
			dps = avghit/(self.atk_interval/(1+aspd/100))
		return dps

class Pudding(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = hitdmg/(self.atk_interval/(1+aspd/100)) * targetscaling[targets]

		
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = hitdmg/(self.atk_interval/(1+aspd/100))  * targetscaling[targets]
		return dps

class Qiubai(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 48
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
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
			
			hitdmgarts = max(final_atk * atk_scale *  (1+extrascale) * (1-res/100), final_atk* atk_scale * (1+extrascale) * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = (hitdmgarts+bonusdmg)/(self.atk_interval/(1+aspd/100)) * min(3, self.targets)
		return dps
	
class Quartz(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 1201  #######including trust
		maxatk = 1437
		self.atk_interval = 2.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 35
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Quartz Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Quartz P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 0.09 if self.pot > 4 else 0.08
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			aspd += 65 + 5 * self.mastery
			skill_scale = 1.2 if self.mastery == 3 else 1
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps * min(self.targets,2)

class Ray(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]

		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		 ##### keep the ones that apply
		if self.talent1: self.name += " with pet"
		if self.talent2: self.name += " After3Hits"


		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
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
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atk_scale *= 2.7 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05) * dmg_scale
			dps = hitdmg/(self.atk_interval/(1+aspd/100))  
			
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			return(self.skill_dps(defense,res) * 8 * (self.atk_interval/(1+self.buffs[2]/100)))
		else:
			return(self.skill_dps(defense,res))
	
class ReedAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 490  #######including trust
		maxatk = 600
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"ReedAlt Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"ReedAlt P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)

		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 42
				else: self.base_atk += 32
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		##### keep the ones that apply
		if not self.talent1 and not self.skill == 3: self.name += " w/o cinder"
		elif not self.skill == 3: self.name += " withCinder"

		if self.skilldmg and self.skill == 2: self.name += " Sandwiched"

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		dmg_scale = 1.3
		if self.pot > 2: dmg_scale = 1.32
		
		if not self.talent1:
			dmg_scale = 1
		
		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			aspd += 35
			if self.mastery == 3:
				atkbuff += 0.02
				aspd += 10
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = max(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
			
		if self.skill == 2:
			atk_scale = 1.8 + 0.2 * self.mastery
			if self.mastery == 0: atk_scale = 1.9
			multiplier = 2 if self.skilldmg else 1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(1-res/100,  0.05) *final_atk * atk_scale * dmg_scale * multiplier
			dps = hitdmgarts/0.8 * self.targets  #/1.5 * 3 (or /0.5) is technically the limit, the /0.8 come from the balls taking 2.4 for a rotation 
			
		if self.skill == 3:
			atkbuff += 0.4 + 0.05 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			atk_scale = 0.3 + 0.1 * self.mastery
			dmg_scale = 1.32 if self.pot > 2 else 1.3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			directhits = max(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale
			atkdps = min(self.targets,2) * directhits/(self.atk_interval/(1+aspd/100))
			skillhits = max(final_atk *(1-res/100), final_atk * 0.05) * dmg_scale * atk_scale
			skilldps = self.targets * skillhits
			dps = atkdps + skilldps
			
		return dps

class Rockrock(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 18
				elif self.module_lvl == 2: self.base_atk += 15
				else: self.base_atk += 13
				self.name += f"{self.module_lvl}"
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
		
		hitdmgarts = max(dmgperinterval *(1-res/100), dmgperinterval * 0.05)
		dps = hitdmgarts/(self.atk_interval/(1+aspd/100))
		return dps

class Rosa(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 966  #######including trust
		maxatk = 1142
		self.atk_interval = 2.4   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Rosa Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Rosa P{self.pot} S{self.skill}"
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
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		self.talent1 = self.talent1 and self.moduledmg
		
		if not self.talent1: self.name += " vsLight"
		else: self.name += " vsHeavy"
		
		if self.targets > 1 and not self.skill == 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		atkbuff += 0.1 if self.pot > 4 else 0.08
		
		additional_scale = 0
		defshred = 0
		if self.talent1: #aka: if heavy
			defshred = 0.6
			if self.module == 1:
				atk_scale = 1.15
				if self.module_lvl == 2: additional_scale = 0.4
				if self.module_lvl == 3: additional_scale = 0.6
		newdef = defense * (1-defshred)

			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = max(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg)/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.6 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = max(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg)/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:
			atkbuff += 0.1 + 0.05 * self.mastery
			maxtargets = 4 if self.mastery > 1 else 3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			extradmg = max(final_atk * atk_scale * additional_scale - newdef, final_atk * atk_scale * additional_scale * 0.05)
			dps = (hitdmg+extradmg) * min(self.targets,maxtargets)
			
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			duration = 8 if self.mastery == 3 else 7
			return(self.skill_dps(defense,res) * duration)
		elif self.skill == 2: return(self.skill_dps(defense,res) * 60)
		else: return(self.skill_dps(defense,res) * 30)

class Rosmontis(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 644  #######including trust
		maxatk = 748
		self.atk_interval = 2.1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Rosmontis Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Rosmontis P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		##### keep the ones that apply
		if self.skill == 3 and self.skilldmg: self.name += " withPillarDefshred"
		if self.skill == 3 and self.targets > 1: self.name += " TargetsOverlap"
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		#talent/module buffs
		bonushits = 1
		defshred = 160 if self.pot < 5 else 175
		if self.module == 1: 
			defshred += 30 * (self.module_lvl - 1)
			bonushits = 2
		newdef = max(0, defense- defshred)
	
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.2 + 0.2 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - newdef, final_atk  * 0.05)
			bonushitdmg = max(final_atk * 0.5 - newdef, final_atk  * 0.05) * bonushits
			skillhitdmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avghit = (sp_cost * (hitdmg + bonushitdmg) + skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
			
		if self.skill == 2:
			self.atk_interval = 3.15
			bonushits += 2
			if self.mastery == 0: atkbuff += 0.3
			if self.mastery == 0: atkbuff += 0.37
			if self.mastery == 0: atkbuff += 0.45
			if self.mastery == 0: atkbuff += 0.55

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - newdef, final_atk * 0.05)
			bonushitdmg = max(final_atk * 0.5 - newdef, final_atk  * 0.05) * bonushits
			dps = (hitdmg+ bonushitdmg)/(self.atk_interval/(1+aspd/100)) * self.targets
		if self.skill == 3:
			self.atk_interval = 1.05
			if self.skilldmg: newdef= max(0, newdef - 160)
			atkbuff += 0.75 if self.mastery == 3 else 0.4 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - newdef, final_atk * 0.05)
			bonushitdmg = max(final_atk * 0.5 - newdef, final_atk  * 0.05) * bonushits
			dps = (hitdmg+ bonushitdmg)/(self.atk_interval/(1+aspd/100)) * self.targets * min(self.targets,2)
		return dps
	
class Saga(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 62
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * min(self.targets,6)
			
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps * (1+dmg)

class Scene(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 371  #######including trust
		maxatk = 432
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 23
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Scene Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Scene P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		
		#Dronestats:
		dronelvl1 = 391
		dronelvl80 = 477
		self.droneinterval = 1.25
		self.drone_atk = dronelvl1 + (dronelvl80-dronelvl1) * (level-1) / (maxlvl-1)
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 36
				elif self.module_lvl == 2: self.base_atk += 28
				else: self.base_atk += 20
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.trait: self.name += " noDrones"   ##### keep the ones that apply
		elif not self.talent1: self.name += " 1Drone"
		else: self.name += " 2Drones"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		drones = 2 if self.talent1 else 1
		if not self.trait: drones = 0
		
		####the actual skills
		if self.skill == 1:
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			atkbuff += 0.3 + 0.1 * self.mastery
			final_drone = self.drone_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = max(final_drone - defense , final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+aspd/100)) * drones
		if self.skill == 2:
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			atkbuff += 1.3 if self.mastery == 3 else 0.8 + 0.15 * self.mastery
			final_drone = self.drone_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			hitdmgdrone = max(final_drone - defense, final_drone * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + hitdmgdrone/(self.droneinterval/(1+aspd/100)) * drones
		return dps
	
class Schwarz(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 746  #######including trust
		maxatk = 940
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 30
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Schwarz Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Schwarz P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 65
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 120
				elif self.module_lvl == 2: self.base_atk += 100
				else: self.base_atk += 80
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 3:
			if self.module == 2: self.moduledmg = True
			self.talent1 == True
		
		if not self.talent1 and not self.skill == 3: self.name += " minDefshred"
		if not self.talent2: self.name += " w/o2ndSniper"
		if self.moduledmg and self.module == 2 and not self.skill == 3: self.name += " directFront"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent2:
			atkbuff += 0.08
			if self.pot == 6: atkbuff+= 0.02
			if self.module == 1:
				if self.module_lvl == 2: atkbuff += 0.03
				if self.module_lvl == 3: atkbuff += 0.05
		
		crate = 0.2
		cdmg = 1.6
		defshred = 0.2
		if self.module == 2:
			cdmg += 0.05 * (self.module_lvl -1)
			if self.module_lvl > 1: defshred = 0.25
		
		newdef = defense * (1-defshred)
		if self.module == 2 and self.moduledmg:
			atk_scale = 1.05

			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.9 + 0.1 * self.mastery
			crate2 = 0.7 + self.mastery * 0.03
			if self.mastery == 3: crate2 = 0.8		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			if self.talent1: hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			else: hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			if self.talent1: skilldmg = max(final_atk * atk_scale * skill_scale - newdef, final_atk * atk_scale * skill_scale * 0.05)
			else: skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk * atk_scale * skill_scale * 0.05)
			skillcrit = max(final_atk * atk_scale * cdmg* skill_scale - newdef, final_atk * atk_scale * cdmg* skill_scale * 0.05)
			avghit = crate * critdmg + (1-crate) * hitdmg
			avgskill = crate2 * skillcrit + (1-crate2) * skilldmg
			
			sp_cost = 3 if self.mastery == 3 else 4
			avgphys = (sp_cost * avghit + avgskill) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			crate = 0.5 if self.mastery == 3 else 0.45
			atkbuff += 1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	
			if self.talent1: hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			else: hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			avghit = crate * critdmg + (1-crate) * hitdmg
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			self.atk_interval = 2.0
			atkbuff += 1.4 + 0.1 * self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			critdmg = max(final_atk * atk_scale * cdmg - newdef, final_atk * atk_scale * cdmg * 0.05)
			dps = critdmg/(self.atk_interval/(1+aspd/100))	
		
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			duration = 25 if self.mastery == 3 else 21 + self.mastery
			return(self.skill_dps(defense,res) * duration)
		else:
			return(self.skill_dps(defense,res))

class Shalem(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
			
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			shreddmg = max(final_atk * (1-newres/100), final_atk * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit) 
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		
		if self.skill == 2:
			hits = 6
			atk_scale = 0.65 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			countinghits =  (6 * int(3 /(self.atk_interval/(1+aspd/100))) + 3)/self.targets + 1
			nocrit = (1-crate)**countinghits
			
			hitdmg = max(final_atk * atk_scale * (1-res/100), final_atk * atk_scale * 0.05)
			shreddmg = max(final_atk * atk_scale * (1-newres/100), final_atk * atk_scale * 0.05)
			avgdmg = hitdmg * nocrit + shreddmg * (1-nocrit)
			dps = 6 * avgdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Siege(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 75
				elif self.module_lvl == 2: self.base_atk += 68
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 82
				elif self.module_lvl == 2: self.base_atk += 74
				else: self.base_atk += 65
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skilldmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * self.targets
			
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class SilverAsh(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 627  #######including trust
		maxatk = 763
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"SilverAsh Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"SilverAsh P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(6,max(1,targets))
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 70
				elif self.module_lvl == 2: self.base_atk += 60
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		
		if not self.trait and not self.skill == 3: self.name += " rangedAtk"   ##### keep the ones that apply
		if self.module == 1 and self.moduledmg and self.talent1: self.name += " vsElite"
		if self.targets > 1 and self.skill == 3: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if not self.trait and self.skill != 3: 
			atk_scale = 0.8
		
		atkbuff += 0.1
		if self.pot > 4: atkbuff += 0.02
		
		if self.module == 1:
			if self.module_lvl == 2:
				atkbuff += 0.1
				if self.talent1 and self.moduledmg: atk_scale *= 1.1
			if self.module_lvl == 3:
				atkbuff += 0.15
				if self.talent1 and self.moduledmg: atk_scale *= 1.15
		
		bonus = 0.1 if self.module == 1 else 0
		
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.25 + 0.2 * self.mastery	
			if self.mastery == 3: skill_scale += 0.05		
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale * skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avgphys = (sp_cost * hitdmg + 2* skillhitdmg) / (sp_cost + 1)
			dps = avgphys/(self.atk_interval/(1+aspd/100)) + bonusdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + bonusdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 1.4 + 0.2 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 6) + bonusdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,6)	
		return dps
	
class Skadi(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 922  #######including trust
		maxatk = 1095
		self.atk_interval = 1.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 33
		
		self.skill = skill if skill in [1,2,3] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Skadi Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Skadi P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 105
				elif self.module_lvl == 2: self.base_atk += 90
				else: self.base_atk += 70
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 85
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg: 
			if self.module == 1: self.name += " vsBlocked"
			if self.module == 2: self.name += " afterRevive"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		atkbuff += 0.14
		if self.pot > 4: atkbuff += 0.02
		if self.module == 2:
			if self.moduledmg: aspd += 30
			atkbuff += 0.04 * (self.module_lvl - 1)
		if self.module == 1 and self.moduledmg: atk_scale = 1.15
			
		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			aspd += 35
			if self.mastery == 3:
				atkbuff += 0.02
				aspd += 10
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 1.2 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk *atk_scale - defense, final_atk* atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			
		return dps

class Skalter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
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
			
			skilldmg = final_atk * skill_scale
			if self.talent1: skilldmg *= 2
			dps = skilldmg * self.targets
		return dps

	
class Specter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 631  #######including trust
		maxatk = 805
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 27
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Specter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Specter P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 52
				else: self.base_atk += 34
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 1: self.name += " vsBlocked"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		dmgbuff = 0
		if self.module == 1 and self.module_lvl > 1:
			if self.module_lvl == 3: dmgbuff = 0.05
			else: dmgbuff = 0.03

		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 1 if self.mastery == 3 else 0.6 + 0.15 * self.mastery
		if self.skill == 2:
			atkbuff += 1 + 0.2 * self.mastery
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			

		hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)*(1+dmgbuff)
			
		dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class SpecterAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 684  #######including trust
		maxatk = 817
		self.atk_interval = 1.2   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 33
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Spectral Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Spectral P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.trait = TrTaTaSkMo[0]
		self.skilldmg = TrTaTaSkMo[3]
		if not self.trait:
			if level != maxlvl: self.name = f"Spectral Lv{level} P{self.pot} (doll)" #####set op name
			else: self.name = f"Spectral P{self.pot} (doll)"
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 83
				elif self.module_lvl == 2: self.base_atk += 69
				else: self.base_atk += 50
				self.name += f"{self.module_lvl}"
			elif self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 33
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 3 and self.trait:
			if self.skilldmg: self.name += " vsHigherHP"
			else: self.name += " vsLowerHP"
		
		if self.targets > 1 and (self.skill == 3 or not self.trait): self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		if not self.trait:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			doll_scale = 0.4
			if self.module == 1:
				atkbuff += 0.15
				doll_scale = 0.2 + 0.2 * self.module_lvl
			hitdmg = max(final_atk * doll_scale * (1-res/100), final_atk * doll_scale * 0.05)
			return hitdmg
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 1.2 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 1.0 + 0.1 * self.mastery
			aspd += 34 if self.mastery == 0 else 32 + 6 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			self.atk_interval = 2.2
			atkbuff += 2 + 0.2 * self.mastery
			dmgbonus = 1.6 if self.mastery == 0 else 1.7
			if not self.skilldmg: dmgbonus = 1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05) * dmgbonus
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class Surtr(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 644  #######including trust
		maxatk = 772
		self.atk_interval = 1.25   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 28
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Surtr Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Surtr P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.skilldmg = TrTaTaSkMo[3]
		
	
		if self.skill == 1:
			if self.skilldmg: self.name += " KillingHitsOnly"
			else: self.name += " noKills"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		resignore = 20
		if self.pot > 4: resignore = 22
		newres = max(0, res - resignore)
			
		####the actual skills
		if self.skill == 1:
			atk_scale = 2.4 + 0.2 * self.mastery
			hits = 3
			if self.mastery == 3: 
				atk_scale += 0.1
				hits = 2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			skilldmgarts = max(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			avghit = (hits * hitdmgarts + skilldmgarts)/(hits + 1)
			if self.skilldmg:
				avghit = skilldmgarts	
			dps = avghit/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.8 + 0.1 *self.mastery
			if self.mastery == 3: atkbuff += 0.1
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			atk_scale = 1.6 if self.mastery == 3 else 1.5
			one_target_dmg = max(final_atk * atk_scale *(1-newres/100), final_atk * atk_scale * 0.05)
			two_target_dmg = max(final_atk * (1-newres/100), final_atk * 0.05)
			dps = one_target_dmg/(self.atk_interval/(1+aspd/100))
			if self.targets > 1:
				dps = 2 * two_target_dmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			atkbuff += 2.4 + 0.3 * self.mastery
			maxtargets = 4 if self.mastery == 3 else 3
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			dps = hitdmgarts/(self.atk_interval/(1+aspd/100)) * min(self.targets,maxtargets)
		return dps

class SwireAlt(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 40
				elif self.module_lvl == 2: self.base_atk += 35
				else: self.base_atk += 25
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		  ##### keep the ones that apply
		self.stacks = 9 if self.pot > 4 else 8
		
		if not self.talent1:
			self.name += " noStacks"
			self.stacks = 0
		else: self.name += f" {self.stacks}Stacks"
		
		if self.skilldmg and self.skill == 2: self.name += " 2HitBottles"
		if not self.skilldmg and self.skill == 1: " heals>attacks"
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
			
		####the actual skills
		if self.skill == 1:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			atkcycle= (self.atk_interval/(1+aspd/100))
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			if not self.skilldmg: dps = dps * (3/atkcycle-1) /(3/atkcycle)
		
		if self.skill == 2:
			skill_scale = 1.7 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skilldmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			if self.skilldmg: skilldmg *= 2
			
			atkcycle= (self.atk_interval/(1+aspd/100))
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			dps = dps * (3/atkcycle-1) /(3/atkcycle) + skilldmg / 3
		
		if self.skill == 3:
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * 2
		return dps

class TexasAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 53
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)

			artsdmg = 320 + 30 * self.mastery
			if self.mastery == 3: artsdmg -= 10
			
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + max(artsdmg *(1-res/100), artsdmg * 0.05)
		
		if self.skill == 2:
			resshred = 0.2
			if self.mastery == 1: resshred = 0.25
			elif self.mastery > 1: resshred = 0.3
			newres = res *(1-resshred)
			atkbuff += 0.4 + 0.05 * self.mastery

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmgarts = max(final_atk *(1-newres/100), final_atk * 0.05)
			
			dps = 2*hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 3:
			skillscale = 1 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			maxtargets = 4 if self.mastery == 3 else 3
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgarts = max(final_atk * skillscale *(1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
			dps += hitdmgarts * min(self.targets, maxtargets)
			
		return dps
		
class Tequila(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atk_scale = 2 + 0.1 * self.mastery
			maxtargets = 3 if self.skilldmg else 2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, maxtargets)
		
		return dps

class Thorns(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 604  #######including trust
		maxatk = 741
		self.atk_interval = 1.3   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 26
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Thorns Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Thorns P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = min(4,max(1,targets))
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 48
				else: self.base_atk += 39
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.skill == 1 and not self.trait: self.name += "rangedAtk"   ##### keep the ones that apply
		if self.talent1: self.name += " vsRanged"
		self.buffs = buffs
		if self.skill == 2: self.name += f" {round(buffs[4],2)}Hits/s"
		if self.skill == 3 and not self.skilldmg: self.name += " firstActivation"
		
		stacks = 4 if self.module_lvl == 3 else 3
		#if self.module == 1 and self.module_lvl > 1: self.name += f" {stacks}PsnStacks"


		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		if self.module == 1:
			aspd += 4 + self.module_lvl
		bonus = 0.1 if self.module == 1 else 0
		#talent1
		artsdps = 140 if self.pot > 4 else 125
		if self.module == 1 and self.module_lvl == 3: artsdps += 10
		if self.talent1: artsdps *= 2
		stacks = 1
		if self.module == 1 and self.module_lvl > 1: stacks = 4 if self.module_lvl == 3 else 3
		artsdps = artsdps * max((1-res/100),0.05) * stacks
		
		if self.skill == 1:
			atkbuff += 0.6 + 0.15 * self.mastery
			if self.mastery == 3: atkbuff -= 0.05
			atk_scale = 1 if self.trait else 0.8
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + artsdps + bonusdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2 and self.buffs[4] > 0:
			atk_scale = 0.8
			cooldown = 0.75 - 0.05 * self.mastery
			atkbuff += 0.4 + 0.05 * self.mastery
			if self.mastery == 3: atkbuff += 0.05
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			if(1/self.buffs[4] < cooldown):
				dps = (hitdmg/cooldown + artsdps + bonusdmg/cooldown) * min(self.targets,4)
			else:
				cooldown = 1/self.buffs[4]
				dps = (hitdmg/cooldown + artsdps) * min(self.targets,4)
		if self.skill == 3:
			bufffactor = 2 if self.skilldmg else 1
			aspd += bufffactor * (16 + 3 * self.mastery)
			atkbuff += bufffactor * (0.4 + 0.05 * self.mastery)
			if self.mastery == 3: atkbuff += 0.05 * bufffactor
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			bonusdmg = max(final_atk * bonus *(1-res/100), final_atk * bonus * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) + artsdps + bonusdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Toddifons(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
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
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
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
			
			hitdmg = max(final_atk * skill_scale * atk_scale - newdef, final_atk * skill_scale * atk_scale * 0.05)

			
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			self.atk_interval = 2.7
			skill_scale = 2.1 + 0.1 * self.mastery
			skill_scale2 = 0.8 if self.mastery == 3 else 0.7
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * skill_scale * atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			hitdmg2 = max(final_atk * skill_scale2 * atk_scale - defense, final_atk * skill_scale2 * atk_scale * 0.05) * self.targets
			
			dps = (hitdmg+hitdmg2)/(self.atk_interval/(1+aspd/100))
		return dps

class Tomimi(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 539  #######including trust
		maxatk = 635
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Tomimi Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Tomimi P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 50
				elif self.module_lvl == 2: self.base_atk += 40
				else: self.base_atk += 30
				self.name += f"{self.module_lvl}"
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
		atkbuff += 1
		if self.pot > 4: atkbuff += 0.2
		if self.module == 2: atkbuff += 0.05 * (self.module_lvl -1)
			
		####the actual skills
		if self.skill == 1:
			aspd += 60 + 10 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			crate = 0.7 + 0.1 * self.mastery
			atk_scale = 1.9 + 0.15 * self.mastery
			if self.mastery == 3: atk_scale = 2.2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			critdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			avgnormal = (1-crate) * hitdmg
			avgstun = crate / 3 * hitdmg
			avgcrit = crate / 3 * critdmg
			avgaoe = crate / 3 * hitdmg * self.targets
			dps = (avgnormal + avgstun + avgcrit + avgaoe)/(self.atk_interval/(1+aspd/100))
		return dps

class Totter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 813  #######including trust
		maxatk = 970
		self.atk_interval = 2.4  #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Totter Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Totter P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 55
				elif self.module_lvl == 2: self.base_atk += 47
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.talent1: self.name += " vsInvis"
		if self.moduledmg and self.module == 1: self.name += " vsHeavy"
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		if self.talent1:
			atkbuff += 0.2 if self.pot > 4 else 0.17
			if self.module == 1: atkbuff += 0.05 * (self.module_lvl - 1)

		if self.module == 1 and self.moduledmg:
			atk_scale = 1.1
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.9 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			skillhitdmg = max(final_atk * atk_scale *skill_scale - defense, final_atk* atk_scale * skill_scale * 0.05) * min(self.targets,2)
			sp_cost = 3
			
			avgphys = (sp_cost * hitdmg + skillhitdmg) / (sp_cost + 1)
			
			dps = avgphys/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			aspd += 35 + 5 * self.mastery
			skill_scale = 2.1 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			if self.targets == 1: hitdmg = max(final_atk * skill_scale *  atk_scale - defense, final_atk * skill_scale * atk_scale * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 3)
		return dps

class Typhon(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 977  #######including trust
		maxatk = 1155
		self.atk_interval = 2.4   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 34
		
		self.skill = skill if skill in [1,2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Typhon Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Typhon P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 78
				else: self.base_atk += 60
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if not self.talent1: self.name += " noDefIgnore"
		if not self.talent2: self.name += " noCrits"
		else:
			if self.skill == 3: self.name += " 1Crit/salvo"
			else: self.name += " allCrits"
		
		if self.moduledmg and self.module == 1: self.name += " vsHeavy"
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		crit_scale = 1
		self.atk_interval = 2.4
		def_ignore = 0
		if self.talent1:
			def_ignore = 0.5
			if self.module == 1 and self.module_lvl > 1:
				def_ignore += 0.05 * (self.module_lvl -1)
		if self.talent2:
			crit_scale = 1.7 if self.pot > 4 else 1.6
		
		if self.module == 1 and self.moduledmg:
			atk_scale = 1.15

		if self.skill == 1:
			atkbuff += 0.34 + 0.03 * self.mastery
			if self.mastery == 3:
				atkbuff += 0.02
				aspd += 45
			else: aspd += 35
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]		
			hitdmg = max(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)		
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 2:
			atkbuff += 0.35 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)
			dps = 2 * hitdmg/(self.atk_interval/(1+aspd/100))
		if self.skill == 3:
			self.atk_interval = 5.5
			hits = 4 if self.mastery == 0 else 5
			atk_scale *= 1.6 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense*(1-def_ignore), final_atk * atk_scale * 0.05)
			critdmg = max(final_atk * atk_scale * crit_scale - defense*(1-def_ignore), final_atk * atk_scale * crit_scale * 0.05)
			totaldmg = hits * hitdmg
			if self.talent2:
				totaldmg = (hits-1)*hitdmg + critdmg
			dps = totaldmg/(self.atk_interval/(1+aspd/100))
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			ammo = 8 if self.mastery == 0 else 7 + self.mastery
			return(self.skill_dps(defense,res) * ammo * (self.atk_interval/(1+self.buffs[2]/100)))
		else:
			return(self.skill_dps(defense,res))

class Ulpianus(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 1397  #######including trust
		maxatk = 1649
		self.atk_interval = 2.5   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 45
		
		self.skill = skill if skill in [2,3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Ulpianus Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Ulpianus P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		
		maxkills = 10 if self.pot > 4 else 9
		if self.talent2: self.name += f" {maxkills}kills"
		if self.talent2:
			self.base_atk += 30 * maxkills
		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		flatbuff = 0
		#talent/module buffs
		
			
		####the actual skills
		if self.skill == 1:
			skill_scale = 2.1 + 0.2 * self.mastery
			sp_cost = 4 if self.mastery == 3 else 5
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	+ flatbuff
		if self.skill == 2:
			atkbuff += 1.3 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	+ flatbuff
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,3)
		if self.skill == 3:
			atkbuff += 2.3 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]	+ flatbuff
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class Utage(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
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
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps

class Vigil(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 30
				elif self.module_lvl == 2: self.base_atk += 25
				else: self.base_atk += 20
				self.name += f"{self.module_lvl}"
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
		newdef = max(0, defense - defignore)
		wolfdef = max(0, defense - 200) if self.pot > 4 else max(0, defense - 175)
		####the actual skills
		if self.skill == 2:
			skill_scale = 1.7 + 0.1 * self.mastery
			sp_cost = 5 if self.mastery == 3 else 6
			
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			final_wolf  = self.wolf_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = max(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgwolfskill = max(final_wolf * skill_scale - wolfdef, final_wolf * skill_scale * 0.05)
			
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
			
			hitdmg = max(final_atk * atk_scale - newdef, final_atk * atk_scale * 0.05)
			hitdmgwolf = max(final_wolf - wolfdef, final_wolf * 0.05)
			hitdmgarts = max(final_atk * skill_scale * (1-res/100), final_atk * 0.05)
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=70
		lvl1atk = 528  #######including trust
		maxatk = 618
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		if self.pot > 3: self.base_atk += 24
		
		self.skill = skill if skill in [1,2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Vigna Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Vigna P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,2] else 2 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 2:
				self.name += " ModY"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.moduledmg and self.module == 2: self.name += " vsLowHp"
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		crate = 0.3
		cdmg = 1.1 if self.pot > 4 else 1
		if self.module == 2:
			crate += 0.05 * (self.module_lvl -1)
			if self.moduledmg: atk_scale = 1.15
			
		####the actual skills
		if self.skill == 1:
			atkbuff += 0.5 + 0.1 * self.mastery
		if self.skill == 2:
			atkbuff += 2 if self.mastery == 3 else 1.5 + 0.15 * self.mastery
			self.atk_interval = 1.5
			
		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		final_atk_crit = self.base_atk * (1+atkbuff+cdmg) + self.buffs[1]
		
		hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
		critdmg = max(final_atk_crit * atk_scale - defense, final_atk_crit * atk_scale * 0.05)
		avgdmg = crate * critdmg + (1-crate) * hitdmg
		dps = avgdmg/(self.atk_interval/(1+aspd/100))
		return dps
		
class Virtuosa(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
			hitdmg = max(final_atk * (1-res/100), final_atk * 0.05)

			skilldmg =max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			
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
			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05)
			artsdps = hitdmgarts/(self.atk_interval/(1+aspd/100))
			targetEledps = eleDamage / (eleDuration + eleThreshold/eleApplicationTarget)
			ambientEledps = eleDamage / (eleDuration + eleThreshold/eleApplicationBase)
			
			dps = min(self.targets, 2) * (artsdps + targetEledps)
			if self.targets > 2:
				dps += ambientEledps * (self.targets -2)			
			
		
		if self.skill == 3:
			eleBonus *= 2.2 + 0.1 * self.mastery
			atkbuff += 1.4 + 0.15 * self.mastery
			if self.mastery > 1: atkbuff -= 0.05
			eleThreshold = eleThreshold / (1 + eleBonus)
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			eleApplication = final_atk * 0.1
			applicationDuration = eleThreshold / eleApplication
			dps = self.targets * eleDamage / (eleDuration + applicationDuration)			

		return dps
	
class Viviana(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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

			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale
			skilldmg = 2 * max(final_atk * cdmg * (1-res/100), final_atk * cdmg * 0.05) * dmg_scale
			avgdmg = crate * skilldmg + (1-crate) * hitdmgarts
			dps = avgdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		if self.skill == 3:
			self.atk_interval = 1.75
			atkbuff += 1.1 if self.mastery == 3 else 0.75 + 0.1 * self.mastery
			hits = 3 if self.skilldmg else 2
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]

			hitdmgarts = max(final_atk * (1-res/100), final_atk * 0.05) * dmg_scale

			dps = hits * hitdmgarts/(self.atk_interval/(1+aspd/100))
		
		return dps

class Vulcan(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 689  #######including trust
		maxatk = 870
		self.atk_interval = 1.6   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 1

		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Vulcan Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Vulcan P{self.pot} S{self.skill}"
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
				self.name += " ModX"
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		

		
		if self.targets > 1: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
			
	
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		####the actual skills
		if self.skill == 2:
			self.atk_interval = 2 
			atkbuff += 1.05 + 0.15 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets,2)
		return dps

class Walter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 673  #######including trust
		maxatk = 777
		self.atk_interval = 2.1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.shadow_atk = self.base_atk
		self.pot = pot if pot in range(1,7) else 1
		if self.pot > 3: self.base_atk += 32
		
		self.skill = skill if skill in [3] else 3 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Wis'adel Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Wis'adel P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		
		self.talent1 = TrTaTaSkMo[1]
		self.talent2 = TrTaTaSkMo[2]
		self.skilldmg = TrTaTaSkMo[3]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 65
				elif self.module_lvl == 2: self.base_atk += 55
				else: self.base_atk += 45
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		##### keep the ones that apply
		if self.skill == 2 and self.skilldmg: self.name += " overdrive"
		if self.skill == 3: self.name += " 3shadows"
		
		if self.targets > 1: self.name += f" {self.targets}targets"
		
		self.buffs = buffs
			
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		
		if self.module == 1:
			aspd += 4 + self.module_lvl
		
		#talent/module buffs
		bonushits = 2 if self.module == 1 else 1
		maintargetscale = 1.15
		crate = 0.15
		shadowexplosion = 1.6 if self.pot >4 else 1.5
		if self.module == 1:
			if self.module_lvl == 2: 
				shadowexplosion += 0.2
				maintargetscale += 0.05
			if self.module_lvl == 3: 
				shadowexplosion += 0.25
				maintargetscale += 0.1
	
		####the actual skills
		if self.skill == 1:
			skill_scale = 1.2 + 0.2 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - newdef, final_atk  * 0.05)
			bonushitdmg = max(final_atk * 0.5 - defense, final_atk  * 0.05) * bonushits
			skillhitdmg = max(final_atk * skill_scale * (1-res/100), final_atk * skill_scale * 0.05)
			sp_cost = 2 if self.mastery == 3 else 3
			avghit = (sp_cost * (hitdmg + bonushitdmg) + skillhitdmg) / (sp_cost + 1) * self.targets
			dps = avghit/(self.atk_interval/(1+aspd/100))
			
			
		if self.skill == 2:
			self.atk_interval = 1.4
			atkbuff += 0.35 if self.mastery == 3 else 0.25

			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			bonushitdmg = max(final_atk * 0.5 - defense, final_atk  * 0.05) * bonushits
			dps = (hitdmg+ bonushitdmg)/(self.atk_interval/(1+aspd/100)) * self.targets
		
		if self.skill == 3:
			
			self.atk_interval = 5
			atkbuff += 1.5 + 0.1 * self.mastery
			skill_scale = 1.9 + 0.1 * self.mastery
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			mainhitdmg = max(final_atk * maintargetscale *skill_scale - defense, final_atk * maintargetscale * skill_scale * 0.05)
			aoehitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			mainaftershocks = max(final_atk * maintargetscale * skill_scale * 0.5 - defense, final_atk * skill_scale * maintargetscale * 0.5 * 0.05)
			aoeaftershocks = max(final_atk * 0.5 - defense, final_atk * 0.5 * 0.05)
			shadowexplosion = max(final_atk * shadowexplosion - defense, final_atk * shadowexplosion * 0.05)
			if self.targets == 1:
				dps = (mainhitdmg + mainaftershocks * bonushits + shadowexplosion)/(self.atk_interval/(1+aspd/100))
			else:
				#main target
				dmg = mainhitdmg + mainaftershocks * bonushits + (self.targets - 1) * (aoehitdmg + aoeaftershocks * bonushits) + min(2,self.targets) * self.targets * shadowexplosion
				dps = dmg/(self.atk_interval/(1+aspd/100))
		
		shadowthorns = 1 #if self.talent2 else 0
		if self.skill == 3: shadowthorns += 2
		shadowhit = max(self.shadow_atk * (1-res/100), self.shadow_atk * 0.05) * shadowthorns
		dps += shadowhit/4
		return dps
	
	def total_dmg(self, defense, res):
		if self.skill == 3:
			self.atk_interval = 5
			return(self.skill_dps(defense,res) * 6 * (self.atk_interval/(1+self.buffs[2]/100)))
		else:
			return(self.skill_dps(defense,res))

class Whislash(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
		maxlvl=80
		lvl1atk = 571  #######including trust
		maxatk = 675
		self.atk_interval = 1.05   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6
		
		self.skill = skill if skill in [2] else 2 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Whislash Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Whislash P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		self.targets = max(1,targets)
		self.trait = TrTaTaSkMo[0]
		self.moduledmg = TrTaTaSkMo[4]
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 52
				elif self.module_lvl == 2: self.base_atk += 47
				else: self.base_atk += 35
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		if self.module == 1: self.trait = self.trait and self.moduledmg
		
		if not self.trait: self.name += " blocking"

		
		if self.targets > 1 and self.skill == 2: self.name += f" {self.targets}targets" ######when op has aoe
		
		self.buffs = buffs
				
	def skill_dps(self, defense, res):
		dps = 0
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]
		atk_scale = 1
		
		#talent/module buffs
		talentbuff = 8 if self.pot > 4 else 6
		
		if self.trait:
			atk_scale = 1.3 if self.module == 1 else 1.2
			
		####the actual skills
		if self.skill == 2:
			atkbuff += 0.35 if self.mastery == 0 else 0.3 + 0.1 * self.mastery
			
			talentscaling = 1.7 + 0.1 * self.mastery
			aspd += talentbuff * talentscaling
			
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)

			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(3, self.targets)
		return dps

class Wildmane(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0,0,0],**kwargs):
		maxlvl=90
		lvl1atk = 538  #######including trust
		maxatk = 628
		self.atk_interval = 1.0   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		
		self.skill = skill if skill in [1,2] else 1 ###### check implemented skills
		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Wildmane Lv{level} P{self.pot} S{self.skill}" #####set op name
		else: self.name = f"Wildmane P{self.pot} S{self.skill}"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"

		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 60
				elif self.module_lvl == 2: self.base_atk += 50
				else: self.base_atk += 40
				self.name += f"{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0
		
		
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
			aspd += 135 if self.mastery == 3 else 100 + 10 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		
		if self.skill == 2:
			atkbuff += 0.8 if self.mastery == 3 else 0.6 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100))
		return dps



class YatoAlter(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
		
		self.module = module if module in [0,1,2] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 48
				elif self.module_lvl == 2: self.base_atk += 43
				else: self.base_atk += 36
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			hitdmgarts = max(final_atk * extra_arts * (1-res/100), final_atk * extra_arts * 0.05)
			dps = (hitdmg+hitdmgarts)/(self.atk_interval/(1+aspd/100)) * 10 / 3
		if self.skill == 2:
			extra_arts *= 2.1 if self.mastery == 0 else 2.05 + 0.15 * self.mastery
			atk_scale *= 1.5 if self.mastery == 3 else 1.3 + 0.05 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * atk_scale - defense, final_atk * atk_scale * 0.05)
			hitdmgarts = max(final_atk * atk_scale * extra_arts * (1-res/100), final_atk * atk_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts) * self.targets * 16
		if self.skill == 3:
			skill_scale = 3 if self.mastery == 3 else 2.6 + 0.1 * self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			hitdmg = max(final_atk * skill_scale - defense, final_atk * skill_scale * 0.05)
			hitdmgarts = max(final_atk * skill_scale * extra_arts * (1-res/100), final_atk * skill_scale * extra_arts * 0.05)
			dps = (hitdmg+ hitdmgarts)*self.targets
		return dps

class ZuoLe(Operator):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, targets=1, TrTaTaSkMo=[True,True,True,True,True], buffs=[0,0,0],**kwargs):
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
				self.name += " ModX"
				if self.module_lvl == 3: self.base_atk += 90
				elif self.module_lvl == 2: self.base_atk += 75
				else: self.base_atk += 55
				self.name += f"{self.module_lvl}"
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
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skilldmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			
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
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			dps = hitdmg/(self.atk_interval/(1+aspd/100)) * min(self.targets, 2)
		
		if self.skill == 3:
			atk_scale = 2.2 if self.mastery == 0  else 2.15 + 0.1 * self.mastery
			hits = 6
			sp_cost = 28 - self.mastery
			final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
			
			hitdmg = max(final_atk - defense, final_atk * 0.05)
			skilldmg = max(final_atk * atk_scale - defense, final_atk* atk_scale * 0.05)
			skilldmg2= max(2*final_atk * atk_scale - defense, 2*final_atk* atk_scale * 0.05)
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
op_dict = {"absinthe": Absinthe, "aciddrop": Aciddrop, "<:amimiya:1229075612896071752>": Amiya, "amiya": Amiya, "amiya2": AmiyaGuard, "guardmiya": AmiyaGuard, "amiyaguard": AmiyaGuard, "amiyaalter": AmiyaGuard, "amiyaalt": AmiyaGuard, "andreana": Andreana, "angelina": Angelina, "april": April, "archetto": Archetto, "arene": Arene, "asbestos":Asbestos, "ascalon": Ascalon, "ash": Ash, "ashlock": Ashlock, "astesia": Astesia, "astgenne": Astgenne, "aurora": Aurora, "<:aurora:1077269751925051423>": Aurora, "bagpipe": Bagpipe, "beehunter": Beehunter, "bibeak": Bibeak, "blaze": Blaze, "<:blaze_smug:1185829169863589898>": Blaze, "<:blemi:1077269748972273764>":Blemishine, "blemi": Blemishine, "blemishine": Blemishine, "bp": BluePoison, "bluepoison": BluePoison, "<:bpblushed:1078503457952104578>": BluePoison, "broca": Broca,
		"cantabile": Cantabile, "canta": Cantabile, "caper": Caper, "carnelian": Carnelian, "ceobe": Ceobe, "chen": Chen, "chalter": ChenAlter, "chenalter": ChenAlter, "chenalt": ChenAlter, "chongyue": Chongyue, "click": Click, "coldshot": Coldshot, "conviction": Conviction, "dagda": Dagda, "degenbrecher": Degenbrecher, "degen": Degenbrecher,"dobermann": Dobermann, "doc": Doc, "dokutah": Doc, "dorothy" : Dorothy, "durin": Durin, "god": Durin, "dusk": Dusk, "ebenholz": Ebenholz, "ela": Ela, "estelle": Estelle, "eunectes": Eunectes, "fedex": ExecutorAlter, "executor": ExecutorAlter, "executoralt": ExecutorAlter, "executoralter": ExecutorAlter, "exe": ExecutorAlter, "foedere": ExecutorAlter, "exu": Exusiai, "exusiai": Exusiai, "<:exucurse:1078503466353303633>": Exusiai, "<:exusad:1078503470610522264>": Exusiai, "eyja": Eyjafjalla, "eyjafjalla": Eyjafjalla, 
		"fang": FangAlter, "fangalter": FangAlter, "fartooth": Fartooth, "fia": Fiammetta, "fiammetta": Fiammetta, "<:fia_ded:1185829173558771742>": Fiammetta, "firewhistle": Firewhistle, "flamebringer": Flamebringer, "flametail": Flametail, "flint": Flint, "folinic" : Folinic,
		"franka": Franka, "fuze": Fuze, "gavial": GavialAlter, "gavialter": GavialAlter, "GavialAlter": GavialAlter, "gladiia": Gladiia, "gg": Goldenglow, "goldenglow": Goldenglow, "grani": Grani, "greythroat": GreyThroat, "haze": Haze, "hellagur": Hellagur, "hibiscus": Hibiscus, "hibiscusalt": Hibiscus, "highmore": Highmore, "hoe": Hoederer, "hoederer": Hoederer, "<:dat_hoederer:1219840285412950096>": Hoederer, "hool": Hoolheyak, "hoolheyak": Hoolheyak, "horn": Horn, "hoshiguma": Hoshiguma, "hoshi": Hoshiguma, "humus": Humus, "iana": Iana, "ifrit": Ifrit, "indra": Indra, "ines": Ines, "irene": Irene, "jessica": JessicaAlter, "jessica2": JessicaAlter, "jessicaalt": JessicaAlter, "<:jessicry:1214441767005589544>": JessicaAlter, "jester":JessicaAlter, "jessicaalter": JessicaAlter, 
		"kafka": Kafka, "kazemaru": Kazemaru, "kjera": Kjera, "kroos": KroosAlter, "kroosalt": KroosAlter, "kroosalter": KroosAlter, "3starkroos": Kroos, "kroos3star": Kroos, "lapluma": LaPluma, "pluma": LaPluma,
		"lappland": Lappland, "lappy": Lappland, "<:lappdumb:1078503487484207104>": Lappland, "lava": Lavaalt, "lavaalt": Lavaalt,"lavaalter": Lavaalt, "lessing": Lessing, "leto": Leto, "logos": Logos, "lin": Lin, "ling": Ling, "lunacub": Lunacub, "lutonada": Lutonada, "magallan": Magallan, "maggie": Magallan, "manticore": Manticore, "matoimaru": Matoimaru, "melantha": Melantha, "meteor":Meteor, "meteorite": Meteorite, "mizuki": Mizuki, "mlynar": Mlynar, "uncle": Mlynar, "monster": Mon3tr, "mon3ter": Mon3tr, "mon3tr": Mon3tr, "kaltsit": Mon3tr, "morgan": Morgan, "mountain": Mountain, "mousse": Mousse, "mudmud": Mudrock, "mudrock": Mudrock,
		"mumu": MumuDorothy, "muelsyse": MumuDorothy, "mumudorothy": MumuDorothy,  "mumu1": MumuDorothy, "mumu2": MumuEbenholz,"mumuebenholz": MumuEbenholz, "mumu3": MumuCeobe,"mumuceobe": MumuCeobe, "mumu4": MumuMudrock,"mumumudrock": MumuMudrock, "mumu5": MumuRosa,"mumurosa": MumuRosa, "mumu6": MumuSkadi,"mumuskadi": MumuSkadi, "mumu7": MumuSchwarz,"mumuschwarz": MumuSchwarz, 
		"ntr": NearlAlter, "ntrknight": NearlAlter, "nearlalter": NearlAlter, "nearl": NearlAlter, "nian": Nian, "odda": Odda, "pallas": Pallas, "penance": Penance, "phantom": Phantom, "pinecone": Pinecone, "platinum": Platinum, "pozy": Pozemka, "pozemka": Pozemka, "projekt": ProjektRed, "red": ProjektRed, "projektred": ProjektRed, "provence": Provence, "pudding": Pudding, "qiubai": Qiubai,"quartz": Quartz, "ray": Ray, "reed": ReedAlter, "reedalt": ReedAlter, "reedalter": ReedAlter,"reed2": ReedAlter, "rockrock": Rockrock, "rosa": Rosa, "rosmontis": Rosmontis, "saga": Saga, "bettersiege": Saga, "scene": Scene, "schwarz": Schwarz, "shalem": Shalem, 
		"siege": Siege, "silverash": SilverAsh, "sa": SilverAsh, "skadi": Skadi, "<:skadidaijoubu:1078503492408311868>": Skadi, "<:skadi_hi:1211006105984041031>": Skadi, "<:skadi_hug:1185829179325939712>": Skadi, "kya": Skadi, "kyaa": Skadi, "skalter": Skalter, "skadialter": Skalter, "specter": Specter, "shark": SpecterAlter, "specter2": SpecterAlter, "spectral": SpecterAlter, "specteralter": SpecterAlter, "laurentina": SpecterAlter, "surtr": Surtr, "jus": Surtr, "swire": SwireAlt, "swire2": SwireAlt,"swirealt": SwireAlt,"swirealter": SwireAlt, "texas": TexasAlter, "texasalt": TexasAlter, "texasalter": TexasAlter, "texalt": TexasAlter, "tequila": Tequila, "thorns": Thorns, "thorn": Thorns,"toddifons":Toddifons, "tomimi": Tomimi, "totter": Totter, "typhon": Typhon, "<:typhon_Sip:1214076284343291904>": Typhon, 
		"ulpianus": Ulpianus, "utage": Utage, "vigil": Vigil, "trash": Vigil, "garbage": Vigil, "vigna": Vigna, "virtuosa": Virtuosa, "<:arturia_heh:1215863460810981396>": Virtuosa, "arturia": Virtuosa, "viviana": Viviana, "vivi": Viviana, "vulcan": Vulcan, "walter": Walter, "wisadel": Walter, "whislash": Whislash, "aunty": Whislash, "wildmane": Wildmane, "yato": YatoAlter, "yatoalter": YatoAlter, "kirinyato": YatoAlter, "kirito": YatoAlter, "zuo": ZuoLe, "zuole": ZuoLe}

#The implemented operators
operators = ["Absinthe","Aciddrop","Amiya","AmiyaGuard","Andreana","Angelina","April","Archetto","Arene","Asbestos","Ascalon","Ash","Ashlock","Astesia","Astgenne","Aurora","Bagpipe","Beehunter","Bibeak","Blaze","Blemishine","BluePoison","Broca","Cantabile","Caper","Carnelian","Ceobe","Chen","Chalter","Chongyue","Click","Coldshot","Conviction","Dagda","Degenbrecher","Dobermann","Doc","Dorothy","Durin","Dusk","Ebenholz","Ela","Estelle","Eunectes","ExecutorAlt","Exusiai","Eyjafjalla","FangAlter","Fartooth","Fiammetta","Firewhistle","Flamebringer","Flametail","Flint","Folinic","Franka","Fuze","Gavialter","Gladiia","Goldenglow","Grani","Greythroat",
		"Haze","Hellagur","Hibiscus","Highmore","Hoederer","Hoolheyak","Horn","Hoshiguma","Humus","Iana","Ifrit","Indra","Ines","Irene","JessicaAlt","Kazemaru","Kjera","Kroos","Kroos3star","Lapluma","Lappland","LavaAlt","Lessing","Logos","Leto","Lin","Ling","Lunacub","Lutonada","Magallan","Manticore","Matoimaru","Melantha","Meteor","Meteorite","Mizuki","Mlynar","Mon3tr","Morgan","Mountain","Mousse","Mudrock","Muelsyse(type !mumu for more info)","NearlAlter","Nian","Odda","Pallas","Penance","Phantom","Pinecone","Platinum","Pozemka","ProjektRed","Provence","Pudding","Qiubai","Quartz","Ray","ReedAlt","Rockrock",
		"Rosa","Rosmontis","Schwarz","Siege","SilverAsh","Skadi","Skalter","Specter","SpecterAlter","Surtr","SwireAlt","TexasAlter","Tequila","Thorns","Toddifons","Tomimi","Totter","Typhon","Ulpianus","Utage","Vigil","Vigna","Virtuosa","Viviana","Vulcan","Wis'adel","Whislash","Wildmane","YatoAlter","ZuoLe"]

#copy from op_dict to show the plot. should only be used for testing
test_ops = {}

if __name__ == "__main__":
	for x in op_dict.keys():
		for skill in [1,2,3]:
			operator = op_dict[x](-10,-1, skill, 3,-1,3, 1, TrTaTaSkMo= [True,True,True,True,True],buffs=[0,0,0,0,1],bonus=False)
			try:
				assert operator.skill_dps(100,40) != 0
			except AssertionError:
				print(f"The following request has returned 0 damage:\n"+ operator.get_name())
	print("Seems to be working just fine.\nMake sure you added the new operator to the operator dictionary.")
	
	if len(list(test_ops.keys())) != 0:
		defences = np.linspace(0,3000,301)
		damages = np.zeros(301)
		resistances = np.linspace(0,120,301)
		for x in test_ops.keys():
			for skill in [1,2,3]:
				operator = test_ops[x](-10,-1, skill, 3,-1,3, 1, TrTaTaSkMo= [True,True,True,True,True],buffs=[0,0,0,0,1],bonus=False)
				op_name = operator.get_name()
				for i in range(301):
					damages[i] = operator.skill_dps(defences[i],resistances[i])
				pl.plot(defences, damages, label=op_name)
		pl.legend()
		pl.show()
