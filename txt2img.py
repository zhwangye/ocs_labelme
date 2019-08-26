import cv2
import os
import numpy as np
"""
将
"""

classnum=4
txtpath='./txt/'
imgpath='./img2/'
savepath='./save/'
resize_w=[1,500,500,200]
resize_h=[1,500,500,1000]
widthscale=1.0
heightscale=1.0
if __name__ == '__main__':
    txt_list = os.listdir(txtpath)
    filepairs=[]
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    for x in range(classnum):
        if not os.path.isdir(savepath+str(x)):
            os.mkdir(savepath+str(x))

    classcnt=np.zeros(classnum,np.int32)
    for x in txt_list:
        name,ext=os.path.splitext(x)
        if os.path.isfile(imgpath+name+'.jpg'):
            filepairs.append([txtpath+x,imgpath+name+'.jpg'])
    for filepair in filepairs:
        rects=np.loadtxt(filepair[0]).reshape((-1,6))
        print(rects)
        img=cv2.imread(filepair[1],cv2.IMREAD_ANYCOLOR)
        img_w=img.shape[1]
        img_h=img.shape[0]
        for line in range(rects.shape[0]):
            rect=rects[line]
            classn=str(int(rect[0]))
            if rect[5]<-45:
                rect[5]+=90
                t= rect[4]
                rect[4]=rect[3]
                rect[3]=t
            t_rect=((rect[1],rect[2]),(rect[3]*widthscale,rect[4]*heightscale),rect[5])
            box=cv2.boxPoints(t_rect)
            srcarray=np.ones_like(box)
            srcarray[:,0]=box[:,0]*img_w
            srcarray[:,1]=box[:,1]*img_h
            dstarray = np.array([[[0, resize_h[int(rect[0])] - 1]],[[0, 0]],[[resize_w[int(rect[0])] - 1, 0]], [[resize_w[int(rect[0])], resize_h[int(rect[0])] - 1]]], np.float32)
            M, mask = cv2.findHomography(srcarray, dstarray)
            output_img = cv2.warpPerspective(img, M, (resize_w[int(rect[0])], resize_h[int(rect[0])]))
            classcnt[int(rect[0])]+=1
            cv2.imshow('zz',output_img)
            cv2.waitKey(0)
            cv2.imwrite(savepath+'/'+classn+'/'+str(classcnt[int(rect[0])])+'.jpg',output_img)





