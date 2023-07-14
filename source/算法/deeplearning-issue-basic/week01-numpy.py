import numpy as np

def sigmoid(x):
    return 1/(1+np.exp(-x))

def sigmoid_grad(x):
    s=sigmoid(x)
    return s*(1-s)

def image2vector(image):
    """
    Argument:
    向量化
    image -- a numpy array of shape (length, height, depth)
    
    Returns:
    v -- a vector of shape (length*height*depth, 1)
    """
    
    ### START CODE HERE ### (≈ 1 line of code)
    v = image.reshape(image.shape[0] * image.shape[1] * image.shape[2], 1)
    ### END CODE HERE ###
    return v

def normalizeRows(x):
    x_norm = np.linalg.norm(x, axis = 1, keepdims = True)
    x = x / x_norm
    return x

def softmax(x):
    x_exp=np.exp(x)
    x_sum=np.sum(x_exp,axis=1,keepdims=True)
    s=x_exp/x_sum
    return s

#L1、L2损失函数
def L1(yhat,y):
    return np.sum(np.abs(y-yhat))
def L2(yhat,y):
    return np.dot((y-yhat),(y-yhat).T)

if __name__ == '__main__':
    array=np.array([1,2,3])+3
   
    print(sigmoid_grad(array))


    image = np.array([[[ 0.67826139,  0.29380381],
        [ 0.90714982,  0.52835647],
        [ 0.4215251 ,  0.45017551]],

       [[ 0.92814219,  0.96677647],
        [ 0.85304703,  0.52351845],
        [ 0.19981397,  0.27417313]],

       [[ 0.60659855,  0.00533165],
        [ 0.10820313,  0.49978937],
        [ 0.34144279,  0.94630077]]])

    print ("image2vector(image) = " + str(image2vector(image)))

    x = np.array([
    [0, 3, 4],
    [1, 6, 4]])
    print("normalizeRows(x) = " + str(normalizeRows(x)))

    x=np.array([
        [9,2,5,0,0],
        [7,5,0,0,0]
    ])
    print(softmax(x))

    #向量化
    import time
    x1=[1,2,3,4,5,6,7,8,9,0]
    x2=[10,11,23,44,55,66,77,88,99,1]
    W = np.random.rand(3,len(x1))

    tic=time.process_time()
    print(tic)
    dot=0
    for i in range(len(x1)):
        dot+=x1[i]*x2[i]
    toc=time.process_time()
    print("dot:"+str(dot)+"\nprocess time:"+str(1000*(toc-tic))+"ms")

    tic=time.process_time()
    dot=np.dot(x1,x2)
    mul=np.multiply(x1,x2)
    gdot=np.dot(W,x1)
    toc=time.process_time()
