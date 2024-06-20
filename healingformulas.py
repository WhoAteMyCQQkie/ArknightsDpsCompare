class Healer:
	
	def avg_dps(self,defense,res):
		print("The operator has not implemented the avg_dps method")
		return -100
		
	def skill_dps(self, defense, res, targets, high):
		print("The operator has not implemented the skill_dps method")
		return -100
	
	def skill_hps(self):
		return -100
		
	def avg_hps(self):
		return -100
	
	def get_name(self):
		return self.name

class Example(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0,0]):
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
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 20
		skillcost = 50
		atkbuff = self.buffs[0]
		aspd = self.buffs[2]

		
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
		basehps = final_atk/(self.atk_interval/(1+aspd/100)) * (1+buffs[3])
		avghps = (basehps * skillcost/(1+buffs[4]) + skillhps * skillduration)/(skillduration + skillcost/(1+buffs[4]))
		self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}*"
		return self.name

class Eyjaberry(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
		maxlvl=70
		lvl1atk = 436  #######including trust
		maxatk = 520
		self.atk_interval = 1   #### in seconds
		level = lvl if lvl > 0 and lvl < maxlvl else maxlvl
		self.base_atk = lvl1atk + (maxatk-lvl1atk) * (level-1) / (maxlvl-1)
		self.pot = pot if pot in range(1,7) else 6

		self.mastery = mastery if mastery in [0,1,2,3] else 3
		if level != maxlvl: self.name = f"Myrtle Lv{level} P{self.pot} S2" #####set op name
		else: self.name = f"Myrtle P{self.pot} S2"
		if self.mastery == 0: self.name += "L7"
		elif self.mastery < 3: self.name += f"M{self.mastery}"
		
		self.module = module if module in [0,1] else 1 ##### check valid modules
		self.module_lvl = module_lvl if module_lvl in [1,2,3] else 3		
		if level >= maxlvl-30:
			if self.module == 1:
				self.name += f" ModX{self.module_lvl}"
			else: self.name += " no Mod"
		else: self.module = 0

		self.buffs = buffs
		self.boost = boost
	
	def skill_hps(self, **kwargs):
		skillhps = 0
		basehps = 0
		avghps = 0
		skillduration = 16
		skillcost = 27 - self.mastery
		atkbuff = self.buffs[0]
		
		extraheal = 28 if self.pot > 4 else 25
		if self.module == 1:
			if self.module_lvl == 2: extraheal += 3
			if self.module_lvl == 3: extraheal += 5

		final_atk = self.base_atk * (1+atkbuff) + self.buffs[1]
		skillhps = final_atk * (0.35 + 0.05 * self.mastery) * (1+self.buffs[3])
		avghps = (basehps * skillcost/(1+self.boost) + skillhps * skillduration)/(skillduration + skillcost/(1+self.boost))
		self.name += f": **{int(skillhps)}**/{int(basehps)}/*{int(avghps)}* + {extraheal}hps to vanguards"
		return self.name

class Ptilopsis(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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

class Silence(Healer):
	def __init__(self, lvl = 0, pot=-1, skill=-1, mastery = 3, module=-1, module_lvl = 3, buffs=[0,0,0,0], boost = 0):
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
#################################################################################################################################################


healer_dict = {"eyja": Eyjaberry, "eyjafjalla": Eyjaberry, "eyjaberry": Eyjaberry, "lumen": Lumen, "myrtle": Myrtle, "ptilopsis": Ptilopsis, "ptilo": Ptilopsis, "purestream": Purestream, "quercus": Quercus, "silence": Silence}

healers = ["Eyjafjalla","Lumen","Myrtle","Ptilopsis","Purestream","Quercus"]

if __name__ == "__main__":
	for operator in healer_dict.values():
		for skill in [1,2,3]:
			operator(skill= skill).skill_hps()
	print("Seems to be working fine. Make sure the operator is added to the dictionary.")
	
	#Test individual operators:
	#print(Eyjaberry().skill_hps())

#below you will find first attempts at creating a bar diagram using the operator inputs. 
#that does however just look stupid with only 1 operator and the idea ultimately was discarded in favor of just texting the hps
"""import numpy as np
import pylab as pl

class Healing:
	def __init__(self,heal=[0,0,0,0],aura=[0,0,0,0],shield=[0,0,0,0],conditional=[0,0,0,0],selfheal=0):
		self.heal = heal
		self.aura = aura
		self.shield = shield
		self.conditional = conditional
		self.selfheal = selfheal
	
	def totalHeal(self):
		return sum(self.heal)+sum(self.aura)+sum(self.shield)+sum(self.conditional)+self.selfheal
	
	def __lt__(self, other): return self.totalHeal() < other.totalHeal()
	def __le__(self, other): return self.totalHeal() <= other.totalHeal()
	def __eq__(self, other): return self.totalHeal() == other.totalHeal()
	def __ne__(self, other): return self.totalHeal() != other.totalHeal()
	def __gt__(self, other): return self.totalHeal() > other.totalHeal()
	def __ge__(self, other): return self.totalHeal() >= other.totalHeal()

skilldown = Healing(heal=[0,20,0,0])
skillup = Healing(heal=[400,0,0,0])
averaged = Healing(heal=[400*4/9,0,0,0])
PlotTarget = ("Myrtle",skilldown,skillup,averaged)
skillup2 = Healing(heal=[200,100,0,0])
PlotTarget2 = ("suss",skilldown,skillup2,averaged)

ListofPLotTargets = [PlotTarget,PlotTarget,PlotTarget2,PlotTarget2]
ListofPLotTargets.sort(key=lambda tup: tup[2], reverse=True)
operators = len(ListofPLotTargets)
fig, ax = pl.subplots()
width = 0.2
for y,plot in enumerate(ListofPLotTargets):
	if True:
		name,down,up,avg = plot
		bottom = [0,0,0]
		print(up.totalHeal())
		rect = ax.bar(y-width,down.heal[0],width,label="4+",bottom = bottom[0],color = (0.1,0.1,0.9))
		bottom[0] += down.heal[0]
		rect = ax.bar(y,up.heal[0],width,label="4+",bottom = bottom[1],color = (0.1,0.1,0.9))
		bottom[1] += up.heal[0]
		pl.bar_label(rect,padding = 1)
		rect = ax.bar(y+width,avg.heal[0],width,label="4+",bottom = bottom[2],color = (0.1,0.1,0.9))
		bottom[2] += avg.heal[0]
		###
		rect = ax.bar(y-width,down.heal[1],width,label="3",bottom = bottom[0],color = (0.3,0.3,0.9))
		bottom[0] += down.heal[1]
		rect = ax.bar(y,up.heal[1],width,label="3",bottom = bottom[1],color = (0.3,0.3,0.9))
		bottom[1] += up.heal[1]
		rect = ax.bar(y+width,avg.heal[1],width,label="3",bottom = bottom[2],color = (0.3,0.3,0.9))
		bottom[2] += avg.heal[1]
		###
		
		
		
ax.set_xticks(np.arange(operators), [i[0] for i in ListofPLotTargets])		
pl.show()		

    
basehealing = np.array([20,30,40])
aoehealing = np.array([20,30,40])
aurahealing = np.array([20,30,40])

width = 0.2

operators = ("perfumer","paprika","myrtle")

weight_counts = {
	"4+": np.array([400,0,300]),
	"3": np.array([0,200,0]),
	"2": np.array([0,100,0]),
	"1": np.array([0,100,0]),
	"aura4+": np.array([99,0,0]),
	"aura3": np.array([0,0,0]),
	"aura2": np.array([0,0,0]),
	"aura1": np.array([0,0,0]),
	"shield": np.array([400,0,300]),
	"shield": np.array([0,200,0]),
	"shield": np.array([0,100,0]),
	"shield": np.array([0,100,0]),
	"self": np.array([99,0,0]),
}


fig, ax = pl.subplots()
bottom = np.zeros(3)
#for boolean, weight_count in weight_counts.items():
 #   p = ax.bar(operators, weight_count, width, label=boolean, bottom=bottom)
 #   bottom += weight_count

x = np.arange(len(operators))
multiplier = 0
for attribute, measurement in weight_counts.items():
    offset = width# * multiplier #this does the sideways difference
    rects = ax.bar(x + offset, measurement, width, label=attribute,bottom= bottom)
    bottom += measurement  #this does the height difference(together with this^ )
    ax.bar_label(rects, padding=0)
    multiplier += 1

ax.set_xticks(x + width, operators)
ax.legend(loc='upper right', ncols=2)

#ax.set_title("Number of penguins with above average body mass")
#ax.legend(loc="upper right")

pl.show()

#name aura 1->4+ normal 1->4+ self conditional shield/ele 1->4+
# 1       4*3         4*3       3      4*3        4*3
"""
