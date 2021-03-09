import tkinter as tk
import random
import time


class Game(tk.Tk):
    WIDTH_BG, HEIGHT_BG = 700, 800
    WIDTH_S1, WIDTH_S2 = HEIGHT_BG*0.3, HEIGHT_BG*0.6
    HEIGHT_S = HEIGHT_BG-30

    def __init__(self, r=20):
        super().__init__()
        self.canvas = tk.Canvas(width=self.WIDTH_BG, height=self.HEIGHT_BG,
                                bg="black")
        self.canvas.pack()
        self.ship_1 = Ship(self.canvas, self.WIDTH_S1, self.HEIGHT_S, r)
        self.ship_2 = Ship(self.canvas, self.WIDTH_S2, self.HEIGHT_S, r)
        self.bind_all_keys()
        self.display_game_score()
        self.id_bombs = []
        self.add_bombs()
        self.run = True
        self.new_bombs()

        self.time = 40
        self.game_started = time.time()
        self.time_label = self.canvas.create_text(self.WIDTH_BG/2,
                                                  self.HEIGHT_S, text="00:00",
                                                  font="arial 30",
                                                  fill="orangered")

    def bind_all_keys(self):
        # Bind all keys for SHIP_1
        self.canvas.bind_all("<KeyPress-Up>", self.ship_1.keypress_up)
        self.canvas.bind_all("<KeyRelease-Up>", self.ship_1.keyrelease_up)
        self.canvas.bind_all("<KeyPress-Down>", self.ship_1.keypress_down)
        self.canvas.bind_all("<KeyRelease-Down>", self.ship_1.keyrelease_down)
        # Bind all keys for SHIP_2
        self.canvas.bind_all("<KeyPress-w>", self.ship_2.keypress_up)
        self.canvas.bind_all("<KeyRelease-w>", self.ship_2.keyrelease_up)
        self.canvas.bind_all("<KeyPress-s>", self.ship_2.keypress_down)
        self.canvas.bind_all("<KeyRelease-s>", self.ship_2.keyrelease_down)

    def add_bombs(self):
        for i in range(random.randint(2, 5)):
            id = Bomb(self.canvas, self.WIDTH_BG, self.HEIGHT_BG)
            self.id_bombs.append(id)

    def new_bombs(self):
        if self.run:
            self.add_bombs()
            self.canvas.after(800, self.new_bombs)
        else:
            pass

    def display_game_time(self):
        t = self.time - int(time.time() - self.game_started)
        min = t // 60
        sec = t % 60
        time_string = "{:02d}:{:02d}".format(min, sec)
        self.canvas.itemconfig(self.time_label, text=time_string)
        return t

    def display_game_score(self):
        self.ship_1_score = self.canvas.create_text(40, self.HEIGHT_S-10,
                                                    text="0", font="arial 30",
                                                    fill="white")
        self.ship_2_score = self.canvas.create_text(self.WIDTH_BG-40,
                                                    self.HEIGHT_S-10, text="0",
                                                    font="arial 30",
                                                    fill="white")

    def udpate_score(self):
        self.canvas.itemconfig(self.ship_1_score, text=self.ship_1.score)
        self.canvas.itemconfig(self.ship_2_score, text=self.ship_2.score)

    def timer(self):
        self.ship_1.tik()
        self.ship_2.tik()
        self.bind_all_keys()
        self.udpate_score()
        for i in self.id_bombs:
            i.tik()
            if self.ship_1.crash_ship(i):
                self.ship_1.destroy()
            if self.ship_2.crash_ship(i):
                self.ship_2.destroy()
        t = self.display_game_time()
        if t <= 0:
            self.game_over()
        else:
            self.canvas.after(40, self.timer)

    def game_over(self):
        self.run = False
        self.canvas.delete(self.ship_1)
        self.canvas.delete(self.ship_2)
        for i in self.id_bombs:
            i.destroy()
        self.canvas.create_text(self.WIDTH_BG/2, self.HEIGHT_BG/2,
                                fill="green", text="GAME OVER",
                                font="arial 40")


class Bomb:
    CHOICE = [True, False]

    def __init__(self, canvas, max_x, max_y):
        self.canvas = canvas
        self.x, self.max_x = 0, max_x
        self.y = random.randint(10, max_y-70)
        self.r = random.randint(3, 10)
        self.speed = random.randint(3, 5)
        self.direction = self.get_direction()
        self.draw_bomb(self.x, self.y, self.r)

    def draw_bomb(self, x, y, r):
        self.id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white",
                                          outline="white")

    def destroy(self):
        self.canvas.delete(self.id)

    def get_direction(self):
        if random.choice(self.CHOICE):
            self.x = 0
            return True
        else:
            self.x = self.max_x
            return False

    def move(self):
        if self.direction:
            x = self.x + self.speed
            if x < self.max_x:
                self.x = x
            else:
                self.destroy()
        else:
            x = self.x - self.speed
            if 0 < x:
                self.x = x
            else:
                self.destroy()
        self.canvas.coords(self.id, self.x-self.r, self.y-self.r,
                           self.x+self.r, self.y+self.r)

    def tik(self):
        self.move()


class Ship:
    def __init__(self, canvas, x, y, r):
        self.canvas = canvas
        self.max_height, self.start_x = y, x
        self.x, self.y = x, y
        self.r = r
        self.dy = 0
        self.score = 0
        self.id = self.canvas.create_oval(self.x-r, self.y-r, self.x+r,
                                          self.y+r, fill="gray")

    def move(self):
        y = self.dy + self.y
        if self.r/2 <= y <= self.max_height:
            self.y = y
        if self.r/2 == self.y:
            self.score += 1
            self.destroy()
        else:
            self.canvas.coords(self.id, self.x-self.r, self.y-self.r,
                               self.x+self.r, self.y+self.r)

    def destroy(self):
        self.y = self.max_height
        self.canvas.coords(self.id, self.start_x-self.r,
                           self.max_height-self.r, self.start_x+self.r,
                           self.max_height+self.r)

    def crash_ship(self, bomb):
        dst = ((self.x - bomb.x)**2 + (self.y - bomb.y)**2)**0.5
        if dst < 30:
            return True

    def keypress_up(self, event):
        self.dy = -5

    def keyrelease_up(self, event):
        self.dy = 0

    def keypress_down(self, event):
        self.dy = 5

    def keyrelease_down(self, event):
        self.dy = 0

    def tik(self):
        self.move()


game = Game()
game.timer()
game.mainloop()
