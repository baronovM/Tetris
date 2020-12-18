import pygame as pg
import sys
import random

pg.init()	#Инициализация


print('\n'*7)
print("Добро пожаловать в игру 'Тетрис'")
print("Не закрывайте окно командной строки, это приведёт к вылету игры без сохранения данных (можно свернуть, оно автоматически закроется при выходе из игры)")
print("Окно самой игры закрыть можно\n")


#Считывание файла
try:
	f=open('tetris data')
	file_text=f.read().split()
	f.close()
except:
	file_text=['0','0','False','False','False']

try:
	best_score=int(file_text[0])
except:
	best_score=0

try:
	total_score=int(file_text[1])
except:
	total_score=0

try:
	sack_buyed=True if file_text[2]=='True' else False
except:
	sack_buyed=False

try:
	color_back_buyed=True if file_text[3]=='True' else False
except:
	color_back_buyed=False

try:
	next_buyed=True if file_text[4]=='True' else False
except:
	next_buyed=False

try:
	f=open('tetris resolution')
	fread=f.read()
	f.close()
	height=int(fread)
	print("Принято то же разрешение, что и при прошлом запуске; если разрешение неправильное и вы не можете сменить его в настройках игры, удалите файл 'tetris resolution'")
	mem_resol_b=True
except:
	height=int(input('Пожалуйста, введите разрешение (высоту, ширина настроится автоматически и будет в 2 раза меньше) в пикселях (одно число, например - 600): '))
	if 'y'==input("Запомнить его для будущих запусков игры, чтобы не вводить его в следующий раз? (y/n) "):
		mem_resol_b=True
		f=open('tetris resolution','w')
		f.write(str(height))
		f.close()
	else:
		mem_resol_b=False


width=height//2

block_size=width//10
next_size=width//25

sc=pg.display.set_mode((width,height))	#Дисплей
pg.display.set_caption('Tetris')

clock=pg.time.Clock()	#Часы

#Цвета
white=(255,255,255)
black=(0,0,0)
gray=(125,125,125)
light_blue=(64,128,255)
blue=(0,0,255)
red=(255,0,0)
green=(0,255,0)
yellow=(255,255,0)
orange=(255,130,0)


#Цвета блоков
col=[red,blue,green,yellow,white,orange]
block_colors={'O':col.pop(random.randint(0,5)),'I':col.pop(random.randint(0,4)),
				'T':col.pop(random.randint(0,3)),'L':col.pop(random.randint(0,2)),
				'Z':col.pop(random.randint(0,1)),'S':col.pop()}


#Формы блоков
blocks={'O':((-1,-1),(-1,0),(0,-1),(0,0)),'I':((0,-2),(0,-1),(0,0),(0,1)),
		'T':((-1,0),(0,0),(1,0),(0,1)),'L':((0,-2),(0,-1),(0,0),(1,0)),
		'Z':((-1,-1),(0,-1),(0,0),(1,0)),'S':((-1,0),(0,0),(0,-1),(1,-1))}


line_scores={0:0,1:100,2:300,3:700,4:1500}		#Очки за собранные линии


field=[[0 for j in range(25)]+[1] for i in range(10)]	#Поле


#####Обьявление переменных##

next_block=''

v=0.06*block_size
vmod=1
k=0
block_is_falling=False

score=0


menu=True

sack=[]
options=False
sack_trigger=False
sack_size=8
colored_backgr=False
cobg_freeze=False
next_trigger=False
colored_menu=False

bot_trigger=False



####ФУНКЦИИ###########################ФУНКЦИИ####################################################################################################

#Кубик
def drawRe(x,y,c,is_m,is_b):
	if is_m:
		pg.draw.rect(sc,c,(x*block_size,y*block_size+k,block_size,block_size))
		if colored_backgr:
			pg.draw.rect(sc,(0,0,0),(x*block_size,y*block_size+k,block_size,block_size),3)
		else:
			pg.draw.rect(sc,(0,0,0),(x*block_size,y*block_size+k,block_size,block_size),1)
	else:
		if is_b:
			pg.draw.rect(sc,c,(x*block_size,y*block_size,block_size,block_size))
			pg.draw.rect(sc,(10,10,10),(x*block_size,y*block_size,block_size,block_size),1)
		else:
			pg.draw.rect(sc,c,(x*block_size,y*block_size,block_size,block_size))
			if colored_backgr:
				pg.draw.rect(sc,(10,10,10),(x*block_size,y*block_size,block_size,block_size),3)
			else:
				pg.draw.rect(sc,(10,10,10),(x*block_size,y*block_size,block_size,block_size),1)


