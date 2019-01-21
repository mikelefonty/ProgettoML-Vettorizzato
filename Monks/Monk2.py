from Monks.Monk import *
from MLP.Activation_Functions import *
from matplotlib import pyplot as plt
from MLP.MLP import *
import time


X, Y = load_monk("../Datasets/monks-2.train")
X_val, Y_val = load_monk("../Datasets/monks-2.test")

mlp = MLP(17,3,1,TanhActivation(),SigmoidActivation(),eta=1,alfa=0.7,lambd=0,fan_in_h=True,range_start_h=-0.2,range_end_h=0.2,trainer=TrainBackprop())
start = time.time()
mlp.trainer.train(mlp,addBias(X),Y,addBias(X_val),Y_val,500,1e-4)
end = time.time()

print("VECTORIZED TIME ELAPSED = %3f sec per epoch"%((end-start)/500))

st = plt.suptitle("Monk 2")
plt.subplot(2,1,1)
plt.plot(mlp.errors_tr,label='Training Error',ls="-")
plt.plot(mlp.errors_vl,label='Validation Error',ls="dashed")
plt.ylabel('loss')
plt.grid(True)
plt.xlabel('epoch')
plt.legend(loc='upper right',prop={'size':12})

plt.subplot(2,1,2)
plt.plot(mlp.accuracies_tr,label='Training Accuracy',ls="-")
plt.plot(mlp.accuracies_vl,label='Validation Accuracy',ls="dashed")
plt.ylabel('Accuracy')
plt.grid(True)
plt.xlabel('epoch')
plt.legend(loc='lower right',prop={'size':12})
plt.show()