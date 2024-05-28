import gym
from gym import spaces
import numpy as np
import pygame
import math
import random
import sys

class PlaneGameEnv(gym.Env):
    metadata = {'render_modes': ['human'], "render_fps": 30}

    def __init__(self):
        super().__init__()

        self.action_space = spaces.Discrete(3)  # 0: left, 1: straight, 2: right
        self.observation_space = spaces.Box(low=-1, high=1, shape=(21,) , dtype=np.float64)


        # Visualisierungs-Einstellungen
        self.screenSize = (750, 500)
        self.visualisationIsActive = False


        self.gameOver = False
        # REWARDS:
        self.iceBergCollisionReward = -20
        self.getCoinReward = 0.05

        # Visualisierungs-Einstellungen

        # Beschreibt die erste Position des Flugzeugs nach Ausführung des Spiels.
        self.planeX = 275
        self.planeY = 350

        # Definiert die Anzahl der Pixel, um die sich das Flugzeug pro Frame nach rechts oder links bewegt. (bei bestimmter Action)
        self.planeSchritt = 6

        # Beschreibt die X-Punkte, ab denen das Flugzeug nicht mehr nach rechts bzw. nach links kann.
        self.cornerLeft =  -22
        self.cornerRight = 622

        # Beschreibt um wieviele Pixel das Flugzeug pro Frame vorankommt. (kann auch eine Dezimalzahl sein).
        self.gameSpeed = 8

        # Dies ist keine vom User veränderbare Einstellung. (Mithilfe dieser Variable können auch Dezimalzahlen in der Variable "gameSpeed" benutzt werden).
        self.gameSpeedAkkumulator = 0

        self.score = 0

        # Nur um anzuzeigen was der letzte Reward war.
        self.lastReward = None
        self.lastAction = [0,1,0]

        # Beinhaltet die Koordinaten von den Gletschern und Sternen.
        self.stars = []
        self.icebergs = []

        # Unwichtiger Reward, falls Flugzeug auf eine Kante stößt.
        self.rewardKante = -0.05

        # Beschreibt nach welchem Pixel-Interval (in Y-Achse) (der random zwischen (a,b) ist) die Gletscher/Sterne gespawnt werden sollen.
        self.starsSpawnInterval = (300,450)
        self.starsPixelCounter = 0
        # Erster Stern wird zugefügt
        self.stars.append([random.randint(0,675), -1 * random.randint(50, 150)])

        self.icebergSpawnInterval = (300,450)
        self.icebergPixelCounter = 0
        self.icebergs.append([random.randint(0,675), -1 * random.randint(50, 150)])

        # Keine Einstellung - beschreibt nur die Y-Koordinate des Hintergrunds. (immer zwischen 0 und 60) (für die Illusion des vorankommenden Flugzeugs ).
        self.backgroundShift = 0

        # region ALLE HITBOXEN:
        # region FLUGZEUG

        # "Dots" beschreiben immer einen Vektor des Punktes vom Bild (bzw. linke obere Ecke des Bildes).
        # Width und Height beschreiben dabei immer die Hitbox von diesem Punkt aus.
        self.planeDotB = (17, 40)
        self.planeBWidth = 113
        self.planeBHeight = 25

        self.planeBHitbox = [self.planeDotB, self.planeBWidth, self.planeBHeight]
        self.planeDotC = (58, 17)
        self.planeDotCWidth = 34
        self.planeDotCHeight = 95

        self.planeCHitbox = [self.planeDotC, self.planeDotCWidth, self.planeDotCHeight]

        self.planeHitboxes = [self.planeBHitbox, self.planeCHitbox ]
        #endregion

        # region COINS:
        self.coinB =(23,27)
        self.coinBWidth = 40
        self.coinBHeight = 36
        self.coinBHitbox = [self.coinB , self.coinBWidth, self.coinBHeight]
        self.coinHitboxes = [self.coinBHitbox]

        #endregion

        # region EISBERG
        # Beschreibt die "lange" Hitbox
        self.iceBergB = (22,58)
        self.iceBergBWidth =142
        self.iceBergBHeight = 42
        self.icebergBHitbox = [self.iceBergB,self.iceBergBWidth,self.iceBergBHeight]
        # beschreibt die "hohe" Hitbox
        self.iceBergC = (90, 38)
        self.iceBergCWidth = 21
        self.iceBergCHeight = 20
        self.icebergCHitbox = [self.iceBergC, self.iceBergCWidth, self.iceBergCHeight]

        self.icebergHitboxes = [self.icebergBHitbox, self.icebergCHitbox]

        #endregion

        #endregion

    # Muss zu Beginn einer Visualisierung ausgeführt werden, um diese zu ermöglichen.
    def startRendering(self):
      self.visualisationIsActive = True
      self.canvas = pygame.display.set_mode((750, 500))
      pygame.display.set_caption("Hydravion")


      pygame.font.init()
      self.my_font = pygame.font.SysFont("Comis Sans MS",30)

      #region Visualisation Variablen (Nur wenn man es nebenbei visualisiert bekommen will):

      #Verschiebung von Hintergrund.
      self.backgroundShift = 0

      # Anzeigen der Bilder der Spielelemente.
      self.planeImage = pygame.transform.scale(pygame.image.load("img/avion/straight/1.png"), (152,126))
      self.icebergImage = pygame.transform.scale(pygame.image.load("img/iceberg/0.png"), (175,100))
      self.starImage = pygame.transform.scale(pygame.image.load("img/star/star 0.png"), (85,85))
      self.waterblockImage = pygame.transform.scale(pygame.image.load("img/water_Animation/1.jpg"), (60,60))
      #endregion

    # Stellt mithilfe von Pygame einen aktuellen Spielstand bzw. Frame graphisch dar.
    def render(self):
      if(not self.visualisationIsActive):
        print("ERROR: Visualisationsstartsfunktion wurde nicht aufgerufen!")

      # Hintergrund wird aktualisiert.
      for x in range(0,13):
        for y in range(0,11):
          self.canvas.blit(self.waterblockImage, (x*60-20, y*60 - 60 + self.backgroundShift))

      # Flugzeugbild aktualisieren.
      self.canvas.blit(self.planeImage, (self.planeX, self.planeY))

      # Spielelemente (Gletscher und Münzen/Sterne) aktualisieren.
      for star in self.stars:
        self.canvas.blit(self.starImage, (star[0], star[1]))
      for iceberg in self.icebergs:
        self.canvas.blit(self.icebergImage, (iceberg[0], iceberg[1]))

      # Score anzeigen:
      self.canvas.blit(self.my_font.render("Score: " + str(self.score), False, (0,0,0)), (0,0))

      # State anzeigen.
      otherFont = pygame.font.SysFont("Comis Sans MS",20)
      self.canvas.blit(otherFont.render("State " + str([round(i, 1) for i  in self.getState()] ), False, (0,0,0)), (0,475))

      # Rewards anzeigen.
      rewardFont = pygame.font.SysFont("Comis Sans MS",20)
      self.canvas.blit(rewardFont.render("Last Reward other than zero: " + str(self.lastReward), False, (0,0,0)), (515,475))

      # Aktuelle Action anzeigen.
      rewardFont = pygame.font.SysFont("Comis Sans MS",20)
      self.canvas.blit(rewardFont.render("Current action: " + str(self.lastAction), False, (0,0,0)), (600,0))

      # Daten mithilfe von Pygame graphisch aktualisieren.
      pygame.display.update()

    # Überprüft eine Kollision zwischen 2 Spielelementen (Entities) mithilfe ihrer Hitboxen (hitboxes1 bzw. 2).
    # "hitboxes" ist ein Array mit mehreren Hitboxen. Eine Entity ist: [Koordinaten] und Hitbox [dot, width, height].
    def checkForCollision(self,entity1, hitboxes1, entity2, hitboxes2):
        for hitbox1 in hitboxes1:
          for hitbox2 in hitboxes2:
              w1, h1 =  (hitbox1[1], hitbox1[2])
              w2, h2 = (hitbox2[1], hitbox2[2])
              x1, y1 = entity1[0] + hitbox1[0][0] ,entity1[1] + hitbox1[0][1]
              x2, y2 = entity2[0] + hitbox2[0][0] ,entity2[1] + hitbox2[0][1]
              if (x1 + w1 > x2 and x1 < x2 + w2 and y1 + h1 > y2 and y1 < y2 + h2):
                  return True
        return False

    # "action=0" für Links.
    # "action=1" für Geradeaus.
    # "action=2" für nach Rechts.
    # Wird für jede "Frame"-Ausrechnung aufgerufen.
    # -> Aufrufen dieser Funktion steht so für Framewechsel.
    def step(self,action):
      l = [0,0,0]
      l[action] = 1
      self.lastAction = l.copy()
      rewardToReturn = 0
      if(action == 0):
        if(self.planeX > self.cornerLeft):
          self.planeX -= self.planeSchritt
        else:
          rewardToReturn = self.rewardKante
      if(action == 2):
          if(self.planeX < self.cornerRight):
            self.planeX += self.planeSchritt
          else:
            rewardToReturn = self.rewardKante

      # Muss durchgeführt werden, da beispielsweise gameSpeedAkkumulator 0,4 und gameSpeed 0,6 sein könnte
      # - so würde dies dazu führen, dass das Flugzeug um 1 Pixel nach vorne bewegt wird.
      self.gameSpeedAkkumulator += self.gameSpeed

      # "Verschiebung" beschreibt, wie viele Pixel das Flugzeug in diesem Step nach vorne bewegt werden soll.
      # So wird die größte natürliche Zahl dieser Zahl entnommen, und anschließend diese Zahl von gameSpeedAkkumulator abgezogen (mithilfe von Modulo 1).
      self.verschiebung = math.floor(self.gameSpeedAkkumulator)
      # Aktualisieren von dem gameSpeedAkkumulator
      self.gameSpeedAkkumulator = self.gameSpeedAkkumulator % 1

      # Im Falle, dass der neue Frame diese Steps visualisert werden soll
      if(self.visualisationIsActive):
        if(self.backgroundShift>58):
          self.backgroundShift = 0
        else:
          self.backgroundShift += self.verschiebung

      # Verschieben von allen Entitys (bzw. Spielelemente) um "Verschiebung" nach unten durchzuführen
      for i in range(len(self.stars)):
        self.stars[i][1]+=self.verschiebung
      for i in range(len(self.icebergs)):
        self.icebergs[i][1]+=self.verschiebung

      # Überprüfen, ob erste Entity in Array schon weg ist, (wenn ja, dann entfernen)
      if(len(self.stars) != 0):
        if(self.stars[0][1] > 500):
          self.stars.pop(0)
      if(len(self.icebergs) != 0):
        if(self.icebergs[0][1] > 500):
          self.icebergs.pop(0)

      # Wenn die letzte Entity in den Spielelement-Arrays fast das Sichtfeld betreten hat ODER das Array der Entities leer ist,
      # dann wird die nächste Entity erstellt
      if(len(self.stars) == 0 or self.stars[-1][1] > -60):
        self.stars.append([random.randint(0,675), -60-random.randint(self.starsSpawnInterval[0],self.starsSpawnInterval[1])])
      if(len(self.icebergs) == 0 or self.icebergs[-1][1] > -60):
        self.icebergs.append([random.randint(0,675), -60-random.randint(self.icebergSpawnInterval[0],self.icebergSpawnInterval[1])])

      #region Münzen dürfen nicht in Gletscher auftreten.
      toDelCoin = []
      toDelIceBerg = []

      changedCoinHitboxes = [[(10,10) ,50, 46]]
      for iceberg in self.icebergs:
        for coin in self.stars:
          if(self.checkForCollision(iceberg, self.icebergHitboxes, coin, changedCoinHitboxes)):
            toDelCoin.append(coin)
            toDelIceBerg.append(iceberg)

      for coin in toDelCoin:
        try:
          self.stars.pop(self.stars.index(coin))
        except:
          print("Fehler beim Löschen von Coins")

      for iceberg in toDelIceBerg:
        try:
          self.icebergs.pop(self.icebergs.index(iceberg))
        except:
          print("Fehler beim Löschen von Gletscher")
      #endregion

      # Überprüfen, ob eine Kollision zwischen Flugzeug und Münze stattfindet.
      starsToDelete = []
      for star in self.stars:
        if(self.checkForCollision(star, self.coinHitboxes, [self.planeX, self.planeY], self.planeHitboxes )):
          starsToDelete.append(star)
          self.score += 1
          rewardToReturn = self.getCoinReward

      for star in starsToDelete:
        self.stars.pop(self.stars.index(star))

      # Überprüfen, ob eine Kollision zwischen Flugzeug und Gletscher oder Münze stattfindet. (dann GameOver).
      for iceberg in self.icebergs:
        if(self.checkForCollision(iceberg, self.icebergHitboxes, [self.planeX, self.planeY], self.planeHitboxes )):
          self.gameOver = True
          rewardToReturn = self.iceBergCollisionReward

      # Nur für die Visualisierung von dem LastReward nötig. (Label-Visualisierung Pygame).
      if(rewardToReturn != 0):
        self.lastReward =rewardToReturn


      return np.array(self.getState()), rewardToReturn, self.gameOver, {}

    # Zurücksetzen von Spielfeld.
    def reset(self):
      lastReward = self.lastReward
      if(self.visualisationIsActive):
        self.__init__()
        self.visualisationIsActive = True
      else:
        self.__init__()
      self.lastReward = lastReward

      return np.array(self.getState())

    # Der aktuelle State des Frames wird im für die KI lesbaren Format zurückgegeben.
    # Es werden 21 Zahlen zurückgegeben, jeweils im Bereich zwischen 0 und 1, die später den Input-Neuronen des NN übergeben werden.
    def getState(self):
      # Erstellung von Array mit den Default-Werten (0) für Münzen
      starState = [0 for _ in range(10)]

      # Dieser Array wird (meistens teilweise) mit den Koordinaten der Münzen gefüllt.
      sterneAufFeld = []
      for stern in self.stars:
        if(stern[0] > 0 and stern[1] > -59):
          sterneAufFeld.append(stern.copy())
      if(len(sterneAufFeld) > 5 ):
        print("FEHLER: ES SIND MEHR ALS 5 STERNE AUF DEM FELD")

      # Normalisieren der Koordinaten der Münzen.
      for i in range(len(sterneAufFeld)):
        sterneAufFeld[i][0] = sterneAufFeld[i][0] / self.screenSize[0]
        sterneAufFeld[i][1] = sterneAufFeld[i][1] / self.screenSize[1]

      # Diese 2D-Liste in eine 1D-Liste umwandeln.
      sterneState = [element for sublist in sterneAufFeld for element in sublist]
      for zahl in reversed(sterneState):
        starState.insert(0, zahl)
        starState.pop()

      # Das gleiche geschieht für die Gletscher:

      # Erstellung von Array mit den Default-Werten (0) für Münzen
      iceState = [0 for _ in range(10)]

      # Dieses Array wird (meistens teilweise) mit den Koordinaten der Gletscher gefüllt.
      icebergAufFeld = []
      for iceberg in self.icebergs:
        if(iceberg[0] > 0 and iceberg[1] > -130):
          icebergAufFeld.append(iceberg.copy())

      if(len(icebergAufFeld) > 5 ):
        print("FEHLER: ES SIND MEHR ALS 5 STERNE AUF DEM FELD")

      # Normalisieren der Koordinaten der Münzen.
      for i in range(len(icebergAufFeld)):
        icebergAufFeld[i][0] = icebergAufFeld[i][0] / self.screenSize[0]
        icebergAufFeld[i][1] = icebergAufFeld[i][1] / self.screenSize[1]
      icebergState = [element for sublist in icebergAufFeld for element in sublist]

      # Diese 2D-Liste in eine 1D-Liste umwandeln.
      for zahl in reversed(icebergState):
        iceState.insert(0, zahl)
        iceState.pop()

      # Die Arrays der Gletscher und der Münzen werden jeweils mit der X-Koordinate des Flugzeugs konkateniert.
      returnValue = starState + iceState + [(self.planeX + abs(self.cornerLeft -3 )) / (abs(self.cornerLeft -3) + self.cornerRight)]

      return returnValue


    def close(self):
      pygame.quit()
    def closeIfQuit(self):
       for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
