# -*- coding:utf-8 -*-
from __future__ import division
from genericpath import isfile
import glob
import os
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
# import tkinter as tk  
import natsort
img_index_w = 1
img_index_h = 1


def drawCircle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, width=0, **kwargs)

def resize(w, h, w_box, h_box, pil_image):
    """
    resize a pil_image object so it will fit into 
    a box of size w_box times h_box, but retain aspect ratio 
    对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例 
    """
    f1 = w_box/w
    f2 = h_box/h  
    factor = min(f1,f2)
    width  = int(w*factor)  
    height = int(h*factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)  
  



class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("keypoint Annotation Tool 4.0.1")
        # self.parent.geometry("1000x500")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=TRUE, height=TRUE)

        # 图片大小
        
        self.COLORS = ['blue', 'cyan', 'green', 'deepskyblue','deeppink','fuchsia','yellow','lawngreen',
                       'Salmon','white', '#6B8E23']

        # initialize global state
        self.imageDir = ''  # 图片所在文件夹
        self.imageList = []

        self.outDir = ''  # 输出文件夹

        self.cur = 0
        self.total = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # reference to bbox
        self.pointIdList = []
        self.pointId = None
        self.pointList = []

        # ----------------- GUI 部件 ---------------------
        # dir entry & load
        self.label1 = Label(self.frame, text="图像目录:")
        self.label1.grid(row=0, column=1, sticky=E+W)

        self.label2 = Label(self.frame, text="保存目录:")
        self.label2.grid(row=1, column=1, sticky=E+W)

        self.btn1 = Button(self.frame, text="选择文件夹",
                           command=self.get_image_dir)
        self.btn1.grid(row=0, column=2, sticky=E+W)

        self.btn2 = Button(self.frame, text="选择文件夹",
                           command=self.get_save_dir)
        self.btn2.grid(row=1, column=2, sticky=E+W)

        self.lbs_w = Label(self.frame, text='width')
        self.entry_w = Entry(self.frame)

        self.lbs_w.grid(row=2, column=1, sticky=E+W)
        self.entry_w.grid(row=2, column=2, sticky=E+W)

        self.lbs_h = Label(self.frame, text='height')
        self.entry_h = Entry(self.frame)

        self.lbs_h.grid(row=3, column=1, sticky=E+W)
        self.entry_h.grid(row=3, column=2, sticky=E+W)

        self.ldBtn = Button(self.frame, text="开始加载", command=self.loadDir)
        self.ldBtn.grid(row=4, column=1, columnspan=2, sticky=N+E+W)
 
        # main panel for labeling
        self.mainPanel = Canvas(self.frame, bg='lightgray')

        # 鼠标左键点击
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.grid(row=0, column=0, rowspan=13, sticky=W+N+S+E)

        # 快捷键
        self.parent.bind("<Control-s>", self.saveAll)    # press 'Ctrl + s' to save
        self.parent.bind("<Control-Up>", self.prevImage)  # press 'Ctrl + up' to go backforward
        self.parent.bind("<Control-Down>", self.nextImage)  # press 'Ctrl + down' to go forward
        

        self.label_challenges = Label(self.frame, text="可见光图像请选择当前帧挑战类型,可多选:", bg="lightgrey", fg="black")
        self.label_challenges.grid(row=9, column=1,columnspan=2, sticky=E+W)

        self.challenges = {0: "常规挑战:NC", 1: "低光照:LI", 2: "低纹理:LT", 3: "运动模糊:MB", 4: "云雾天气:CF"}
        # 这里负责给予字典的键一个False或者True的值，用于检测是否被勾选
        self.cheakboxs = {}
        for i in range(len(self.challenges)):
            # 这里相当于是{0: False, 1: False, 2: False, 3: False, 4: False}
            self.cheakboxs[i] = BooleanVar()
            # 只有被勾选才变为True
            if i < 2:
                Checkbutton(self.frame, text=self.challenges[i], variable=self.cheakboxs[i],padx=8,pady=1).grid(row=10, column=i+1,rowspan = 1,sticky=N+W)
            if i < 4 and i >=2:
                Checkbutton(self.frame, text=self.challenges[i], variable=self.cheakboxs[i],padx=9,pady=1).grid(row=11, column=i-1,rowspan = 1,sticky=N+W)
            if i == 4:
                Checkbutton(self.frame, text=self.challenges[i], variable=self.cheakboxs[i],padx=10,pady=1).grid(row=12, column=i-3,rowspan = 1,sticky=N+W)


        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='关键点坐标:')
        self.lb1.grid(row=5, column=1, columnspan=2, sticky=N+E+W)

        self.listbox = Listbox(self.frame)  # , width=30, height=15)
        self.listbox.grid(row=6, column=1, columnspan=2, sticky=N+S+E+W)

        self.btnDel = Button(self.frame, text='删除', command=self.delBBox)
        self.btnDel.grid(row=7, column=1, columnspan=2, sticky=S+E+W)
        self.btnClear = Button(
            self.frame, text='清空', command=self.clearBBox)
        self.btnClear.grid(row=8, column=1, columnspan=2, sticky=N+E+W)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=13, column=0, columnspan=5, sticky=E+W+S)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev',
                              width=10, command=self.prevImage)
        # self.prevBtn.grid(row=13, column=1, columnspan=1, sticky=E+W+S)
        self.prevBtn.pack(side=LEFT, padx=7, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>',
                              width=10, command=self.nextImage)
        # self.nextBtn.grid(row=13, column=2, columnspan=1, sticky=E+W+S)                 
        self.nextBtn.pack(side=LEFT, padx=7, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        # self.progLabel.grid(row=13, column=3, columnspan=1, sticky=E+W+S)
        self.progLabel.pack(side=LEFT, padx=7)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        # self.tmpLabel.grid(row=13, column=4, columnspan=1, sticky=E+W+S)
        self.tmpLabel.pack(side=LEFT, padx=7)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        # self.idxEntry.grid(row=13, column=5, columnspan=1, sticky=E+W+S)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)

        self.goBtn.pack(side=LEFT,padx=5)
        self.img_name = Label(self.ctrPanel, text = '  ' )
        self.img_name.pack(side=LEFT,padx=5)

        self.Searchspace = Label(self.ctrPanel, text = '  ' )
        self.Searchspace.pack(side=LEFT,padx=5)
        self.SearchEntry = Entry(self.ctrPanel, width=15)
        # self.idxEntry.grid(row=13, column=5, columnspan=1, sticky=E+W+S)
        self.SearchEntry.pack(side=LEFT)
        self.SearchBtn = Button(self.ctrPanel, text='Search', command=self.SearchImage)
        self.SearchBtn.pack(side=LEFT,padx=5)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(0, weight=30)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(6, weight=1)

        # menu
        self.menubar = Menu(self.parent)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='帮助', menu=self.helpmenu)

        self.helpmenu.add_command(label='使用说明', command=self.usage)
        self.helpmenu.add_command(label='关于软件', command=self.about)

        # for debugging
        # self.loadDir()
        self.parent.config(menu=self.menubar)
    
    def usage(self):
        messagebox.showinfo(
            title='使用说明', message="1. 选择图片所在路径\n2. 选择保存路径\n3.设置保存图片大小(如果不设置就按照默认图片默认分辨率计算)\n"
                                +"4. 点击开始加载\n5.Ctrl + down 下一张并保存 \n6.Ctrl + down 下一张并保存\n7.Ctrl + s 保存当前标注\n7.热红外图像不用标注挑战信息")

    def about(self):
        messagebox.showinfo(title='关于软件', message="源作者:pprp 当前版本:ahucs_lf 版权所有 请勿商业使用\n地址: https://github.com/pprp\n博客:https://blog.csdn.net/DD_PP_JJ")

    def get_image_dir(self):
        self.imageDir = askdirectory()
        print(self.imageDir)

    def get_save_dir(self):
        self.outDir = askdirectory()
        print(self.outDir)

    def loadDir(self):
        # for debug
        # self.imageDir = "./data/images"
        # self.outDir = "./data/labels"

        # 读取并设置图片大小
        # self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.imageList = os.listdir(self.imageDir)
        self.imageList = natsort.natsorted(self.imageList)
        if len(self.imageList) == 0:

            messagebox.showwarning(
                title='警告', message="文件夹内为空")
            return
        else:
            for img_order in range(0,len(self.imageList)):
                if not '.jpg' in self.imageList[img_order]:
                    messagebox.showerror(title='错误',message='选择的文件夹内没有jpg文件,请重新选择!')
                    return
            print("num=%d" % (len(self.imageList)))

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.imagepath = os.path.join(self.imageDir,self.imageList[self.cur - 1])
        pil_image = Image.open(self.imagepath)
        # get the size of the image
        # 获取图像的原始大小
        w0, h0 = pil_image.size
        if  self.entry_h.get()!= '' and self.entry_w.get()!= '':
            self.img_h = int(self.entry_h.get())
            self.img_w = int(self.entry_w.get())
        else:
            messagebox.showwarning(
            title='警告', message="不输入尺寸则默认为读入图像大小")
            self.img_h = h0
            self.img_w = w0

        self.loadImage()
        print("image shape: (%d, %d)" % (self.img_w, self.img_h))
        print('%d images loaded from %s' % (self.total, self.imageDir))

    def m_resize(self,w_box, h_box, img_w, img_h, pil_image): # 参数是：要适应的窗口宽、高、Image.open后的图片
         # 获取图像的原始大小
        f1 = 1.0 * w_box / img_w
        f2 = 1.0 * h_box / img_h
        factor = min([f1, f2])
        w2 = int(img_w * factor)
        h2 = int(img_h * factor)
        pil_image.resize((w2, h2))
        #return pil_image.scaled(w2, h2)

    def loadImage(self):
        # load image
        self.imagepath = os.path.join(self.imageDir,self.imageList[self.cur - 1])
        print(self.imageList)
        pil_image = Image.open(self.imagepath)
        # get the size of the image
        # 获取图像的原始大小
        self.w0, self.h0 = pil_image.size
        self.m_resize(win_w,win_h,self.w0,self.h0,pil_image)
        global img_index_w,img_index_h
        img_index_w = self.img_w/self.w0
        img_index_h = self.img_h/self.h0
        # 缩放到指定大小
        pil_image = pil_image.resize(
            (self.img_w, self.img_h), Image.ANTIALIAS)

        #pil_image = imgresize(w, h, w_box, h_box, pil_image)
        
        # pil_image = pil_image.convert('L')
        self.img = pil_image

        self.tkimg = ImageTk.PhotoImage(pil_image)

        #self.mainPanel.config(width=self.img_w, height=self.img_h)
        self.mainPanel.config(width=max(self.tkimg.width(), self.img_w),height=max(self.tkimg.height(), self.img_h))
        self.mainPanel.create_image(
            self.img_w//2, self.img_h//2, image=self.tkimg, anchor=CENTER)

        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))
        self.img_name.config(text= '\t\t'+ self.imageDir.split('/')[-2] +' : '+self.imagepath.split('\\')[-1])
        # load labels
        self.clear()
        self.imagename = os.path.split(self.imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        print('/'.join(self.imageDir.split('/')[:-1]))
        self.challenges_text_path = os.path.join('/'.join(self.imageDir.split('/')[:-1]),'Challenge_Attributes.txt')
        print(self.challenges_text_path)
        bbox_cnt = 0
        self.read_challenges_text()
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    # if i == 0:
                    #     bbox_cnt = int(line.strip())
                    #     continue
                    tmp = [(t.strip()) for t in line.split()]

                    #print("*********loadimage***********")
                    # print("tmp[0,1]===%d, %d" %('{:.4f}'.format(float(tmp[0])), '{:.4f}'.format(float(tmp[1]))))

                    # 类似鼠标事件
                    self.pointList.append((tmp[0], tmp[1]))
                    self.pointIdList.append(self.pointId)
                    self.pointId = None
                    self.listbox.insert(
                        END, '%d:(%s, %s)' % (len(self.pointIdList), '{:.4f}'.format(float(tmp[0])), '{:.4f}'.format(float(tmp[1]))))
                    self.listbox.itemconfig(
                        len(self.pointIdList) - 1, fg=self.COLORS[(len(self.pointIdList) - 1) % len(self.COLORS)])
                    drawCircle(self.mainPanel, float('{:4f}'.format(float(tmp[0])*img_index_w)), float('{:4f}'.format(float(tmp[1])*img_index_h)), 2, fill=self.COLORS[(
                        len(self.pointIdList) - 1) % len(self.COLORS)])


                    tmp[0] = '{:4f}'.format(float(tmp[0]))
                    tmp[1] = '{:4f}'.format(float(tmp[1]))

                    # tx0 = int(tmp[0]*self.img_w)
                    # ty0 = int(tmp[1]*self.img_h)
        return self.w0,self.h0
    
    def saveImage(self):
        # print "-----1--self.pointList---------"
        print("Save File Length: %d" % len(self.pointList))
        # print "-----2--self.pointList---------"

        if self.labelfilename == '':
            print("labelfilename is empty")
            return
        self.SaveChallenges()
        if 'Z' in self.imagename and not self.is_challenges_bz:
            return
        with open(self.labelfilename, 'w') as f:
            #f.write('%d\n' % len(self.pointList))
            for bbox in self.pointList:
                print('bbox ' ,bbox)

                new_point_line_str = '{:.4f}'.format(float(bbox[0])) + ' ' +'{:.4f}'.format(float(bbox[1]))+ '\n'
                f.write(new_point_line_str)
        print('Image No. %d saved' % (self.cur))


    def read_challenges_text(self):
        # if not os.path.exists(self.challenges_text_path):
        #     messagebox.showwarning(title='警告',message='没有找到 Challenge_Attributes.txt')
        self.challenges_text_list = []  
        self.challenges_img_list= []
        if  os.path.exists(self.challenges_text_path):
            with open(self.challenges_text_path,'r') as f:
                for line in f.readlines():

                    print('line',line)
                    if line == '\n':
                        break
                    self.challenges_img_list.append(line.strip('\n').split(':')[0])
                    self.challenges_text_list.append({line.strip('\n').split(':')[0]:line.strip('\n').split(':')[1].split(' ')})

                    if line.strip('\n').split(':')[0] == self.imagename+'.jpg':
                        chg_list = []
                        print('line',line)
                        read_chg_list = line.strip('\n').split(':')[1].split(' ')[:-1]
                        for chg_order in range(0,len(self.challenges)):
                            chg_list.append(self.challenges[chg_order].split(':')[-1])
                        print('chg_list',chg_list)
                        for i in range(len(self.challenges)):
                            self.cheakboxs[i].set(False)
                        for i in range(len(self.challenges)):
                            if chg_list[i] in read_chg_list:
                                self.cheakboxs[i].set(True)
                        print('read_chg_list',read_chg_list)
                if self.imagename+'.jpg' not in self.challenges_img_list:
                    for i in range(len(self.challenges)):
                        self.cheakboxs[i].set(False)

            self.challenges_text_list = natsort.natsorted(self.challenges_text_list)
            for challenges_text_order in range(0,len(self.challenges_text_list)):
                
                if self.imagename in self.challenges_text_list[challenges_text_order]:
                    self.challenges_text_list[challenges_text_order][self.imagename].split(' ')
                    for i in range(len(self.challenges)):
                    # 这里相当于是{0: False, 1: False, 2: False, 3: False, 4: False}
                        self.cheakboxs[i].set(True)


    def SaveChallenges(self):
        challenges_text = ''
        for j in self.cheakboxs:
        # 这里实际上是cheakboxs[j].get() == True
        # 如果被勾选的话传回来的值为True
        # 如果没有被勾选的话传回来的值为False
            if self.cheakboxs[j].get():
                challenges_text = challenges_text +self.challenges[j].split(':')[-1] + " "

        if 'T' in self.imagepath.split('\\')[-1] and len(challenges_text.replace(' ','')) != 0:
            messagebox.showwarning(
                title='警告', message="infrared图像挑战属性不需要标注\n不保存挑战信息")
        if 'Z' in self.imagepath.split('\\')[-1]:

            self.is_challenges_bz = True
            if not self.pre_flag:
                if len(challenges_text.replace(' ','')) == 0:
                    messagebox.showwarning(
                    title='警告', message="挑战属性没有标注")
                    self.is_challenges_bz = False
            chanlleges_dic = {}
            if os.path.isfile(self.challenges_text_path):
                with open (self.challenges_text_path,'r') as f:
                    for line in f.readlines():
                        if line == '\n':
                            print('line是空行')
                            break
                        line = line.strip('\n')
                        print('line',line)

                        line_key = line.split(':')[0]
                        line_value = line.split(':')[1]
                        chanlleges_dic[line_key] = line_value
            chanlleges_new_dic = {}
            chanlleges_new_dic[self.imagepath.split('\\')[-1]] = challenges_text
            chanlleges_dic.update(chanlleges_new_dic)
            # print(len(chanlleges_dic))
            # chanlleges_dic = natsort.natsorted(chanlleges_dic)
            print('challenges_text',challenges_text)
            print('len(challenges_text.split(' '))',len(challenges_text.split(' ')))
            if 'NC' in challenges_text and len(challenges_text.split(' '))-1 > 1:
                messagebox.showwarning(title='警告',message='当前标注挑战与常规挑战NC冲突,请不要勾选NC挑战')
                self.is_challenges_bz = False
            with open(self.challenges_text_path,'w') as f:
                for dic_item in chanlleges_dic.items():
                    f.write(str(dic_item[0]).replace('T','Z')+':'+str(dic_item[1]) + '\n')
        

    def saveAll(self, event=None):
        with open(self.labelfilename, 'w') as f:
            #f.write('%d\n' % len(self.pointList))
            for bbox in self.pointList:
                f.write(' '.join(map(str, bbox)) + '\n')

        self.SaveChallenges()
        if 'Z' in self.imagename and not self.is_challenges_bz:
            return
        print('Image No. %d \'s label saved' % (self.cur))
        # messagebox.showwarning(
        #     title='保存', message="保存对应关键点以及挑战信息成功")

    def mouseClick(self, event):
        x1, y1 = event.x, event.y
        # x1 = int(x1)
        # y1 = int(y1)
        print(x1,y1)
        # print(img_index_w)
        # print(img_index_h)
        ##################画点的坐标点位置################    
        # x2 = float(x1*img_index_w)
        # y2 = float(y1*img_index_h)        
        ################################################
        #print(img_index_w,img_index_h)
        # print(self.entry_w.get())
        if self.entry_w.get() and self.entry_h.get():
            x2 = float(format(x1/float(self.entry_w.get())*self.w0,'.4f'))
            y2 = float(format(y1/float(self.entry_h.get())*self.h0,'.4f'))
        else:
            x2 = float(format(x1,'.4f'))
            y2 = float(format(y1,'.4f'))
        print(f'x2 {x1}y2 {y2}')
        self.pointList.append((x2, y2))
        self.pointIdList.append(self.pointId)
        self.pointId = None


        
        self.listbox.insert(END, '%d:(%s, %s)' %
                            (len(self.pointIdList), '{:.4f}'.format(x2), '{:.4f}'.format(y2)))
        print('click mouse')
        print(len(self.pointList), self.COLORS[(
            len(self.pointIdList) - 1) % len(self.COLORS)])
        self.listbox.itemconfig(
            len(self.pointIdList) - 1, fg=self.COLORS[(len(self.pointIdList) - 1) % len(self.COLORS)])
        drawCircle(self.mainPanel, x1, y1, 2, fill=self.COLORS[(
            len(self.pointIdList) - 1) % len(self.COLORS)])#####draw point
        # cv.putText(self.mainPanel, str(len(self.pointIdList) - 1), (x1,y1), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 1)

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.pointIdList[idx])
        self.pointIdList.pop(idx)
        self.pointList.pop(idx)
        self.listbox.delete(idx)
        # print('self.pointIdList',self.pointIdList)
        # print('self.pointList',self.pointList)
        # print('self.listbox',self.listbox)
        # for i in range(0,len(self.pointList)):
        #     print('int(self.pointList[i][0]), int(self.pointList[i][1])',int(self.pointList[i][0]), int(self.pointList[i][1]))
        #     drawCircle(self.mainPanel, int(self.pointList[i][0]), int(self.pointList[i][1]), 2, fill=self.COLORS[(
        #     len(self.pointIdList) - 1) % len(self.COLORS)])

        self.pre_flag = True
        self.saveImage()
        self.loadImage()

    def clearBBox(self):
        for idx in range(len(self.pointIdList)):
            self.mainPanel.delete(self.pointIdList[idx])
        self.listbox.delete(0, len(self.pointList))
        self.pointIdList = []
        self.pointList = []
        self.pre_flag = True
        self.saveImage()
        self.loadImage()
    
    def clear(self):
        for idx in range(len(self.pointIdList)):
            self.mainPanel.delete(self.pointIdList[idx])
        self.listbox.delete(0, len(self.pointList))
        self.pointIdList = []
        self.pointList = []

    def prevImage(self, event=None):
        self.pre_flag = True
        self.saveImage()
        if 'Z' in self.imagename and not self.is_challenges_bz:
            return
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        self.pre_flag = False
        self.saveImage()
        if 'Z' in self.imagename and not self.is_challenges_bz:
            return
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()
            messagebox.showwarning(
            title='保存', message="保存对应关键点以及挑战信息成功")
        else:
            self.loadImage()
            messagebox.showwarning(
            title='警告', message="已经是最后一张了")

        
    def gotoImage(self):
        self.pre_flag = True
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            if 'Z' in self.imagename and not self.is_challenges_bz:
                return
            self.cur = idx
            self.loadImage()
        else:
            messagebox.showwarning(
            title='警告', message="跳跃位置错误，请重新输入")

    def SearchImage(self):
        self.pre_flag = True
        Searchname = self.SearchEntry.get()
        if Searchname in os.listdir(self.imageDir):
            self.saveImage()
            if 'Z' in self.imagename and not self.is_challenges_bz:
                return
            self.cur = os.listdir(self.imageDir).index(Searchname)+ 1
            self.loadImage()
        else:
            messagebox.showwarning(
            title='警告', message="搜索输入错误，请重新输入")

    def imgresize(self, w, h, w_box, h_box, pil_image):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        '''
        f1 = 1.0*w_box/w  # 1.0 forces float division in Python2
        f2 = 1.0*h_box/h
        factor = min([f1, f2])
        # use best down-sizing filter
        width = int(w*factor)
        height = int(h*factor)
        return pil_image.resize((width, height), Image.ANTIALIAS)


if __name__ == '__main__':
    
    
    #*****************************************************
    # open_icon = open("./points.ico","rb")
    # b64str = base64.b64encode(open_icon.read())
    # icon = b64str
    # icondata= base64.b64decode(icon)
    # ## The temp file is icon.ico
    # tempFile= "icon.ico"
    # iconfile= open(tempFile,"wb")
    # ## Extract the icon
    # iconfile.write(icondata)
    # iconfile.close()
    root = Tk()
    # root.wm_iconbitmap(tempFile)
    # # Delete the tempfile
    # os.remove(tempFile)
    # root.iconbitmap('./points.ico')
    tool = LabelTool(root)
    win_w = root.winfo_screenwidth()
    win_h = root.winfo_height()
    root.rowconfigure(1,weight=1)
    root.mainloop()
