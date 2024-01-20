from random import randint
class BoardException(Exception):
    pass
class BoardOutException:
    def __init__(self):
        return "Вы пытаетесь выстрелить за пределы поля"

class BoardInException:
    def __init__(self):
        return "Вы уже стреляли в эту клетку"
class BoardWrongShipPlace(Exception):
    pass

class Dot:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.y == other.y and self.x == other.x
    def __repr__(self):
        return f'Точка ({self.y},{self.x})'
class Ship:
    _life_point = 1
    def __init__(self,width,start,direction):
        self.width = width
        self.start = start
        self.direction = direction
    @property
    def life_point(self):
        return self._life_point

    @life_point.setter
    def life_point(self, value):
        if value > 0:
            self._life_point = value
        else:
            raise ValueError('Корабль мертв')


    @property
    def ShipDot(self):
        ship_dot = []
        for i in range(self.width):
            start_x = self.start.x
            start_y = self.start.y

            if self.direction == 0:
                start_x +=i
            elif self.direction == 1:
                start_y +=i

            ship_dot.append(Dot(start_x,start_y))
        return ship_dot
    def hit(self,shot):
        return shot in self.ShipDot

class Board:
    def __init__(self,hid=False,size=6):
        self.size = size
        self.field = [["O"]*size for _ in range(size)]
        self.all_ships = []
        self.hid = hid
        self.life_ships = []
        self.count = 0
    def __str__(self):
        s = '    1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            s = s + f"\n{i+1} | " + " | ".join(row) + " |"
        if self.hid:
            s = s.replace('■',"0")
        return s
    def out_of(self,s):
        return not((0<= s.x < self.size) and (0<= s.y < self.size))

    def contur(self,ship,die = False):
        m_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.ShipDot:
            for dx, dy in m_list:
                m_dot = Dot(d.x + dx, d.y + dy)
                if not (self.out_of( m_dot)) and  m_dot not in self.all_ships:
                    if die:
                        self.field[ m_dot.x][ m_dot.y] = "."
                    self.all_ships.append( m_dot)

    def add_ship(self, ship):
        for d in ship.ShipDot:
            if self.out_of(d) or d in self.all_ships:
                raise BoardWrongShipPlace()
        for d in ship.ShipDot:
            self.field[d.x][d.y] = "■"
            self.all_ships.append(d)

        self.life_ships.append(ship)
        self.contur(ship)

    def shot(self, d):
        if self.out_of(d):
            raise BoardOutException()

        if d in self.all_ships:
            raise BoardInException()

        self.all_ships.append(d)

        for ship in self.life_ships:
            if ship.hit(d):
                ship.life_point -= 1
                self.field[d.x][d.y] = "X"
                if ship.life_point == 0:
                    self.count += 1
                    self.contur(ship, die=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    def begin_m(self):
        self.all_ships = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        turn = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {turn.x+1} {turn.y+1}")
        return turn

class User(Player):
    def ask(self):
        while True:
            turn = input("Ваш ход: ").split()

            if len(turn) != 2:
                print(" Сделайте выстрел! (Введите 2 числа!) ")
                continue

            x, y = turn

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        width = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in width:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(l,Dot(randint(0, self.size), randint(0, self.size)),randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipPlace:
                    pass
        board.begin_m()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()




