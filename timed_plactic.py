from numpy import array

class TimedWord:
    """
    The class of timed words.
    """
    def __init__(self, w):
        """
        Initialize ``self`` from ``w``.

        INPUT:

        ``w`` - a list of pairs ``(c, t)`` where ``c`` is a positive integer
                and ``t`` is a positive real number.

        EXAMPLE::

            sage: TimedWord([(2, 1.5), (1, 1.324)])
            [(2, 1.5), (1, 1.324)]
            sage: TimedWord([(2, 1.2), (1, 0), (2, 1)])
            [(2, 2.2)]
        """
        if isinstance(w, TimedWord):
            self._w = w._w
        elif len(w) == 0:
            self._w = []
        else:
            v = [tuple(w[0])]
            for i in range(1, len(w)): # ingore terms with zero time
                if w[i][1] == 0:
                    print "Im here"
                    pass
                elif w[i][0] == v[-1][0]: # merge common consecutive terms
                    v[-1] = (v[-1][0], v[-1][1]+w[i][1])
                else:
                    v.append((w[i][0], w[i][1]))
            self._w = v

    def __repr__(self):
        """
        Return the sring representations of ``self``.
        """
        return str(self._w)

    def to_list(self):
        """
        Return the list underlying ``self``.
        """
        return self._w

    def rows(self):
        """
        Return the row decomposition of ``self``.
        """
        if self._w == []:
            return []
        output = [[self._w[0]]]
        for entry in self._w[1:]:
            if entry[0] >= output[-1][-1][0]:
                output[-1].append(entry)
            else:
                output.append([entry])
        return [TimedRow(r) for r in output]
        b = break_into_rows(self._w)
        return [r for r in b]

    def is_row(self):
        """
        Return if ``self`` is a row.
        """
        return all([self._w[i][0]<= self._w[i+1][0] for i in range(len(self._w)-1)])
    
    def length(self):
        """
        Return the length to ``self``.

        The length of a timed word is the sum of timings of its terms.
        """
        return sum([term[1] for term in self._w])

    def value(self, t):
        """
        Return the value of ``self`` at time ``t``.

        NOTE:

        The function associated to a timed word is right continuous. 
        """
        t0 = 0
        for i, l in enumerate(self._w):
            t1 = t0 + l[1]
            if t1 > t:
                return l[0]
            else:
                t0 = t1
        return 0

    def segments(self):
        """
        Return the points of discontinuity of ``self``.
        """
        durations = [l[1] for l in self._w]
        return [sum(durations[:i]) for i in range(len(self._w))]

    def is_tableau(self):
        b = self.rows()
        if len(b) == 1:
            return True
        else:
            return all([TimedRow(b[i]).dominates(TimedRow(b[i+1])) for i in range(len(b)-1)])

    def number_of_rows(self):
        return len(self.rows())

    def concatenate(self, other):
        return TimedWord(self._w + other._w)

    def schensted(self):
        """
        Return the insertion tableau of ``self``.

        The Schensted tableau of a timed word is the unique tableaux that is
        plactic equivalent to it.
        """
        output = TimedTableau([])
        for row in self.rows():
            output = output.insert_row(row)
        return output
        
class TimedTableau(TimedWord):
    def __init__(self, w):
        TimedWord.__init__(self, w)
        if not self.is_tableau():
            raise ValueError("%s is not a tableau"%(self))

    def split_first_row(self):
        for i in range(1, len(self._w)):
            if self._w[i] < self._w[i-1]:
                break
        first_row = TimedRow(self._w[:i])
        rest = TimedTableau(self._w[i:])
        return first_row, rest
        
    def pre_insert_row(self, row):
        if self.number_of_rows() <= 1:
            rowin = TimedRow(self).insert_row(row)
            return rowin[0], rowin[1]
        else:
            first_row, rest = self.split_first_row()
            bumped, newrest = rest.pre_insert_row(row)
            out = first_row.insert_row(bumped)
            return out[0], TimedTableau(out[1].concatenate(newrest))

    def insert_row(self, row):
        out = self.pre_insert_row(row)
        return TimedTableau(out[0].concatenate(out[1]))

    def shape(self):
        return [TimedRow(r).length() for r in reversed(self.rows())]

    def gt_pattern(self):
        m = max([term[0] for term in self._w])
        arr = [[sum([term[1] for term in row if term[0] < i+1]) for row in reversed(self.rows())] for i in range(1, m+1)]
        return [(line+[0]*(max(0, i + 1 - len(line))))[:i+1] for i, line in enumerate(arr)]
        
class TimedRow(TimedWord):
    """
    The class of timed rows.
    """
    def __init__(self, w):
        if isinstance(w, TimedWord):
            w = w._w
        assert all([w[i][0] <= w[i+1][0] for i in range(len(w)-1)]), "%s is not a row"%(w)
        return TimedWord.__init__(self, w)

    def dominates(self, other):
        """
        Return whether ``self`` dominates ``other``.
        """
        if self.length() > other.length():
            return False
        else:
            s1 = self.segments()
            s2 = other.segments()
            comb = sorted(s1+s2)
            return all([self.value(t) > other.value(t) for t in comb if t < self.length()])
        return dominates(self._w, other._w)

    def insert_term(self, term):
        c = term[0]
        t = term[1]
        if self._w == []:
            return TimedRow([]), TimedRow([[c, t]])
        # Find first term which is greater than c - this is the term w[i]
        postfix = []
        for i, l in enumerate(self._w):
            if l[0] > c:
                break
            else:
                postfix.append(self._w[i])
        else:
            return TimedRow([]), TimedRow(self.concatenate(TimedRow([[c, t]])))
        sofar = 0
        prefix = []
        for j in range(i, len(self._w)):
            next_time = sofar + self._w[j][1]
            if next_time >= t:
                t0 = t - sofar
                prefix.append([self._w[j][0], t0])
                postfix.append([c, t - sofar])
                if next_time > t:
                    postfix.append([self._w[j][0], next_time - t])
                break
            else:
                prefix.append(self._w[j])
                postfix.append([c, self._w[j][1]])
                sofar = next_time
        if next_time < t:
            postfix.append([c, t - sofar])
        else:
            for k in range(j+1, len(self._w)):
                postfix.append(self._w[k])
        return TimedRow(prefix), TimedRow(postfix)

    def insert_row(self, other):
        first_row = TimedRow([])
        second_row = self
        for term in other._w:
            step = second_row.insert_term(term)
            second_row = step[1]
            first_row = TimedRow(first_row.concatenate(step[0]))
        return TimedRow(first_row), TimedRow(second_row)

def random_word(max_let, terms, max_time=1):
    return TimedWord([[randint(1, max_let), max_time*random()] for i in range(terms)])

def random_row(max_let):
    return TimedRow([[i+1, random()] for i in range(max_let)])

def random_term(max_let):
    return [randint(1, max_let), random()]

def plactic_rsk(A):
    return (TimedWord([[j+1, A[i,j]] for i in range(A.shape[0]) for j in range(A.shape[1])]).schensted(), TimedWord([[i+1, A[i,j]] for j in range(A.shape[1]) for i in range(A.shape[0])]).schensted())
    
w1 = TimedWord([[1, 1], [2, 1.5], [4, 2], [3, 1.2], [1, 3]])
w2 = TimedTableau([[2, 1], [3, 1.5], [1, 1.5], [2, 1.5], [3, 0.2]])
w3 = TimedWord([[2, 1], [2, 1], [1, 2]])
r = TimedRow([[1, 0.5], [2, 0.3], [3, 0.1], [4, 0.7]])
