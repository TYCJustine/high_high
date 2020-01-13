import pygame
from pygame.locals import *
import sys, random, math
#===================================================================================
#設定參數
class sets():
	def __init__(self):
		self.screensize = [450,690]
		self.caption = "好高好高！"
		self.FPS = 60
		self.difficulity = -0.01
#房子類別
class House(object):
	def __init__(self,screen,x,y,points):
		self.rawpic = pygame.image.load(House_pics[random.randrange(19)])
		self.rect = self.rawpic.get_rect()
		self.pic = self.rawpic
		self.screen = screen
		self.left = x
		self.top = y
		self.width = self.rect[2]
		self.height = self.rect[3]

		self.swinging = True
		self.falling = False
		self.staying = False

		self.speed_x = 10*(2-1.5*math.exp(sets.difficulity*points))
		self.speed_y = 0

	def rotate(self,angle):
		self.pic = pygame.transform.rotate(self.rawpic,angle)
		self.rect = self.pic.get_rect()
	def update(self):
		if self.swinging:
			if self.left + self.width > sets.screensize[0]-25 or self.left < 25:
				self.speed_x = -self.speed_x
			self.top = (100-(0.04*(self.left + self.width/2-225))**2)
			self.rotate((self.left-150)/25)
			self.rope((170,0),(self.left+20,self.top+10))
			self.rope((280,0),(self.left-20 + self.width,self.top+10))
		elif self.falling:
			self.speed_x, self.speed_y = 0,5
			self.rotate(0)
		elif self.staying:
			self.speed_x, self.speed_y = 0,0

		self.left += self.speed_x
		self.top += self.speed_y

		self.screen.blit(self.pic,(self.left,self.top))
	def rope(self, start, end):
		pygame.draw.line(self.screen, (0,0,0), start, end, 5)
#===================================================================================
#紀錄讀取
def load_record(filepath):
	ranks = []
	try:
		with open(filepath, 'r') as record:
			for info in record:
				ranks.append(info.strip().split(':'))
	except IOError as ioerr:
		print("檔案 %s 不存在" % (filepath))
	return ranks
#紀錄儲存
def save_record(ranks, filepath):
	try:
		with open(filepath, 'w') as record:
			for [key,value] in ranks:
				record.write('%s:%s\n' % (key, value))
	except IOError as ioerr:
		print("檔案 %s 無法建立" % (filepath))
