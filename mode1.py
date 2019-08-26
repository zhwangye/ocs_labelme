# coding:utf-8
import cv2
import os
import numpy as np
import tkinter as tk
from PIL import Image,ImageTk
"""
模式一
点击两点确定上下端螺丝的位置，从而计算出其他零件的位置
"""
class Mode1:
    def __init__(self,window,imgPath,txtPath,ptPath):
        self.window = window
        self.COLOR_MAP = [[0, 255, 0], [0, 0, 255], [255, 0, 0]]
        self.RECT_COLOR_MAP = [[0, 255, 0], [0, 0, 255], [255, 0, 0],[255, 255, 0]]
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
            self.totalDirList.append([name,imgPath+imgName,txtPath+name+'.txt',ptPath+name+'.npy'])

        # 记录图片数量，从零开始
        self.totalImgNum = len(self.totalDirList)-1

        self.imgWidth = 800
        self.imgHeight = 800
        try:
            if self.totalImgNum == 0:
                raise Exception('This path has no images!',1)
        except Exception:
            print('Error')

        # 初始化显示背景图
        im = cv2.imread(self.totalDirList[self.curImgIdx][1], 0)
        im = cv2.resize(im, (self.imgWidth, self.imgHeight), cv2.INTER_CUBIC)
        img = cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
        self.curCvImg = img
        self.curCvImgCp = img.copy()

        # 窗口添加鼠标，键盘监听
        self.window.bind('<Key>', self.onKeydown)
        self.window.bind('<MouseWheel>',self.onMouseWheelMove)
        self.window.focus_set()  # 当前框架被选中，意思是键盘触发，只对这个框架有效

        # 创建主面板
        self.mainFrm = tk.Frame(self.window,width=1920,height=820)
        self.mainFrm.place(x=0,y=0,anchor='nw')

        self.topFrm = tk.Frame(self.mainFrm, width=1920, height=800)
        self.topFrm.place(x=0,y=0,anchor='nw')
        # self.btmFrm = tk.Frame(self.mainFrm, width=1920, height=280)
        # self.btmFrm.place(x=0,y=800,anchor='nw')

        # 创建左侧图像、右侧图像、信息面板、工具面板
        self.leftImgFrm = tk.Frame(self.topFrm, width=self.imgWidth+6, height=self.imgHeight+6)
        self.leftImgFrm.place(x=0,y=0,anchor='nw')
        self.rightImgFrm = tk.Frame(self.topFrm, width=self.imgWidth+6, height=self.imgHeight+6)
        self.rightImgFrm.place(x=810,y=0,anchor='nw')
        self.infoFrm = tk.Frame(self.topFrm, width=250, height=800)
        self.infoFrm.place(x=1624,y=0,anchor='nw')
        # self.toolFrm = tk.Frame(self.btmFrm, width=1920, height=280)
        # self.toolFrm.place(x=0,y=0,anchor='nw')

        # 记录当前点
        self.canvasPt = []
        # 记录当前多边形
        self.canvasPoly = []
        # 创建左侧画布，用于显示原图和在该图上进行打标
        self.leftImgCanvas = tk.Canvas(self.leftImgFrm, height=self.imgHeight, width=self.imgWidth)
        self.leftImgCanvas.bind(sequence='<Button-1>',func=self.onClick)
        self.leftImgCanvas.bind(sequence='<Button-3>',func=self.onMouseRightClick)
        self.leftImgCanvas.place(x=400+6, y=400+3, anchor='center')
        # 创建右侧画布，用于显示标注结果
        self.rightImgCanvas = tk.Canvas(self.rightImgFrm, height=self.imgHeight, width=self.imgWidth)
        self.rightImgCanvas.place(x=400-6, y=400+3, anchor='center')
        # 显示图片初始化
        self.curTkImg = ImageTk.PhotoImage(Image.fromarray(np.asarray(self.curCvImg)))
        self.curTkImgRes = self.curTkImg

        self.leftCanvasImg = self.leftImgCanvas.create_image(400+3, 400+3, anchor='center', image=self.curTkImg)
        self.rightCanvasImg = self.rightImgCanvas.create_image(400+3, 400+3, anchor='center', image=self.curTkImgRes)

        ## info 面板内容
        # 当前图片index/图片总数
        self.numFrm = tk.Frame(self.infoFrm, width=220, height=100)
        self.numFrm.place(x=0, y=0, anchor='nw')
        self.imgNumLbl = tk.Label(self.numFrm, text=str(self.curImgIdx) + ' / ' + str(self.totalImgNum),
                                  bg='white',font=('Arial', 12), justify='center', width=320, height=2)
        self.imgNumLbl.place(x=115, y=50, anchor='center')

        # 滑动定位条
        self.scaleBar = tk.Scale(self.infoFrm, from_=0, to=self.totalImgNum, orient=tk.HORIZONTAL, length=220,
                                 showvalue=0,tickinterval=int(self.totalImgNum/5), resolution=1,command=self.onScaleBarMove)
        self.scaleBar.place(x=0, y=100, anchor='nw')

        # self.btn = tk.Button(self.infoFrm, text="Change", command=self.onClickTest)
        # self.btn.pack(side='top')

        self.window.mainloop()


    def pil2cv(self,img):
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_GRAY2BGR)

    def cv2pil(self,img):
        return Image.fromarray(np.asarray(img))

    # 更新当前/总数label
    def update_disp_num(self):
        info = str(self.curImgIdx)+' / '+str(self.totalImgNum)
        self.imgNumLbl.config(text=info)
        self.imgNumLbl.update()

    # 清空左canvas片中的点和右侧canvas中的polygon
    def clear_pt(self):
        for pt in self.canvasPt:
            self.leftImgCanvas.delete(pt)
            self.rightImgCanvas.delete(pt)
        for poly in self.canvasPoly:
            self.rightImgCanvas.delete(poly)
        self.canvasPt=[]
        self.canvasPoly=[]
        self.curImgPt = np.empty((0,3),np.float32)

    # 加载本地存储的坐标点
    def load_pts(self):
        if os.path.isfile(self.totalDirList[self.curImgIdx][3]):
            localPts = np.load(self.totalDirList[self.curImgIdx][3])
            self.curImgPt = np.concatenate([self.curImgPt,localPts],0)

    # 在左侧canvas画出本地保存的点，右侧canvas画出polygon
    def update_lpts_poly(self):
        if self.curImgPt.size!=0:
            for axy in self.curImgPt:
                self.canvasPt.append(self.leftImgCanvas.create_oval(axy[1]*self.imgWidth - self.ptOffset, axy[2]*self.imgHeight - self.ptOffset, axy[1]*self.imgWidth + self.ptOffset,axy[2]*self.imgHeight + self.ptOffset, fill='red'))
            self.draw_poly()

    def create_right_canvas_pts(self):
        if self.curImgPt.size!=0:
            for axy in self.curImgPt:
                self.canvasPt.append(self.rightImgCanvas.create_oval(axy[1]*self.imgWidth - self.ptOffset, axy[2]*self.imgHeight - self.ptOffset, axy[1]*self.imgWidth + self.ptOffset,axy[2]*self.imgHeight + self.ptOffset, fill='red'))


    # 更新左侧canvas和右侧canvas图片
    def update_img(self):
        self.clear_pt()
        self.load_pts()
        self.scaleBar.set(self.curImgIdx)
        im = cv2.imread(self.totalDirList[self.curImgIdx][1],0)
        im = cv2.resize(im, (self.imgWidth, self.imgHeight), cv2.INTER_CUBIC)
        self.curCvImg = cv2.cvtColor(im,cv2.COLOR_GRAY2BGR)
        self.curCvImgCp = self.curCvImg.copy()
        self.curTkImg = ImageTk.PhotoImage(Image.fromarray(np.asarray(self.curCvImg)))
        self.curTkImgRes = self.curTkImg
        self.leftImgCanvas.itemconfig(self.leftCanvasImg, image=self.curTkImg)
        self.rightImgCanvas.itemconfig(self.rightCanvasImg, image=self.curTkImgRes)
        self.update_lpts_poly()


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
        points = self.curImgPt
        self.create_right_canvas_pts()
        if points.shape[0] >= 2:
            poly = []
            tlist = []

            # for curColorMode in range(self.COLOR_CLASS):
                # 将每种颜色的坐标存放在一个list中
            for lineIdx in range(points.shape[0]):
                # if points[lineIdx][0] == curColorMode:  # 查找对应的颜色
                tlist.append([int(points[lineIdx][1] * self.imgWidth), int(points[lineIdx][2] * self.imgHeight)])  # 提取一种颜色下的所有坐标并恢复原有尺度
            tlist = np.array(tlist)

            ## 矩形区域
            top_point = tlist[0]
            bottom_point = tlist[1]
            x_offset = 20
            y_offset = 0
            y_diff = bottom_point[1] - top_point[1]
            offset_points = [[top_point[0] - x_offset, top_point[1] + y_offset],
                             [top_point[0] + x_offset, top_point[1] + y_offset],
                             [bottom_point[0] - x_offset, bottom_point[1] - y_offset],
                             [bottom_point[0] + x_offset, bottom_point[1] - y_offset]]
            offset_points = np.asarray(offset_points)
            rect = cv2.minAreaRect(offset_points)  # 计算包含点组成区域的最小矩形 return: [[x1,y1],[x2,y2],rotated_angel]
            box = cv2.boxPoints(rect)  # Finds the four vertices of a rotated rect
            pts = box.reshape((-1, 1, 2))
            pts = np.int32(pts)
            cv2.polylines(self.curCvImgCp, [pts], True, self.RECT_COLOR_MAP[3])  # 画多边形

            ## 画圆
            if y_diff <= 320:
                r1 = int(y_diff * (1.3 / 9))
                r2 = int(y_diff * (1.8 / 9))
            elif y_diff >= 420:
                r1 = int(y_diff * (0.8 / 9))
                r2 = int(y_diff * (1.2 / 9))
            else:
                r1 = int(y_diff * (1.1 / 9))
                r2 = int(y_diff * (1.6 / 9))

            r1_xoffset = 0
            r2_soffset = 0

            if self.labelMode == 1:
                # 正常
                r1_xoffset = 0
                r2_soffset = 0
            elif self.labelMode == 2:
                # 倾斜
                r1_xoffset = 18
                r2_soffset = -25
            else:
                pass

            center_r1 = [top_point[0] + r1_xoffset, top_point[1]]
            center_r2 = [bottom_point[0] + r2_soffset, bottom_point[1]]

            cv2.circle(self.curCvImgCp, tuple(center_r1), r1, self.RECT_COLOR_MAP[2])
            cv2.circle(self.curCvImgCp, tuple(center_r2), r2, self.RECT_COLOR_MAP[0])
            self.curCvImgCp = cv2.cvtColor(self.curCvImgCp,cv2.COLOR_BGR2RGB)
            self.curTkImgRes = ImageTk.PhotoImage(Image.fromarray(np.asarray(self.curCvImgCp)))
            self.canvasPoly.append(self.rightImgCanvas.itemconfig(self.rightCanvasImg, image=self.curTkImgRes))

            poly.append([1, top_point[0] / self.imgWidth, top_point[1] / self.imgHeight, r1 * 2 / self.imgWidth, r1 * 2 / self.imgHeight,0])  # 将圆形r1的三个点归一化
            poly.append([2, bottom_point[0] / self.imgWidth, bottom_point[1] / self.imgHeight, r2 * 2 / self.imgWidth, r2 * 2 / self.imgHeight,0])  # 将圆形r1的三个点归一化
            poly.append([3, rect[0][0] / self.imgWidth, rect[0][1] / self.imgHeight, rect[1][0] / self.imgWidth,rect[1][1] / self.imgHeight, rect[2]])  # 将矩形的四个点归一化

            poly = np.array(poly)
            # 保存生成的多边形和圆形的坐标信息
            # 多边形：[color_model,x,y,]
            np.savetxt(self.totalDirList[self.curImgIdx][2], poly)
        # 保存人点击鼠标左键的点
        np.save(self.totalDirList[self.curImgIdx][3], self.curImgPt)


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
            self.rightImgCanvas.itemconfig(self.rightCanvasImg, image=self.curTkImgRes)
            self.curImgPt = np.empty((0, 3), np.float32)

            # 删除保存的txt和npy文件
            if os.path.isfile(self.totalDirList[self.curImgIdx][2]):
                os.remove(self.totalDirList[self.curImgIdx][2])
            if os.path.isfile(self.totalDirList[self.curImgIdx][3]):
                os.remove(self.totalDirList[self.curImgIdx][3])

        if event.char == 'v':
            self.draw_poly()
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
        self.canvasPt.append(self.leftImgCanvas.create_oval(x-self.ptOffset,y-self.ptOffset,x+self.ptOffset,y+self.ptOffset,fill='red'))
        self.curImgPt = np.concatenate([self.curImgPt, np.expand_dims(np.array([0, x / self.imgWidth, y / self.imgHeight]),0) ],0)

    def onScaleBarMove(self,event):
        self.scaleBar.set(int(event))
        self.curImgIdx=int(event)
        self.update_img()
        self.update_disp_num()

    def onMouseRightClick(self,event):
        self.draw_poly()
        self.next_img()

    def onMouseWheelMove(self,event):
        if event.delta > 0:
            self.pre_img()
        else:
            self.next_img()