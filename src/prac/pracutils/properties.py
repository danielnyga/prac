# PROBABILISTIC ROBOT ACTION CORES
#
# (C) 2015 by Mareike Picklum (mareikep@cs.uni-bremen.de)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# hsv values for color similarity calculation
chrcolorspecs = {
                'pink.s.01': (335, 87, 87),
                'purple.s.01': (290, 87, 87),
                'blue.s.01': (235, 87, 87),
                'light-blue.s.01': (175, 87, 87),
                'cyan.s.01': (150, 87, 87),
                'green.s.01': (115, 87, 87),
                'yellow.s.01': (50, 87, 87),
                'yellowish.s.01': (50, 87, 87),
                'orange.s.01': (20, 87, 87),
                'brown.s.01': (20, 87, 97),
                'red.s.01': (0, 87, 87),
                'blood-red.s.01': (0, 89, 55)
}

achrcolorspecs = {
                'black.a.01': (0, 55, 5),
                'blackish.s.01': (0, 55, 5), 
                'white.a.01': (0, 5, 95),
                'whitish.s.02': (0, 5, 95),
                'grey.s.01': (0, 5, 50),
                'greyish.s.01': (0, 5, 50),
                'gray.s.01': (0, 5, 50),
                'grayish.s.01': (0, 5, 50)
}


# similarity represented by (#edges, #angles, #faces, #subjective similarity)
# does not work for all shapes due to lack of information (then using rule
# of thumb estimate)
# #edges/angles/faces for curved, annular, ringlike...?
# hexangular, octangular... 2D or 3D??
shapespecs = {
                'crescent.s.01': (2, 2, 1, 0),
                'semicircular.s.01': (2, 2, 1, 1),
                'curved.a.01': (2, 0, 1, 2),
                'annular.s.01': (2, 0, 1, 4),  # ringfoermig
                'ringlike.s.01': (2, 0, 1, 4),
                'coil.n.02': (2, 0, 1, 5),  # spiralfoermig
                'coiling.s.01': (2, 0, 1, 5),  # spiralfoermig
                'rounded.a.01': (0, 0, 1, 6),
                'roundish.s.01': (0, 0, 1, 7),
                'egg-shaped.s.01': (0, 0, 1, 8),
                'ellipse.n.01': (0, 0, 1, 8),
                'flat.s.02': (0, 0, 1, 6),
                'elliptic.s.01': (0, 0, 1, 8),
                'ellipsoid.s.01': (0, 0, 1, 8),
                'pear-shaped.s.01': (0, 0, 1, 9),
                'cylindrical.s.01': (2, 0, 3, 10),
                'round.a.01': (0, 0, 1, 7.5),
                'spherical.a.01': (0, 0, 1, 11.1),
                'ball-shaped.s.01': (0, 0, 1, 11.2),
                'circular.s.02': (0, 0, 1, 11),
                'circular.n.01': (0, 0, 1, 11),
                'hemispherical.a.01': (0, 0, 1, 15),
                'octangular.a.01': (8, 8, 1, 14),
                'hexangular.a.01': (6, 6, 1, 15),
                'pentangular.a.01': (5, 5, 1, 16),
                'quadrangular.a.01': (4, 4, 1, 17),
                'square.n.01': (4, 4, 1, 17),
                'square-shaped.s.01': (4, 4, 1, 17),
                'rectangle.n.01': (4, 4, 1, 18),
                'rectangular.s.01': (4, 4, 1, 18),
                'orthogonal.s.03': (4, 4, 1, 20),
                'boxlike.s.01': (12, 8, 6, 19),
                'trapezoidal.a.01': (4, 4, 1, 21),
                'rhombic.a.01': (4, 4, 1, 22),
                'triangle.n.01': (3, 3, 1, 24),
                'triangular.s.01': (3, 3, 1, 25),
                'pyramidal.s.01': (5, 5, 5, 26),
                'wedge-shaped.a.02': (9, 6, 5, 27),
                'pronged.s.01': (8, 4, 2, 27),
                'cuneate.s.01': (3, 3, 1, 28),  # keilfoermig
                'conic.a.01': (2, 1, 2, 29),
                'tapered.s.01': (2, 1, 2, 30),  # kegelfoermig
                'star-shaped.s.01': (10, 5, 1, 35),
                'cordate.s.01': (2, 2, 1, 40),  # herzfoermig
                'convex.a.01': (1, 1, 2, 40),
                'concave.a.01': (3, 3, 2, 40),
                'hollow.a.01': (3, 3, 2, 45),
}


sizespecs = {
                'dwarfish.s.01': 0,
                'bantam.s.01': 1,
                'little.s.03': 2,
                'shallow.a.01': 2.5,  # todo remove! belongs to dimension!
                'small.a.01': 3,
                'modest.s.02': 4,
                'average.s.04': 5,
                'medium-sized.s.01': 5,
                'large.a.01': 7,  # 'big'
                'huge.s.01': 8,
                'grand.s.06': 9,
}