#Клавиши
def key_left():
	global x_fi,y_fi,cu_block_form
	resol=True
	for i in cu_block_form:
		if field[x_fi+i[0]-1][y_fi+i[1]]!=0 or x_fi+i[0]==0:
			resol=False
	if resol:
		x_fi-=1

def key_right():
	global x_fi,y_fi,cu_block_form
	resol=True
	for i in cu_block_form:
		if not (x_fi+i[0]!=9 and field[x_fi+i[0]+1][y_fi+i[1]]==0):
			resol=False
	if resol:
		x_fi+=1

def rotate():
	global cu_block_form,rotation
	resol=True
	for i in cu_block_form:
		if -i[1]+x_fi>=10:
			resol=False
		elif -i[1]+x_fi<0:
			resol=False
		elif field[-i[1]+x_fi][i[0]+y_fi]!=0:
			resol=False
	if resol:
		for i in range(4):
			cu_block_form[i]=[-cu_block_form[i][1],cu_block_form[i][0]]
		rotation+=1
		rotation%=4

def rotate_left():
	global cu_block_form,rotation
	resol=True
	for i in cu_block_form:
		if i[1]+x_fi>=10:
			resol=False
		elif i[1]+x_fi<0:
			resol=False
		elif field[i[1]+x_fi][-i[0]+y_fi]!=0:
			resol=False
	if resol:
		for i in range(4):
			cu_block_form[i]=[cu_block_form[i][1],-cu_block_form[i][0]]
		rotation=rotation-1 if rotation>0	else 3

def drop():
	global y_fi
	block_is_falling=True
	while block_is_falling:
		for i in cu_block_form:
			if field[x_fi+i[0]][y_fi+i[1]+1]!=0:
				block_is_falling=False
				break
		else:
			y_fi+=1