#-----------------------------------------------------------------------------------
#常規檢查
def CheckEvent():
	global runnung, waiting, gaming, ranking, showing, house_list, named, name, Names_On_Rank, ranks, debug
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
			pygame.quit()
		if event.type == pygame.KEYDOWN:
			if event.key == K_d:
				if gaming and not named:
					pass
				else:
					if debug: debug = False
					else: debug = True
			if waiting:
				if debug:print('[debug][from waiting] pressing #' + pygame.key.name(event.key))
				if event.key == K_RETURN:#Enter開始遊戲
					waiting, gaming = False, True

			elif gaming:
				if debug:print('[debug][from gaming] pressing #' + pygame.key.name(event.key))
				if not named:#命名
					if len(name) <= 13:
						if len(pygame.key.name(event.key)) == 1:
							name += pygame.key.name(event.key)
						elif event.key == K_SPACE:
							name += ' '
					if event.key == K_BACKSPACE:
						name = ''.join(list(name)[0:-1])
					elif event.key == K_RETURN:
						if name not in Names_On_Rank:
							ranks.append([name,0])
						named = True
				elif event.key == K_SPACE and named and not First_time:#Space房子落下
					house_list[-1].swinging = False
					house_list[-1].falling = True
					house_list[-1].top = (house_list[-1].top//5)*5


			elif ranking:
				if debug:print('[debug][from ranking] pressing #' + pygame.key.name(event.key))
				if event.key == K_BACKSPACE:#Backspace離開排名
					ranking, waiting = False, True

			elif showing:#任意鍵回到初始頁面
				if debug:print('[debug][from showing] pressing #' + pygame.key.name(event.key))
				showing, waiting = False, True
			elif event.key == K_UP:
				pygame.mixer.music.pause()


		if event.type == pygame.MOUSEBUTTONUP:
			if waiting:#點擊進入排名
				if event.pos[0] < RankRect[2]+5 and event.pos[1] < RankRect[3]+10:
					waiting, ranking = False, True

			elif ranking:#點擊退出排名
				if event.pos[0] < ReturnRect[2] and event.pos[1] < ReturnRect[3]:
					ranking, waiting = False, True
#倒塌檢查
def collapse_detect(house_list, Cg, floor = 0):
	if floor == len(house_list):
		print(f'[info] Center at : {Cg}')
		return False
	else:
		left = house_list[-1-floor].left
		right = left + house_list[-1-floor].width
		if Cg < left or Cg > right:
			print('[info] haha! You lose.')
			return True
		else:
			Cg = (Cg*floor + (left+right)/2)//(floor + 1)
			floor += 1
			return collapse_detect(house_list, Cg, floor)
#-----------------------------------------------------------------------------------
#每幀渲染
def Render(color):
	pygame.display.update()
	clock.tick(sets.FPS)
	screen.fill(color)
	CheckEvent()
#===================================================================================
#初始化
pygame.init()
#-----------------------------------------------------------------------------------
#預宣告
runnung, waiting = True, True
ranking, gaming, showing, named, debug = False, False, False, False, False
sets = sets()
clock = pygame.time.Clock()
name = ''
points = 0
font = pygame.font.Font('elements/Champagne_Limousines.ttf', 30)

ranks = load_record('elements/ranks.txt')
Names_On_Rank = [record[0] for record in ranks]

screen = pygame.display.set_mode(sets.screensize)
pygame.display.set_caption(sets.caption)

House_pics = [f'elements/pictures/house{i}.png'for i in range(1,20)]
Lose_face = pygame.image.load("elements/pictures/lose_face.png")
Lose_faceRect = Lose_face.get_rect()
RankPic = pygame.image.load("elements/pictures/rank.png")
RankRect = RankPic.get_rect()
ReturnPic = pygame.image.load("elements/pictures/return.png")
ReturnRect = ReturnPic.get_rect()

house_list = []
house_list.append(House(screen,26,50,0))

First_time = True
CurTop = sets.screensize[1]
TapSignColor = [0,0,0]
TapSignShine = 5
#===================================================================================
#主迴圈
pygame.mixer.music.load('elements/Bob-the-Builder-Can-We-Fix-It.mp3')
pygame.mixer.music.play(-1,0)
while runnung:

	while waiting:#初始頁面----------------------------------------------------------
		Render((0,0,0))
		if TapSignColor[0] == 0:TapSignShine = 5
		elif TapSignColor[0] == 255:TapSignShine = -5
		for RGB in range(3):
			TapSignColor[RGB] += TapSignShine
		TapSign = font.render('Tap "Enter" to start !',True,TapSignColor)
		screen.blit(TapSign,[(sets.screensize[0]-TapSign.get_rect()[2])//2,sets.screensize[1]//2+200])
		screen.blit(RankPic,(RankRect[0]+5,RankRect[1]+10))

	while ranking:#排名頁面----------------------------------------------------------
		Render((0,0,0))
		scores = sorted(list(set([int(record[1]) for record in ranks])))[:10][::-1]#列出前十分數
		On_Rank = []#榜單
		screen.blit(ReturnPic,ReturnRect)
		for score in scores:
			for record in ranks:
				if int(record[1]) == score:
					On_Rank.append(record)
		TempRank = 1
		for name, score in On_Rank:
			if name == '':
				name = 'None'
			info = font.render('%s. %-15s %3s'%(TempRank, name, score),True,(255,255,255))
			screen.blit(info,[(sets.screensize[0]-300)//2,50+50*TempRank])
			if TempRank == 10:break
			TempRank += 1
		name = ''

	while gaming:#遊戲頁面-----------------------------------------------------------

		while not named:#命名頁面----------------------------------------------------
			Render((255,255,255))
			TypeName = font.render('Type your name:',True,(0,0,0))
			screen.blit(TypeName,[(sets.screensize[0]-TypeName.get_rect()[2])//2,sets.screensize[1]//2+170])
			Name = font.render(name,True,(0,0,0))
			screen.blit(Name,[(sets.screensize[0]-Name.get_rect()[2])//2,545])
		shine = -1
		shinecolor = [254,254,254]
		while First_time:
			Render((255,255,255))
			Tip = font.render('Press "Space" to release the house !',True,shinecolor)
			if shinecolor[0] == 0:shine = 1
			if shinecolor[0] == 255:
				First_time = False
				break
			for RGB in range(3):
				shinecolor[RGB] += shine
			screen.blit(Tip,[(sets.screensize[0]-Tip.get_rect()[2])//2,sets.screensize[1]//2])


		Render((255,255,255))
		if CurTop < 2*sets.screensize[1]//3:#全體下降
			CurTop += 5
			for house in house_list:
				if house.staying:
					house.top += 5
		elif house_list[-1].top + house_list[-1].height >= CurTop:#落下
			house_list[-1].falling = False
			house_list[-1].staying = True
			if collapse_detect(house_list,house_list[-1].left + house_list[-1].width//2):#倒塌判定
				showing, gaming = True, False
				house_list.pop()
				for record in ranks:
					if record[0] == name and int(record[1]) < points:
						record[1] = points
				save_record(ranks,'elements/ranks.txt')
				#本次排名
				my_rank = 1
				for record in ranks:
					if int(record[1]) > points:
						my_rank += 1
				My_points = font.render(f'Your points : {points}',True,(0,0,0))
				My_rank = font.render(f'Your rank : {my_rank}',True,(0,0,0))
				#準備開刷
				depth = house_list[0].top
				if debug:print(f'[info] depth is : {depth}')
				swipe = house_list[0].height - depth
				for house in house_list:
					house.top -= (depth-390)
				while showing:#結束頁面----------------------------------------------
					Render((255,255,255))
					if swipe <= 0:
						swipe += depth/(80*math.log(points/2+10))
						for house in house_list:
							house.top += depth/(80*math.log(points/2+10))
					pygame.draw.rect(screen,(0,0,0),[0,depth+390+swipe,sets.screensize[0],230])
					for house in house_list:
						house.update()
					if TapSignColor[0] == 0:TapSignShine = 5
					elif TapSignColor[0] == 255:TapSignShine = -5
					for RGB in range(3):
						TapSignColor[RGB] += TapSignShine
					TapSign = font.render('Tap to continue !',True,TapSignColor)
					screen.blit(Lose_face,[(sets.screensize[0]-Lose_faceRect[2])//2,swipe+80])
					screen.blit(My_points,[(sets.screensize[0]-My_points.get_rect()[2])//2,swipe+340])
					screen.blit(My_rank,[(sets.screensize[0]-My_rank.get_rect()[2])//2,swipe+380])
					screen.blit(TapSign,[(sets.screensize[0]-TapSign.get_rect()[2])//2,swipe+545])

				named = False
				name = ''
				points = 0
				house_list = []
				house_list.append(House(screen,26,50,0))
				CurTop = sets.screensize[1]
				break
			points += 1
			CurTop -= house_list[-1].height

			house_list.append(House(screen,30+240*random.random(),50,points))
			print(f'[info] speed : {round(house_list[-1].speed_x,2)}')

			
		Point = font.render(f'Points:{points}',True,(255,0,0))
		screen.blit(Point,(10,0))
		for house in house_list:
			house.update()


pygame.quit()
quit()