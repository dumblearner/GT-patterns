import numpy as np
import pandas as pd

class GTPatterns:
	def __init__(self, a):
		assert all(a[i-1][j] >= a[i][j] >= a[i-1][j+1] for i in range(1, len(a)) for j in range(len(a[i])))
		self.gt = a
		self.matrix = pd.DataFrame(a).fillna(0.0).values
		self.wmatrix = np.zeros(self.matrix.shape)
		for i in range(len(self.matrix)-1):
			self.wmatrix[i] = self.matrix[i] - self.matrix[i+1]
		self.wmatrix[-1] = self.matrix[-1]
	
	def word(self):
		w = ""
		l = len(self.wmatrix)
		for j in range(l-1,-1,-1):
			for i in range(l-j-1,-1,-1):
				w = w+str(l-i)*int(self.wmatrix[i][j])
		return(w)

	def tab(self):
		w = []
		l = len(self.wmatrix)
		for j in range(l):
			if(np.count_nonzero(self.wmatrix[:,j]) == 0):
				continue
			w = w+[[]]
			for i in range(l-j-1,-1,-1):
				w[j] = w[j]+[(l-i)]*int(self.wmatrix[i][j])
		return(w)
	