#Уничтожение ряда
delete_timer=-1
def delete_line():
	global field,delete_timer,score
	line_count=0
	for i in range(5,25):
		block_counter=0
		for j in range(10):
			if field[j][i]!=0:
				block_counter+=1
		if block_counter>=10:
			light=255
			for anim in range(200//(bot_trigger+1)):
				pg.draw.rect(sc,(light,light,light),(0,(i-5)*block_size,width,block_size))
				pg.display.update()
				pg.time.delay(not bot_trigger+1)
				light-=0.5+bot_trigger*0.5
			for j in range(10):
  				colomn=field[j]
  				field[j]=[0]+colomn[:i]+colomn[i+1:]
			line_count+=1
	score+=line_scores[line_count]
	delete_timer=-1

def game_over():
	global score,field,block_is_falling,menu,total_score,best_score,sack,next_block,v,vmod,bot_trigger

	#Сообщение о конце игры
	sc.fill((0,0,0))
	lose_font=pg.font.Font(None,int(0.045*height))
	lose_text_surface=lose_font.render('Игра окончена',1,(250,10,10))
	sc.blit(lose_text_surface,(height*0.12,height*0.35))

	lose_font=pg.font.Font(None,int(0.038*height))
	lose_text_surface=lose_font.render('Твой счёт: '+str(score),1,(10,250,10))
	sc.blit(lose_text_surface,(height*0.14,height*0.45))

	lose_font=pg.font.Font(None,int(0.028*height))
	lose_text_surface=lose_font.render('Нажмите "R" или "Пробел" чтобы начать заново',1,(10,180,10))
	sc.blit(lose_text_surface,(height*0.025,height*0.52))

	lose_text_surface=lose_font.render('Нажмите "Esc" чтобы выйти в меню',1,(10,180,10))
	sc.blit(lose_text_surface,(height*0.095,height*0.54))


	#Запоминание лучшего счёта
	if score>best_score:
		best_score=score

		lose_font=pg.font.Font(None,int(0.038*height))
		lose_text_surface=lose_font.render('Новый рекорд!',1,(255, 215, 0))
		sc.blit(lose_text_surface,(height*0.13,height*0.6))

	pg.display.update()

	total_score+=score
	score=0
	v=0.003*height
	vmod=1
	bot_trigger=False
	block_is_falling=False
	field=[[0 for j in range(25)]+[1] for i in range(10)]
	sack=[]
	next_block=''

	write_data()

	exitlose=False
	while True:
		for e in pg.event.get():
			if e.type==pg.QUIT:
				game_exit()
			elif e.type==pg.KEYDOWN:
				if e.key==pg.K_r or e.key==pg.K_SPACE:
					exitlose=True
					break
				elif e.key==pg.K_ESCAPE:
					exitlose=True
					menu=True
					break
		if exitlose:
			break
		clock.tick(20)

def write_data():
	global best_score, total_score
	best_score=max(best_score,score)
	total_score+=score

	f=open('tetris data','w')
	f.write(str(best_score))
	f.write(' '+str(total_score))
	f.write(' '+str(sack_buyed))
	f.write(' '+str(color_back_buyed))
	f.write(' '+str(next_buyed))
	f.close()

def game_exit():
	write_data()
	sys.exit()



while True:
	if menu:

#######Меню###########################################Меню############################Меню#######################################################

		if colored_menu:
			tick_time=pg.time.get_ticks()
			sc.fill(((tick_time*0.02)%150,(tick_time*0.03)%150,(tick_time*0.01)%150))
		else:
			sc.fill((10,0,30))
		for e in pg.event.get():
			if e.type==pg.QUIT:
				game_exit()
			elif e.type==pg.MOUSEBUTTONDOWN:
				if e.button==1:
					if e.pos[0]>=0.18*height and e.pos[0]<=0.32*height and e.pos[1]>=0.22*height and e.pos[1]<=0.28*height:
						menu=False
						write_data()
					elif e.pos[0]>=0.18*height and e.pos[0]<=0.32*height and e.pos[1]>=0.32*height and e.pos[1]<=0.38*height:
						options=not options
			elif e.type==pg.KEYDOWN:
				if e.key==pg.K_q:
					game_exit()
				if options:
					if e.key==pg.K_1:
						if not sack_buyed:
							if total_score>=5000:
								total_score-=5000
								sack_buyed=True
						else:
							sack_trigger=not sack_trigger
					if e.key==pg.K_w:
						if sack_trigger:
							sack_size=sack_size+1 if sack_size<15 else 4
					if e.key==pg.K_2:
						if not color_back_buyed:
							if total_score>=1000:
								total_score-=1000
								color_back_buyed=True
						else:
							colored_backgr=not colored_backgr
					if e.key==pg.K_3:
						if not next_buyed:
							if total_score>=8000:
								total_score-=8000
								next_buyed=True
						else:
							next_trigger=not next_trigger
					if e.key==pg.K_4:
						colored_menu=not colored_menu
					if e.key==pg.K_5:
						f=open('tetris resolution','w')
						mem_resol_b=not mem_resol_b
						if mem_resol_b:
							f.write(str(height))
						f.close()


		menu_score_font=pg.font.Font(None,int(0.028*height))
		menu_score_surf=menu_score_font.render('Общий счёт: '+str(total_score),1,(100,250,100))
		sc.blit(menu_score_surf,(0.3*height,0.02*height))

		if options:
			menu_opt_font=pg.font.Font(None,int(0.028*height))
			if sack_trigger:
				menu_opt_surf=menu_opt_font.render('1 - выкл режим "мешка"',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.42*height))

				menu_opt_font=pg.font.Font(None,int(0.022*height))
				menu_opt_surf=menu_opt_font.render('w - изменить кол-во фигур каждого вида в "мешке", сейчас '+str(sack_size),1,(200,200,100))
				sc.blit(menu_opt_surf,(0.02*height,0.44*height))
			else:
				menu_opt_surf=menu_opt_font.render('1 - вкл режим "мешка"',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.42*height))
				if not sack_buyed:
					menu_opt_font=pg.font.Font(None,int(0.02*height))
					menu_opt_surf=menu_opt_font.render('Покупка стоит 5000 очков общего счёта',1,(200,200,100))
					sc.blit(menu_opt_surf,(0.05*height,0.44*height))

			menu_opt_font=pg.font.Font(None,int(0.028*height))
			if colored_backgr:
				menu_opt_surf=menu_opt_font.render('2 - выкл режим цветного фона',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.46*height))
			else:
				menu_opt_surf=menu_opt_font.render('2 - вкл режим цветного фона',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.46*height))
				if not color_back_buyed:
					menu_opt_font=pg.font.Font(None,int(0.02*height))
					menu_opt_surf=menu_opt_font.render('Покупка стоит 1000 очков общего счёта',1,(200,200,100))
					sc.blit(menu_opt_surf,(0.05*height,0.48*height))

			menu_opt_font=pg.font.Font(None,int(0.028*height))
			if next_trigger:
				menu_opt_surf=menu_opt_font.render('3 - не показывать следующею фигуру',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.5*height))
			else:
				menu_opt_surf=menu_opt_font.render('3 - показывать следующею фигуру',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.5*height))
				if not next_buyed:
					menu_opt_font=pg.font.Font(None,int(0.02*height))
					menu_opt_surf=menu_opt_font.render('Покупка стоит 8000 очков общего счёта',1,(200,200,100))
					sc.blit(menu_opt_surf,(0.05*height,0.52*height))

			menu_opt_font=pg.font.Font(None,int(0.028*height))
			if colored_menu:
				menu_opt_surf=menu_opt_font.render('4 - выкл цветное меню',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.54*height))
			else:
				menu_opt_surf=menu_opt_font.render('4 - вкл цветное меню',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.54*height))

			menu_opt_font=pg.font.Font(None,int(0.028*height))
			if mem_resol_b:
				menu_opt_surf=menu_opt_font.render('5 - сменить разрешение',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.62*height))

			else:
				menu_opt_surf=menu_opt_font.render('5 - сохранить разрешение',1,(200,200,100))
				sc.blit(menu_opt_surf,(0.05*height,0.62*height))

				menu_opt_font=pg.font.Font(None,int(0.025*height))
				menu_opt_surf=menu_opt_font.render('При следующем запуске вы сможете',1,(255,100,100))
				sc.blit(menu_opt_surf,(0.05*height,0.58*height))
				menu_opt_surf=menu_opt_font.render('выбрать разрешение',1,(255,100,100))
				sc.blit(menu_opt_surf,(0.05*height,0.6*height))


		pg.draw.rect(sc,(20,20,250),(width*0.36,height*0.22,width*0.28,height*0.06))
		pg.draw.rect(sc,(0,0,0),(width*0.36,height*0.22,width*0.28,height*0.06),2)

		menu_start_font=pg.font.Font(None,int(height*0.04))
		menu_start_surf=menu_start_font.render('Играть',1,(10,200,10))
		sc.blit(menu_start_surf,(height*0.2,0.235*height))

		pg.draw.rect(sc,(20,250,20),(width*0.36,height*0.32,width*0.28,height*0.06))
		pg.draw.rect(sc,(0,0,0),(width*0.36,height*0.32,width*0.28,height*0.06),2)

		menu_opt_font=pg.font.Font(None,int(0.034*height))
		menu_opt_surf=menu_opt_font.render('Настройки',1,(20,20,10))
		sc.blit(menu_opt_surf,(0.19*height,0.335*height))


		menu_ctrl_font=pg.font.Font(None,int(0.035*height))
		menu_ctrl_surf=menu_ctrl_font.render('Управление:',1,(255, 215, 0))
		sc.blit(menu_ctrl_surf,(0.19*height,0.71*height))

		menu_ctrl_font=pg.font.Font(None,int(0.028*height))
		if colored_backgr:
			menu_ctrl_surf=menu_ctrl_font.render('"F" - "заморозить" фон',1,(100, 200, 10))
			sc.blit(menu_ctrl_surf,(0.035*height,0.75*height))

		menu_ctrl_surf=menu_ctrl_font.render('"Q" - выйти из игры',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.78*height))

		menu_ctrl_surf=menu_ctrl_font.render('Стрелки влево, вправо, вниз - двигать фигуру',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.81*height))

		menu_ctrl_surf=menu_ctrl_font.render('Вверх, "X" или пробел - крутить по часовой',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.84*height))

		menu_ctrl_surf=menu_ctrl_font.render('"Z" - крутить фигуру против часовой',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.87*height))

		menu_ctrl_surf=menu_ctrl_font.render('"R" - закончить игру или начать заново',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.9*height))

		menu_ctrl_surf=menu_ctrl_font.render('"Esc" - приостановить игру',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.93*height))

		menu_ctrl_surf=menu_ctrl_font.render('"B" - включить/выключить бота',1,(100,200,10))
		sc.blit(menu_ctrl_surf,(0.035*height,0.96*height))

	else:

