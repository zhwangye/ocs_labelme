# coding:utf-8
import tkinter as tk
import mode1
import mode2
import menuHelpAbout

"""
铁路吊弦检测标注工具
"""


class MainWindow:
    def __init__(self,imgPath,txtPath,ptPath):
        self.window = tk.Tk()
        self.window.title('打标程序V1.0')

        # 指定窗口大小
        screenwidth = self.window.winfo_screenwidth() - 50
        screenheight = self.window.winfo_screenheight() - 274
        self.window.geometry('%dx%d' % (screenwidth, screenheight))

        # 定义菜单栏
        self.menuBar = tk.Menu(self.window)
        self.window.config(menu=self.menuBar)

        # File菜单
        self.fileMenu = tk.Menu(self.menuBar,tearoff=0)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="open", command=self.onFileOpen)
        self.fileMenu.add_command(label="close", command=self.onFileClose)

        # Tool菜单
        self.toolMenu = tk.Menu(self.menuBar,tearoff=0)
        self.menuBar.add_cascade(label="Tool", menu=self.toolMenu)
        self.toolMenu.add_command(label="Mode1", command=self.onToolMode1)
        self.toolMenu.add_command(label="Mode2", command=self.onToolMode2)

        # Help菜单
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About", command=self.onHelpAbout)

    def onHelpAbout(self):
        menuHelpAbout.onMenuItem_About()

    def onFileOpen(self):
        pass

    def onToolMode1(self):
        self.window.update()
        mode1_inst = mode1.Mode1(self.window,imgPath,txtPath,ptPath)

    def onToolMode2(self):
        self.window.update()
        mode2_inst = mode2.Mode2(self.window, imgPath, txtPath, ptPath)

    def onFileClose(self):
        pass


if __name__ == "__main__":
    imgPath = './img/'
    txtPath = './txt/'
    ptPath = './point/'
    mainFrame = MainWindow(imgPath,txtPath,ptPath)
    mainFrame.window.mainloop()