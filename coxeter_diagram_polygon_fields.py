class Zq: # a class for doing arithmetic over the ~~field~~ ring Z[sqrt(2)]
    def __init__(self, a: int, b: int = 0): # makes a number of the form a + b*q (q = sqrt(2); Wendy's terminology)
        self.a = a
        self.b = b
    def __add__(self, other):
        if type(other) == int:
            other = Zq(other)
        return Zq(self.a + other.a, self.b + other.b)
    def __radd__(self, other):
        return self.__add__(other)
    def __neg__(self):
        return Zq(-self.a, -self.b)
    def __sub__(self, other):
        if type(other) == int:
            other = Zq(other)
        return self + other.__neg__()
    def __rsub__(self, other):
        return self.__sub__(other).__neg__()
    def __mul__(self, other):
        if type(other) == type(self):
            return Zq(self.a*other.a + 2*self.b*other.b, self.a*other.b + self.b*other.a)
        elif type(other) == int:
            return Zq(self.a*other, self.b*other)
        else:
            raise RuntimeError(f"Multiplication between Zq object and type {type(other)} is not supported")
    def __rmul__(self, other): # reverse multiplication (between integer and Zq) is the same as normal multiplication
        return self.__mul__(other)
    def norm(self): # the number times its algebraic conjugate
        return self.a**2 - 2*self.b**2
    def is_invertable(self): # determines whether the number times its algebraic conjugate is +/-1, indicating that it's a unit in the ring
        return self.norm() in [-1, 1]
    def __inv__(self):
        if not self.is_invertable():
            raise RuntimeError(f"{self} is not invertable over Z[q].")
        norm = self.norm()
        return Zq(self.a*norm, -self.b*norm)
    def __pow__(self, exp):
        if type(exp) == int:
            if exp > 0:
                return self**(exp//2)*self**(exp//2)*(self if exp % 2 == 1 else 1)
            if exp == 0:
                return 1
            if exp < 0:
                return (self**(-exp)).__inv__()
    def __str__(self):
        return f"{self.a} + {self.b}q"
    def __eq__(self, other):
        if type(other) == type(self):
            return self.a == other.a and self.b == other.b
        elif type(other) == int:
            return self.a == other and self.b == 0
        else:
            raise RuntimeError(f"Equality comparison between Zq object and type {type(other)} is not supported")
    def __req__(self, other):
        return self.__eq__(other) # reverse equality
    def __floordiv__(self, other):
        # members of this class are supposed to be algebraic *integers* from the field Z[q]
        # (a + bq)/(c + dq) = (a + bq)(c - dq)/(c^2 - 2d^2) = (ac - 2bd)/(c^2 - 2d^2) + (bc - ad)/(c^2 - 2d^2)*q
        # the quotient is an algebraic integer iff c^2 - 2d^2 divides both ac - 2bd and bc - ad
        # it's insufficient to check whether the denominator is a unit after dividing out common factons in the coefficients
        # because, for example, (2 + 0q)/(0 + 1q) has no common factor among its coefficients and q (sqrt(2)) isn't a unit, but (2 + 0q)/(0 + 1q) = 0 + 1q
        # this is implemented as floordiv, not truediv, because the analogous operation with integers has to return an integer type, and this way we can reuse the same code for all fields.
        a = self.a
        b = self.b
        c = other.a
        d = other.b
        if (c, d) == (0, 0):
            raise ZeroDivisionError("Division by zero in ring Z[q]")
        # now, because sqrt(2) is irrational, we know c^2 - 2d^2 != 0
        denom = other.norm()
        numer1 = a*c - 2*b*d
        numer2 = b*c - a*d
        if numer1 % denom == 0 and numer2 % denom == 0:
            return Zq(numer1//denom, numer2//denom)
        else:
            raise RuntimeError(f"Result of dividing {self} by {other} is not an algebraic integer")

class Zf: # a class for doing arithmetic over the ring Z[(-1+sqrt(5))/2], the ring of integers of the field Q[sqrt(5)]
    def __init__(self, a: int, b: int = 0): # makes a number of the form a + b*f (f = phi; Wendy's terminology)
        self.a = a
        self.b = b
    def __add__(self, other):
        if type(other) == int:
            other = Zf(other)
        return Zf(self.a + other.a, self.b + other.b)
    def __radd__(self, other):
        return self.__add__(other)
    def __neg__(self):
        return Zf(-self.a, -self.b)
    def __sub__(self, other):
        if type(other) == int:
            other = Zf(other)
        return self + other.__neg__()
    def __rsub__(self, other):
        return self.__sub__(other).__neg__()
    def __mul__(self, other):
        if type(other) == type(self):
            return Zf(self.a*other.a + self.b*other.b, self.a*other.b + self.b*other.a + self.b*other.b)
        elif type(other) == int:
            return Zf(self.a*other, self.b*other)
        else:
            raise RuntimeError(f"Multiplication between Zf object and type {type(other)} is not supported")
    def __rmul__(self, other): # reverse multiplication (between integer and Zf) is the same as normal multiplication
        return self.__mul__(other)
    def __pow__(self, exp):
        if type(exp) == int:
            if exp > 0:
                return self**(exp//2)*self**(exp//2)*(self if exp % 2 == 1 else 1)
            if exp == 0:
                return 1
            if exp < 0:
                return (self**(-exp)).__inv__()
    def __inv__(self):
        if not self.is_invertable():
            raise RuntimeError(f"{self} is not invertable over Z[f].")
        norm = self.norm()
        return Zf(self.a*norm + self.b*norm, -self.b*norm)
    def is_invertable(self): # determines whether the number times its algebraic conjugate is +/-1, indicating that it's a unit in the ring (I think)
        return self.norm() in [-1, 1]
    def norm(self): # the number times its algebraic conjugate
        return self.a**2 + self.a*self.b - self.b**2
    def __str__(self):
        return f"{self.a} + {self.b}f"
    def __eq__(self, other):
        if type(other) == type(self):
            return self.a == other.a and self.b == other.b
        elif type(other) == int:
            return self.a == other and self.b == 0
        else:
            raise RuntimeError(f"Equality comparison between Zf object and type {type(other)} is not supported")
    def __req__(self, other):
        return self.__eq__(other) # reverse equality
    def __floordiv__(self, other):
        # (a + bf)/(c + df) = (a + bf)(c + d - df)/(c + df)(c + d - df) = (ac + ad - bd - adf + bcf)/(c^2 + cd - d^2)
        a = self.a
        b = self.b
        c = other.a
        d = other.b
        if (c, d) == (0, 0):
            raise ZeroDivisionError("Division by zero in ring Z[q]")
        # now, because phi is irrational, we know c^2 + cd - d^2 != 0
        denom = other.norm()
        numer1 = a*c + a*d - b*d
        numer2 = b*c - a*d
        if numer1 % denom == 0 and numer2 % denom == 0:
            return Zf(numer1//denom, numer2//denom)
        else:
            raise RuntimeError(f"Result of dividing {self} by {other} is not an algebraic integer")

# converts a field value to a tuple containing the identity of the field, so it can be hashed
# where a + b*x in field F is stored as the tuple (F, a, b) and rationals are stored as ('Q', a)
def field_value_to_tuple(field, value):
    if field == 'Q':
        return ('Q', value)
    else:
        return (field, value.a, value.b)

# finds the equivalent of an integer in a specific field class, used for Schalfli matrix entries
def field_equivalent_int(field, n):
    if field == 'Q':
        return int(n)
    elif field == 'Qq':
        return Zq(n)
    elif field == 'Qf':
        return Zf(n)
    else:
        print(f"Integer equivalents for field {field} not yet implemented.")
        return None