########Тетрис#########################################Тетрис############################Тетрис############################################################

		#Обработка событий
		stopped=0
		for e in pg.event.get():
			if e.type==pg.QUIT:
				game_exit()
			elif e.type==pg.KEYDOWN:
				if e.key==pg.K_q:
					game_exit()
				elif e.key==pg.K_ESCAPE:
					stopped=True
				elif e.key==pg.K_b:
					if bot_trigger:
						bot_trigger=False
						vmod=max(1,vmod//8)
					else:
						bot_trigger=True
						vmod*=8
				elif e.key==pg.K_LEFT:
					key_left()
				elif e.key==pg.K_RIGHT:
					key_right()
				elif e.key==pg.K_x or e.key==pg.K_UP:
					rotate()
				elif e.key==pg.K_z:
					rotate_left()
				elif e.key==pg.K_DOWN:
					vmod*=4
				elif e.key==pg.K_r:
					game_over()
				elif e.key==pg.K_f:
					cobg_freeze=not cobg_freeze
				elif e.key==pg.K_SPACE:
					drop()
			elif e.type==pg.KEYUP:
				#Клавиша вниз отжата
				if e.key==pg.K_DOWN:
					vmod=max(1,vmod//4)
	
		#Создание фигуры
		if not block_is_falling:
			if sack_trigger:
				if next_block:
					if not sack:
						for i in blocks.keys():
							sack.extend([i]*sack_size)
						random.shuffle(sack)
					cu_block=next_block
					next_block=sack.pop()
				else:
					for i in blocks.keys():
						sack.extend([i]*sack_size)
					random.shuffle(sack)
					cu_block=sack.pop()
					next_block=sack.pop()

			else:
				if next_block:
					cu_block=next_block
					next_block=random.choice(list(blocks.keys()))
				else:
					cu_block=random.choice(list(blocks.keys()))
					next_block=random.choice(list(blocks.keys()))

			cu_block_form=list(blocks[cu_block])
			next_block_form=list(blocks[next_block])
			block_is_falling=True
			x_fi,y_fi=4,4
			rotation=0
			loc=-1,-1
	
		#Зарисовка поля
		sc.fill((30,20,100))
		for i in range(10):
			for j in range(5,25):
				f=field[i][j]
				if f!=0:
					drawRe(i,j-5,f,False,False)
				else:
					if colored_backgr:
						if cobg_freeze:
							if freeze_time:
								drawRe(i,j-5,((j*4+freeze_time*0.01)%100,(i*2-freeze_time*0.01)%100,(i*3+j*2+freeze_time*0.01)%100),False,True)
							else:
								tick_time=pg.time.get_ticks()
								freeze_time=tick_time
								drawRe(i,j-5,((j*4+freeze_time*0.01)%100,(i*2-freeze_time*0.01)%100,(i*3+j*2+freeze_time*0.01)%100),False,True)
						else:
							tick_time=pg.time.get_ticks()
							drawRe(i,j-5,((j*4+tick_time*0.01)%100,(i*2-tick_time*0.01)%100,(i*3+j*2+tick_time*0.01)%100),False,True)
							freeze_time=0
					else:
						drawRe(i,j-5,(30,10,60),False,True)


		#Изображение фигуры
		for i in cu_block_form:
			drawRe(x_fi+i[0],y_fi-5+i[1],block_colors[cu_block],True,False)

		#Вывод следующей фигуры
		if next_trigger:
			next_surf=pg.Surface((5*next_size,5*next_size))
			next_surf.fill((50,50,50))
			for i in next_block_form:
				pg.draw.rect(next_surf,(block_colors[next_block]),(2.5*next_size+i[0]*next_size,2.5*next_size+i[1]*next_size,next_size,next_size))
				pg.draw.rect(next_surf,(10,10,10),(2.5*next_size+i[0]*next_size,2.5*next_size+i[1]*next_size,next_size,next_size),1)
			next_surf.set_alpha(200)
			sc.blit(next_surf,(0,0))

		#Вывод счёта
		score_font=pg.font.Font(None,int(0.028*height))
		score_text_surf=score_font.render('Счёт: '+str(score),1,(100,250,100))
		score_text_surf.set_alpha(100)
		sc.blit(score_text_surf,(0.38*height,0.05*height))
	
		score_font=pg.font.Font(None,int(0.027*height))
		score_text_surf=score_font.render('Лучший счёт: '+str(best_score),1,(255, 215, 0))
		score_text_surf.set_alpha(100)
		sc.blit(score_text_surf,(0.31*height,0.015*height))

		if delete_timer==0:
			delete_line()
		elif delete_timer>0:
			delete_timer-=1

		#Остановка фигуры
		for i in cu_block_form:
			if field[x_fi+i[0]][y_fi+i[1]+1]!=0:
				block_is_falling=False
				break
		if not block_is_falling:
			for i in cu_block_form:
				field[x_fi+i[0]][y_fi+i[1]]=block_colors[cu_block]
			delete_timer=2
			v+=0.0005*block_size
			score+=5
			if y_fi<=5:
				game_over()

		#Опускание фигуры
		k+=v*vmod
		if k>=block_size:
			y_fi+=1
			k=0

#######BOT############BOT###################################BOT############################################################################################


		if bot_trigger:
			if loc!=(rotation,x_fi):
				#Коэфиценты
				KELL=60
				KH=(0.5,6)
				#Массив приоритетов
				pr=[[0 for j in range(10)] for i in range(4)]
				for rot in range(4):
					#Вращение при необходимости
					for i in range(rot):
						rotate()
					for col in range(10):
						for j in range(2,27):
							falled=False	#Упал ли
							over_bo=False	#Вышел ли за границы

							for i in cu_block_form:
								x_pos=col+i[0]
								#Проверка
								if x_pos<10 and x_pos>=0:
									#Упал ли
									if field[x_pos][j+i[1]+1]!=0:
										falled=True
										break
								#Выход за границы
								else:
									over_bo=True
									break
							if falled:
								for i in cu_block_form:
									field[col+i[0]][j+i[1]]=block_colors[cu_block]
								break
							elif over_bo:
								break

						if over_bo:
							pr[rot][col]=-float('inf')
							continue

						#Линии
						block_counter=0
						line_count=0
						for i in range(10):
							if field[i][j]!=0:
								block_counter+=1
						if block_counter>=10:
							line_count+=1
						line_pr=line_scores[line_count]
						pr[rot][col]=line_pr

						#Высота высочайшей точки фигуры
						highest=min(cu_block_form,key=lambda x: x[1])[1]
						pr[rot][col]+=j*KH[0]+(j+highest)*KH[1]
						pr[rot][col]-=100000 if j<=5 else 0
						if j<=10:	KELL//=2

						#Кол-во пустых клеток под фигурой
						blocks_xes=set()
						k_emp_cells_down=0
						for i in cu_block_form:
							if i[0] not in blocks_xes:
								emp_downer=1
								while field[i[0]+col][j+emp_downer+i[1]]==0:
									k_emp_cells_down+=1
									emp_downer+=1
								if k_emp_cells_down!=0:
									blocks_xes.add(i[0])
						pr[rot][col]-=k_emp_cells_down*KELL
						#Удаление фигуры
						for i in cu_block_form:
							field[col+i[0]][j+i[1]]=0
					#Обратный поворот
					for i in range(4-rot):
						rotate()

				#Поиск наилучшей ячейки
				mx=-float('inf')
				for i in range(4):
					for j in range(10):
						if mx<=pr[i][j]:
							loc=i,j
							mx=pr[i][j]
				#Движение к наилучшей ячейке
				for i in range(loc[0]):
					rotate()
				for i in range(loc[1]-x_fi):
					key_right()
				for i in range(x_fi-loc[1]):
					key_left()


#######Пауза##############################################################Пауза##################################################################
		darked=False
		while stopped:
			for e in pg.event.get():
				if e.type==pg.QUIT:
					game_exit()
				elif e.type==pg.KEYDOWN:
					stopped=False
			if not darked:
				pause_surf=pg.Surface((width,height))

				pause_font=pg.font.Font(None,int(0.05*height))
				pause_text_surf=pause_font.render('Игра',1,(255,255,255))
				pause_surf.blit(pause_text_surf,(0.2*height,0.4*height))

				pause_text_surf=pause_font.render('приостановлена',1,(255,255,255))
				pause_surf.blit(pause_text_surf,(0.1*height,0.45*height))

				pause_font=pg.font.Font(None,int(0.025*height))
				pause_text_surf=pause_font.render('нажмите любую клавишу чтобы продолжить',1,(255,255,255))
				pause_surf.blit(pause_text_surf,(0.06*height,0.5*height))

				pause_surf.set_alpha(150)
				sc.blit(pause_surf,(0,0))
				darked=True
				pg.display.update()
			clock.tick(20)

	pg.display.update()
	if menu:
		clock.tick(20)
	elif bot_trigger:
		clock.tick(80)
	else:
		clock.tick(60)