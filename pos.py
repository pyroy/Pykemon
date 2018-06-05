import unittest


class Pos:
    def __init__(self, *args, x=None, y=None):
        if x and y:
            self.x = x
            self.y = y
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.x = args[0][0]
            self.y = args[0][1]
        elif len(args) == 2 and type(args[0]) in [int, float] and type(args[1]) in [int, float]:
            self.x, self.y = args
        else:
            raise ValueError(f"The arguments to Pos are not cool, bro. You see this: {args}?, THAT'S WRONG!!")

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise KeyError(f"Key {key} is out of range in Pos")

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __add__(self, other):
        return Pos(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Pos(self.x - other[0], self.y - other[1])

    def __mul__(self, other):
        return Pos(self.x * other, self.y * other)

    def __round__(self, ndigits=None):
        return Pos(round(self.x, ndigits), round(self.y, ndigits))

    def __truediv__(self, other):
        return Pos(self.x / other, self.y / other)

    def __floordiv__(self, other):
        return Pos(self.x // other, self.y // other)

    def __str__(self):
        return f"Pos({self.x}, {self.y})"

    def __repr__(self):
        return f"Pos({self.x}, {self.y})"

    def __iter__(self):
        return iter([self.x, self.y])

    def __tuple__(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))


class Test(unittest.TestCase):
    def test_init(self):
        p = Pos(4, 5)
        self.assertEqual([p.x, p.y], [4, 5])
        self.assertEqual([p[0], p[1]], [4, 5])

        p = Pos((10, -5))
        self.assertEqual([p.x, p.y], [10, -5])
        self.assertEqual([p[0], p[1]], [10, -5])

        p = Pos((0, 6))
        self.assertEqual([p.x, p.y], [0, 6])
        self.assertEqual([p[0], p[1]], [0, 6])

    def test_add(self):
        self.assertEqual(Pos(4, 5) + Pos(1, 3), Pos(5, 8))
        self.assertEqual(Pos(-3, 10) + (4, -3), Pos(1, 7))
        self.assertEqual(Pos(5, 8) + [-5, -5], Pos(0, 3))
        p = Pos(4, 5)
        p += (5, 9)
        self.assertEqual(p, Pos(9, 14))

    def test_sub(self):
        self.assertEqual(Pos(7, 3) - Pos(5, 0), Pos(2, 3))
        self.assertEqual(Pos(1, 3) - Pos(6, 7), Pos(-5, -4))

    def test_mul(self):
        self.assertEqual(Pos(5, 3)*4, Pos(20, 12))
        self.assertEqual(Pos(0, 1)*0.5, Pos(0, 0.5))

    def test_div(self):
        self.assertEqual(Pos(16, 8)/4, Pos(4, 2))
        self.assertEqual(Pos(3, 6)/0.5, Pos(6, 12))

    def test_true_div(self):
        self.assertEqual(Pos(15, 4)//6, Pos(2, 0))
        self.assertEqual(Pos(20, -5)//5, Pos(4, -1))

    def test_round(self):
        self.assertEqual(round(Pos(15.6, 1.1)), Pos(16, 1))
        self.assertEqual(round(Pos(1, 6)), Pos(1, 6))

    def test_str(self):
        self.assertEqual(str(Pos(4, 5)), "Pos(4, 5)")
        self.assertEqual(str(Pos(0, 0)), "Pos(0, 0)")

    def test_eq(self):
        self.assertTrue(Pos(5, 7) == Pos(5, 7))
        self.assertFalse(Pos(5, 7) == (0, 9))
        self.assertFalse(Pos(5, 7) == [5, 6])
        self.assertFalse(Pos(5, 7) == Pos(6, 7))

    def test_in(self):
        self.assertIn(Pos(5, 7), [Pos(5, 7), Pos(1, 2)])
        self.assertNotIn(Pos(5, 7), [Pos(1, 2), Pos(6, 7)])

if __name__ == '__main__':
    unittest.main()
