# coding:utf-8
import cv2
import os
import numpy as np
import tkinter as tk
from PIL import Image,ImageTk
import math
"""
模式2
用于标注5号相机的9个零件
功能待完善
"""
class Mode2:
    def __init__(self,window,imgPath,txtPath,ptPath):
        self.window = window
        self.COLOR_MAP = [[0, 255, 0], [0, 0, 255], [255, 0, 0]]
        self.RECT_COLOR_MAP = [[0, 255, 0], [0, 0, 255], [255, 0, 0], [255, 255, 0]]
        self.COLOR_CLASS = 4
        self.ptOffset = 4
        self.labelMode = 1
        self.colorMode = 1

        self.curImgPt = np.empty((0, 3), np.float32)
        self.curLblClass = 1
        self.curImgIdx = 0

        self.totalDirList = []
        for imgName in os.listdir(imgPath):
            name = os.path.splitext(imgName)[0]
            self.totalDirList.append([name, imgPath + imgName, txtPath + name + '.txt', ptPath + name + '.npy'])

        # 记录图片数量，从零开始
        self.totalImgNum = len(self.totalDirList) - 1

        self.imgWidth = 1200
        self.imgHeight = 600
        try:
            if self.totalImgNum == 0:
                raise Exception('This path has no images!', 1)
        except Exception:
            print('Error')

        # 初始化显示背景图
        im = cv2.imread(self.totalDirList[self.curImgIdx][1], 0)
        im = cv2.resize(im, (1200,600), cv2.INTER_CUBIC)
        print(np.asarray(im).shape)
        img = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        self.curCvImg = img
        self.curCvImgCp = img.copy()

        # 窗口添加鼠标，键盘监听
        self.window.bind('<Key>', self.onKeydown)
        self.window.bind('<MouseWheel>', self.onMouseWheelMove)
        self.window.focus_set()  # 当前框架被选中，意思是键盘触发，只对这个框架有效

        # 创建主面板
        self.mainFrm = tk.Frame(self.window, width=1920, height=820)
        self.mainFrm.place(x=0, y=0, anchor='nw')

        self.topFrm = tk.Frame(self.mainFrm, width=1920, height=800)
        self.topFrm.place(x=0, y=0, anchor='nw')

        self.imgFrm = tk.Frame(self.topFrm, width=self.imgWidth+10, height=self.imgHeight+10,bg='red')
        self.imgFrm.place(x=0,y=0,anchor='nw')

        self.infoFrm = tk.Frame(self.topFrm, width=250, height=800)
        self.infoFrm.place(x=1300, y=0, anchor='nw')

        # 记录当前点
        self.canvasPt = []
        # 记录当前多边形
        self.canvasPoly = []
        self.curCanvasPoly = []
        # 创建左侧画布，用于显示原图和在该图上进行打标
        # self.imgCanvas = tk.Canvas(self.imgFrm, height=self.imgHeight, width=self.imgWidth,bg='green')
        self.imgCanvas = tk.Canvas(self.imgFrm, height=600, width=1200,bg='green')
        self.imgCanvas.bind(sequence='<Button-1> ', func=self.onClick)
        self.imgCanvas.bind(sequence='<B1-Motion> ', func=self.onMouseDrag)
        self.imgCanvas.bind(sequence='<Button-3>', func=self.onMouseRightClick)
        # self.imgCanvas.place(x=600 + 5, y=300+5, anchor='center')
        self.imgCanvas.place(x=3, y=3, anchor='nw')

        self.curTkImg = ImageTk.PhotoImage(Image.fromarray(np.asarray(self.curCvImg)))
        self.curTkImgRes = self.curTkImg

        self.imgCanvasImg = self.imgCanvas.create_image(0, 0, anchor='nw', image=self.curTkImg)

        ## info 面板内容
        # 当前图片index/图片总数
        self.numFrm = tk.Frame(self.infoFrm, width=220, height=100)
        self.numFrm.place(x=0, y=0, anchor='nw')
        self.imgNumLbl = tk.Label(self.numFrm, text=str(self.curImgIdx) + ' / ' + str(self.totalImgNum),
                                  bg='white', font=('Arial', 12), justify='center', width=320, height=2)
        self.imgNumLbl.place(x=115, y=50, anchor='center')

        # 滑动定位条
        self.scaleBar = tk.Scale(self.infoFrm, from_=0, to=self.totalImgNum, orient=tk.HORIZONTAL, length=220,
                                 showvalue=0, tickinterval=int(self.totalImgNum / 5), resolution=1,
                                 command=self.onScaleBarMove)
        self.scaleBar.place(x=0, y=100, anchor='nw')

        self.curPtIdx = -1
        self.pts=[[203,230],[246,149],[550,180],[863,170],[858,102],[891,112],[1034,235],[1033,292],[1124,369]]
        self.offset = [[25,25],[25,25],[230,160],[25,25],[20,40],[20,40],[25,30],[25,25],[35,35]]
        self.ptsCp = self.pts
        self.offsetCp = self.offset
        # self.draw_poly()
        self.moveScale = 0.01
        self.rotateAngle = 0
        self.glOffset = [[-35,88],[0,0],[0,0],[0,0],[-2,-55],[30,-55],[176,65],[175,122],[266,245]]

    # 更新当前/总数label
    def update_disp_num(self):
        info = str(self.curImgIdx)+' / '+str(self.totalImgNum)
        self.imgNumLbl.config(text=info)
        self.imgNumLbl.update()
        self.rotateAngle = 0


    # 加载本地存储的坐标点
    def load_pts(self):
        if os.path.isfile(self.totalDirList[self.curImgIdx][3]):
            localPts = np.load(self.totalDirList[self.curImgIdx][3])
            self.curImgPt = np.concatenate([self.curImgPt,localPts],0)

    # 清空左canvas片中的点和右侧canvas中的polygon
    def clear_pt(self):
        for pt in self.canvasPt:
            self.imgCanvas.delete(pt)
        self.canvasPt=[]
        self.canvasPoly=[]
        self.curImgPt = np.empty((0,3),np.float32)

    # 更新左侧canvas和右侧canvas图片
    def update_img(self):
        self.load_pts()
        self.scaleBar.set(self.curImgIdx)
        im = cv2.imread(self.totalDirList[self.curImgIdx][1],0)
        im = cv2.resize(im, (self.imgWidth, self.imgHeight), cv2.INTER_CUBIC)
        self.curCvImg = cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
        self.curCvImgCp = self.curCvImg.copy()
        self.curTkImg = ImageTk.PhotoImage(Image.fromarray(np.asarray(self.curCvImg)))
        self.curTkImgRes = self.curTkImg
        self.imgCanvas.itemconfig(self.imgCanvasImg, image=self.curTkImg)
        self.clear_poly()
        self.clear_pt()
        self.ptsCp = self.pts


    def next_img(self):
        if self.curImgIdx+1 > self.totalImgNum:
            pass
        else:
            self.curImgIdx += 1
        self.update_img()
        self.update_disp_num()



    def pre_img(self):
        if self.curImgIdx-1 < 0:
            pass
        else:
            self.curImgIdx -= 1
        self.update_img()
        self.update_disp_num()

    def draw_poly(self):
        for i in range(0,9):
            self.canvasPoly.append(self.imgCanvas.create_rectangle(self.pts[i][0]-self.offset[i][0],self.pts[i][1]-self.offset[i][1],self.pts[i][0]+self.offset[i][0],self.pts[i][1]+self.offset[i][1],outline='green',width=3))

    def draw_polyCp(self):
        points = self.curImgPt
        # points = self.curImgPt
        #
        # if points.shape[0] >=2:
        #     tlist = []
        #     for lineIdx in range(points.shape[0]):
        #         # if points[lineIdx][0] == curColorMode:  # 查找对应的颜色
        #         tlist.append([int(points[lineIdx][1] * self.imgWidth), int(points[lineIdx][2] * self.imgHeight)])  # 提取一种颜色下的所有坐标并恢复原有尺度
        #     tlist = np.array(tlist)
        #
        #
        #
        #     ## 矩形区域
        #     top_point = tlist[0]
        #     bottom_point = tlist[1]
        # self.update_anchor()
        # for i in range(0,9):
        #     self.canvasPoly.append(self.imgCanvas.create_rectangle(self.ptsCp[i][0]-self.offsetCp[i][0],self.ptsCp[i][1]-self.offsetCp[i][1],self.ptsCp[i][0]+self.offsetCp[i][0],self.ptsCp[i][1]+self.offsetCp[i][1],outline='green',width=3))

    def update_anchor(self,x,y):
        # x = self.curImgPt[0][1] * self.imgWidth
        # y = self.curImgPt[0][2] * self.imgHeight
        x1 = x - self.offset[0][0]
        y1 = y - self.offset[0][1]
        x2 = x + self.offset[0][0]
        y2 = y + self.offset[0][1]
        self.canvasPoly.append(self.imgCanvas.create_rectangle(x1,y1,x2,y2, outline='green',width=3))
        poly = [[1, x1 / self.imgWidth, y1 / self.imgHeight, x2 / self.imgWidth,y2 / self.imgHeight]]  # 将矩形的四个点归一化

        poly = np.array(poly)
        # 保存生成的多边形和圆形的坐标信息
        # 多边形：[color_model,x,y,]
        np.savetxt(self.totalDirList[self.curImgIdx][2], poly)
        # 保存人点击鼠标左键的点

        np.save(self.totalDirList[self.curImgIdx][3], self.curImgPt)


    # def update_anchor(self):
    #     # [[-30, 90], [0, 0], [0, 0], [0, 0],
    #     # [-15, -50], [-30, -50], [176, 65], [175, 122], [266, 267]]
    #     x1 = self.curImgPt[0][1]*self.imgWidth
    #     y1 = self.curImgPt[0][2]*self.imgHeight
    #     x2 = self.curImgPt[1][1]*self.imgWidth
    #     y2 = self.curImgPt[1][2]*self.imgHeight
    #
    #     for i in range(0,2):
    #         self.ptsCp[i][0] = x1+self.glOffset[i][0]
    #         self.ptsCp[i][1] = y1+self.glOffset[i][1]
    #
    #     self.ptsCp[2][0] = int((x1+x2)/2)
    #     self.ptsCp[2][1] = int((y1+y2)/2)
    #
    #     for i in range(3,9):
    #         self.ptsCp[i][0] = x2 + self.glOffset[i][0]
    #         self.ptsCp[i][1] = y2 + self.glOffset[i][1]



    def onKeydown(self,event):
        if event.char == '1':
            self.labelMode = 1
        if event.char == '2':
            self.labelMode = 2
        if event.char == 'z':
            self.pre_img()
        if event.char == 'x':
            self.next_img()
        if event.char == 'c':
            self.clear_pt()
            self.curTkImgRes = self.curTkImg
            self.curCvImgCp = self.curCvImg
            self.curImgPt = np.empty((0, 3), np.float32)

            # 删除保存的txt和npy文件
            if os.path.isfile(self.totalDirList[self.curImgIdx][2]):
                os.remove(self.totalDirList[self.curImgIdx][2])
            if os.path.isfile(self.totalDirList[self.curImgIdx][3]):
                os.remove(self.totalDirList[self.curImgIdx][3])

        if event.char == 'v':
            # self.draw_poly()
            # self.draw_polyCp()
            self.update_anchor()
        if event.char == '/':
            self.window.destroy()
        if event.char == ' ':
            self.draw_poly()
            self.next_img()

    def onClickTest(self):
        self.update_img()
        self.curImgIdx +=1

    def onClick(self,event):
        x,y = event.x,event.y
        print(x,',',y)
        self.canvasPt.append(
            self.imgCanvas.create_oval(x - self.ptOffset, y - self.ptOffset, x + self.ptOffset, y + self.ptOffset,fill='red'))

        self.update_anchor(x,y)

        # self.curImgPt = np.concatenate([self.curImgPt, np.expand_dims(np.array([0, x / self.imgWidth, y / self.imgHeight]),0) ],0)

    def onScaleBarMove(self,event):
        self.scaleBar.set(int(event))
        self.curImgIdx=int(event)
        self.update_img()
        self.update_disp_num()

    def onMouseRightClick(self,event):
        self.draw_poly()
        self.next_img()

    def onMouseWheelMove(self,event):
        # self.clear_poly()
        # self.rotateAngle += event.delta/120
        # self.pt_rotate()
        # self.draw_polyCp()
        pass


    def clear_poly(self):
        if len(self.canvasPoly)>0:
            for poly in self.canvasPoly:
                self.imgCanvas.delete(poly)

    def pt_rotate(self):
        cx,cy = self.ptsCp[2]
        for i in range(0,9):
            self.ptsCp[i][0] = int((self.ptsCp[i][0] - cx) * math.cos(self.rotateAngle) + (self.ptsCp[i][1] - cy) * math.sin(self.rotateAngle) + cx)
            self.ptsCp[i][1] = int((self.ptsCp[i][1] - cy) * math.cos(self.rotateAngle) - (self.ptsCp[i][0] - cx) * math.sin(self.rotateAngle) + cy)


    def onMouseDrag(self,event):
        print(event.x,',',event.y)
        self.clear_poly()
        for i in range(0, 9):
            self.ptsCp[i][0] += (event.x - self.curImgPt[0][1]*self.imgWidth)*self.moveScale
            self.ptsCp[i][1] += (event.y - self.curImgPt[0][2]*self.imgHeight)*self.moveScale
