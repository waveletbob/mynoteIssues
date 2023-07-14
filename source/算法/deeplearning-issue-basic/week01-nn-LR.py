import numpy as np
# import matplotlib.pyplot as plt
import h5py
from numpy.lib.arraysetops import isin
import scipy
from PIL import Image
from scipy import ndimage
from lr_utils import load_dataset

train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes=load_dataset()

index=5
print("y="+str(train_set_y_orig[:,index]))
m_train=train_set_x_orig.shape[0]
num_px=train_set_x_orig.shape[1]
"""

算法的一般架构：
1、初始化模型参数
2、计算损失函数和梯度
3、使用优化算法
4、模型训练并测试集测试
"""

def initialize_with_zeros(dim):
    w=np.zeros((dim,1))
    b=0
    assert(w.shape==(dim,1))
    assert(isinstance(b,float) or isinstance(b,inc))
    return w,b