consistencyspecs = {
                'thin.a.05': 1,
                'liquid.a.01': 2,
                'creamy.s.02': 3,
                'bubbling.s.01': 4,
                'sticky.s.02': 5,
                'sticky.s.05': 5,
                'spongy.s.01': 6,
                'spongy.s.02': 6,
                'gluey.s.01': 7,
                'pulpy.s.01': 9,
                'limp.s.02': 11,
                'feathery.s.02': 15,
                'feathery.s.03': 15,
                'featherlike.s.01': 15,
                'soft.s.15': 16,
                'soft.a.01': 16,
                'smooth.a.01': 16.5,
                'downy.s.01': 16,
                'downy.s.02': 17,
                'firm.s.02': 20,
                'dense.s.01': 21,
                'dense.s.03': 21,
                'thick.a.03': 21,
                'compact.s.02': 25,
                'crisp.s.02': 26,
                'breakable.a.01': 27,
                'porous.s.01': 28,
                'porous.a.02': 28,
                'solid.a.03': 29,
                'hard.a.03': 30,
                'unbreakable.a.01': 31
}


dimensionspecs = {	
                'fine.s.03': 1,
                'thin.a.01': 1.5,
                'shallow.a.01': 1.7,
                'low.a.02': 2,
                'squat.s.02': 2,
                'short.a.02': 3.5,
                'short.a.03': 3.5,
                'slender.s.02': 4,
                'narrow.a.01': 5,
                'wide.a.01': 7.2,  # 'broad'
                'broad.s.06': 7.2,
                'chunky.s.02': 8,
                'thick.a.01': 8,
                'dense.s.02': 9,
                'elongated.s.02': 10,
                'long.a.02': 11,
                'long.s.03': 11,
                'high.a.02': 12,
                'tall.a.01': 12
}

numbrs = {
                'one-sixty-fourth.n.01': 0.015625,
                'one-sixtieth.n.01': 0.016666667,
                'one-seventh.n.01': 0.142857143,
                'one-quadrillionth.n.01': 1e-15,
                'one-hundred-millionth.n.01': 1e-08,
                'one-billionth.n.01': 1e-09,
                'one-hundred-thousandth.n.01': 1e-05,
                'one-twelfth.n.01': 0.08333333333333333,
                'one-half.n.01': 0.5,
                'one-hundredth.n.01': 0.01,
                'one-third.n.01': 0.3333333333333333,
                'one-trillionth.n.01': 1e-12,
                'one-ten-thousandth.n.01': 0.0001,
                'one-ninth.n.01': 0.1111111111111111,
                'one-tenth.n.01': 0.1,
                'one-eighth.n.01': 0.125,
                'one-millionth.n.01': 1e-06,
                'one-fifth.n.01': 0.2,
                'one-thousandth.n.01': 0.001,
                'two-thirds.n.01': 0.6666666666666666,
                'one-sixteenth.n.01': 0.0625,
                'one-sixth.n.01': 0.16666666666666666,
                'one-fourth.n.01': 0.25,
                'three-fourths.n.01': 0.75,
                'one-quintillionth.n.01': 1e-18,
                'one-thirty-second.n.01': 0.03125,
                'fifty.n.01': 50.0,
                'octillion.n.01': 1e+27,
                'great_gross.n.01': 1728.0,
                'forty.n.01': 40.0,
                'trillion.n.03': 1e+18,
                'twenty-nine.n.01': 29.0,
                'billion.n.01': 1e+12,
                'trillion.n.02': 1e+12,
                'sixty.n.01': 60.0,
                'ten.n.01': 10.0,
                'twenty-two.n.01': 22.0,
                'quintillion.n.01': 1e+18,
                'septillion.n.01': 1e+24,
                'sixteen.n.01': 16.0,
                'eighteen.n.01': 18.0,
                'twenty.n.01': 20.0,
                'hundred.n.01': 100.0,
                'quadrillion.n.01': 1e+24,
                'twenty-four.n.01': 24.0,
                'seventeen.n.01': 17.0,
                'ten_thousand.n.01': 10000.0,
                'seventy-eight.n.01': 78.0,
                'crore.n.01': 10000000.0,
                'million.n.01': 1000000.0,
                'nineteen.n.01': 19.0,
                'twenty-one.n.01': 21.0,
                'thirteen.n.01': 13.0,
                'ninety.n.01': 90.0,
                'seventy.n.01': 70.0,
                'twenty-three.n.01': 23.0,
                'gross.n.01': 144.0,
                'long_hundred.n.01': 120.0,
                'twelve.n.01': 12.0,
                'quadrillion.n.02': 1e+15,
                'hundred_thousand.n.01': 100000.0,
                'twenty-five.n.01': 25.0,
                'sextillion.n.01': 1e+21,
                'fifteen.n.01': 15.0,
                'five_hundred.n.01': 500.0,
                'fourteen.n.01': 14.0,
                'eleven.n.01': 11.0,
                'twenty-seven.n.01': 27.0,
                'billion.n.03': 1e+09,
                'thirty.n.01': 30.0,
                'thousand.n.01': 1000.0,
                'eighty.n.01': 80.0,
                'aleph-null.n.01': float('inf'),
                'twenty-six.n.01': 26.0,
                'twenty-eight.n.01': 28.0
}
