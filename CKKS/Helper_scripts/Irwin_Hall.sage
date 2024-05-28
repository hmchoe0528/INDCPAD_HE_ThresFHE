# Irwin-Hall probability for CKKS BTS
# Pr[ ||I(Y)||_\infty > K ]

def Irwin_Hall(n, K, h):
	print("\nIrwin-Hall for n=2^"+str(log(n, 2))+", K="+ str(K) + ", h="+str(h))
	K = floor(K)
	invFactor = 2 / factorial(h+1)
	sum = 0

	for i in range(floor(K+(h+1)/2)+1):
		sum += (-1)^i * binomial(h+1, i) * (K+ (h+1)/2 - i)^(h+1)
	sum *= invFactor
	# print("Prob_per_slot="+ str(numerical_approx(2-sum)))
	print("log2(Prob_per_slot)=" + str(numerical_approx(log( 2-sum, 2))))
	return numerical_approx( 1- (sum -1)^(2*n))

n= 2^16

# h=32, K= 12 to 16
h= 32 

# h=192, K= 25 to 28
#h=192

for K in range(7, 16, 1):
	prob = Irwin_Hall(n, K, h)
	#print("Prob="+ str(prob))
	print("log2(Prob)= "+ str(log(prob, 2)))
