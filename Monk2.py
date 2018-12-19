from Monk import *
from MLP import *
from Activation_Functions import *
from matplotlib import pyplot as plt
from Utility import *
X, Y = load_monk("monks-2.train")
X_val, Y_val = load_monk("monks-2.test")

mlp = MLP(17,3,1,TanhActivation(),SigmoidActivation(),eta=0.8,alfa=0.6,lambd=0,fan_in_h=True,range_start_h=-0.4,range_end_h=0.4)
mlp.train(addBias(X),Y,addBias(X_val),Y_val,500,1e-6)

plt.subplot(2,1,1)
plt.plot(mlp.errors_tr)
plt.plot(mlp.errors_vl)
plt.subplot(2,1,2)
plt.plot(mlp.accuracies_tr)
plt.plot(mlp.accuracies_vl)
plt.show()