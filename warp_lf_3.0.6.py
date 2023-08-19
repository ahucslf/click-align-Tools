# from posixpath import join
# from secrets import randbits
import shutil
import cv2 as cv
import numpy as np
import os
import random
import math
# import base64
import natsort
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import sys
#from skimage.metrics import structural_similarity as ssim
#import sklearn.metrics as skm

class warp_lf_2(Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master

        self.pack()
        self.visible_dir = ''
        self.infrared_dir = ''
        self.exp_path = ''
        self.point_i_dir = ''
        self.point_v_dir = ''
        self.warp_save_path = ''
        self.text_order = 0
        self.img_num = 0
        # ----------------- GUI 部件 ---------------------
        # dir entry & load
        self.create_btns()



    def create_btns(self):
        self.label0 = Label(self, text="标注根目录:")
        self.label0.grid(row=0, column=0,pady=2, sticky=E+W)

        self.btn0 = Button(self, text="选择root文件夹",
                            command = self.get_exp_dir)
        self.btn0.grid(row=0, column=1,pady=2,  sticky=E+W)

        # self.label2 = Label(self, text="热红外图像目录:")
        # self.label2.grid(row=1, column=0,pady=2,  sticky=E+W)

        # self.btn2 = Button(self, text="选择T文件夹",
        #                    command=self.get_i_dir)
        # self.btn2.grid(row=1, column=1, pady=2, sticky=E+W)

        # self.label21 = Label(self, text="热红外标注点目录:")
        # self.label21.grid(row=2, column=0,pady=2,  sticky=E+W)

        # self.btn21 = Button(self, text="选择T_point文件夹",
        #                    command=self.get_point_i_dir)
        # self.btn21.grid(row=2, column=1, pady=2, sticky=E+W)

        # self.label1 = Label(self, text="可见光图像目录:")
        # self.label1.grid(row=3, column=0, pady=2, sticky=E+W)

        # self.btn1 = Button(self, text="选择Z文件夹",
        #                    command=self.get_v_dir)
        # self.btn1.grid(row=3, column=1, pady=2, sticky=E+W)

        # self.label11 = Label(self, text="可见光标注点目录:")
        # self.label11.grid(row=4, column=0, pady=2, sticky=E+W)

        # self.btn11 = Button(self, text="选择Z_point文件夹",
        #                    command=self.get_point_v_dir)
        # self.btn11.grid(row=4, column=1, pady=2, sticky=E+W)

        self.lbs_sr = Label(self, text='随机扭曲次数: ')
        text_default_warp_num = StringVar()
        text_default_warp_num.set("1")
        self.entry_set_rand = Entry(self, textvariable=text_default_warp_num)
        self.lbs_sr.grid(row=5, column=0, sticky=E+W)
        self.entry_set_rand.grid(row=5, column=1, pady=2, sticky=E+W)

        # self.label_note_warp_num = Label(self, text="注意：雾天,夜晚,傍晚等场景为8,其他默认为5",background="#D3D3D3")
        # self.label_note_warp_num.grid(row=6, column=0, pady=2,columnspan=2, sticky=N+E+W)

        self.lbs_mb1 = Label(self, text='运动模糊参数: ',background="#B0C4DE")
        self.lbs_mb1.grid(row=7, column=0, columnspan=3, sticky=E+W)

        self.lbs_mb = Label(self, text='运动模糊次数: ',background="#B0C4DE")
        text_default_mb_num = StringVar()
        text_default_mb_num.set("1")
        self.entry_set_mb = Entry(self, textvariable=text_default_mb_num)
        self.lbs_mb.grid(row=8, column=0, sticky=E+W)
        self.entry_set_mb.grid(row=8, column=1, columnspan=1, pady=2, sticky=E+W)
        
        self.lbs_mb_degree = Label(self, text='运动模糊程度: ',background="#B0C4DE")
        text_default_mb_degree = StringVar()
        # text_default_mb_degree.set("10")
        self.entry_set_mb_degree = Entry(self, textvariable=text_default_mb_degree)
        self.lbs_mb_degree.grid(row=9, column=0, sticky=E+W)
        self.entry_set_mb_degree.grid(row=9, column=1, columnspan=1, pady=2, sticky=E+W)

        self.lbs_gb1 = Label(self, text='高斯模糊参数: ',background="#B0C4DE")
        self.lbs_gb1.grid(row=10, column=0, columnspan=3, sticky=E+W)

        self.lbs_gb = Label(self, text='高斯模糊次数: ',background="#B0C4DE")
        text_default_gb_num = StringVar()
        text_default_gb_num.set("1")
        self.entry_set_gb = Entry(self, textvariable=text_default_gb_num)
        self.lbs_gb.grid(row=11, column=0, sticky=E+W)
        self.entry_set_gb.grid(row=11, column=1, columnspan=1, pady=2, sticky=E+W)
        
        self.lbs_gb_degree = Label(self, text='高斯模糊核大小: ',background="#B0C4DE")
        text_default_gb_degree = StringVar()
        # text_default_gb_degree.set("13")
        self.entry_set_gb_degree = Entry(self, textvariable=text_default_gb_degree)
        self.lbs_gb_degree.grid(row=12, column=0, sticky=E+W)
        self.entry_set_gb_degree.grid(row=12, column=1, columnspan=1, pady=2, sticky=E+W)

        self.lbs_sp1 = Label(self, text='椒盐噪声参数: ',background="#B0C4DE")
        self.lbs_sp1.grid(row=13, column=0, columnspan=3, sticky=E+W)

        self.lbs_sp_num = Label(self, text='椒盐噪声次数: ',background="#B0C4DE")
        text_default_sp_num = StringVar()
        text_default_sp_num.set("1")
        self.entry_set_sp = Entry(self, textvariable=text_default_sp_num)
        self.lbs_sp_num.grid(row=14, column=0, sticky=E+W)
        self.entry_set_sp.grid(row=14, column=1, columnspan=1, pady=2, sticky=E+W)
        
        self.lbs_sp_prob = Label(self, text='椒盐噪声比例: ',background="#B0C4DE")
        text_default_sp_prob = StringVar()
        # text_default_sp_prob.set("0.02")
        self.entry_set_sp_prob = Entry(self, textvariable=text_default_sp_prob)
        self.lbs_sp_prob.grid(row=15, column=0, sticky=E+W)
        self.entry_set_sp_prob.grid(row=15, column=1, columnspan=1, pady=2, sticky=E+W)

        self.lbs_chessboard = Label(self, text='输出模式： ',background="#B0C4DE")
        text_default_chessboard = StringVar()
        text_default_chessboard.set("3")
        self.entry_set_chessboard = Entry(self, textvariable=text_default_chessboard)
        self.lbs_chessboard.grid(row=16, column=0, sticky=E+W)
        self.entry_set_chessboard.grid(row=16, column=1, columnspan=1, pady=2, sticky=E+W)

        self.label_note_blur = Label(self, 
                text="注意： 输出模式: 0-全输出; \n1-只输出check_board; \n2-全输出除了check_board;\n3-输出check_board和warp_i;  \n运动模糊程度为8-30的整数\n高斯模糊核大小为11-23的奇数\n椒盐噪声比例为0.01-0.04的浮点数",
                background="#D3D3D3")
        self.label_note_blur.grid(row=17, column=0, pady=2,columnspan=2, sticky=N+E+W)


        self.ldBtn = Button(self, text="开始加载", command=self.all_warp)
        self.ldBtn.grid(row=18, column=0,pady=2, columnspan=2, sticky=N+E+W)
        var=IntVar() # 创建一个变量
        var.set("0")
        self.pbar1=Progressbar(root,length=200,mode='determinate',variable=var) # 绑定变量
        # 水平进度条，模式：determinate 从起始点到终点
        #self.pbar1.grid(row=16, column=0, pady=5,columnspan=3, sticky=N+E+W)
        self.pbar1['maximum']=200
        self.pbar1.pack(padx=10,pady=5)
        # self.loading_text = Label(self, text="running...")
        # self.loading_text.grid(row=18, column=0,pady=2, columnspan=2, sticky=N+E+W)
        # self.text_show_len = StringVar()
        # self.label_show_len = Label(self, textvariable=self.text_show_len)
        # self.label_show_len.grid(row=18, column=0, pady=2, columnspan=2, sticky=E+W)
        # self.v_file_path = self.get_v_dir()
        # self.i_file_path = self.get_i_dir()
        # self.exp_path = self.get_exp_dir()
        # self.point_i_dir = self.get_point_v_dir()
        # self.point_v_dir = self.get_point_i_dir()
        return 

    
    def get_v_dir(self):
        self.visible_dir = askdirectory()
        print(self.visible_dir)

    def get_i_dir(self):
        self.infrared_dir = askdirectory()
        print(self.infrared_dir)

    def get_point_v_dir(self):
        self.point_v_dir = askdirectory()
        print(self.point_v_dir)

    def get_point_i_dir(self):
        self.point_i_dir = askdirectory()
        print(self.point_i_dir)

    def get_exp_dir(self):
        # self.exp_path = askdirectory()
        self.root_path = askdirectory()

        print(self.root_path)

    def get_warp_dir(self):
        self.warp_save_path = askdirectory()
        print(self.warp_save_path)



    def read_points(self, txt_point_path):

        count = 0
        print(txt_point_path)
        if not os.path.exists(txt_point_path):
            print('No .txt label file found in the specified dir!')
            messagebox.showwarning(
                title='警告', message="文件夹中没有对应图像的txt标注文件")
            return 
        else:
            for index, line in enumerate(open(txt_point_path,'r')):
                if line == '\n':
                    break
                count += 1

            with open(txt_point_path, 'r') as f:
                p = [[]]
                for i in range(0,count):
                    line = f.readline().split()
                    p[i] = [float(line[0]),float(line[1])]
                    p.append(p[i])
                return p

    def warp(self):
        
        # self.point_v_dir = self.visible_dir + "_point"
        # self.point_i_dir = self.infrared_dir + "_point"
        
        self.infrared_dir = os.path.join(self.exp_path,'infrared')
        self.visible_dir = os.path.join(self.exp_path,'visible')
        self.point_v_dir =  os.path.join(self.exp_path,'visible_point')
        self.point_i_dir =  os.path.join(self.exp_path,'infrared_point')
        self.warp_save_path = os.path.join(self.exp_path, 'annotation')

        # for file_order,file_name_v in enumerate(os.listdir(self.v_file_path)):
        # self.check_challenges_lines()

        if len(os.listdir(self.point_v_dir)) != len(os.listdir(self.point_i_dir)):
            messagebox.showinfo(title='错误',message='T_point和Z_point内文件数不一致')
            sys.exit()

        if len(os.listdir(self.visible_dir)) != len(os.listdir(self.infrared_dir)):
            messagebox.showinfo(title='错误',message='T和Z内文件数不一致')
            sys.exit()
        # if len(os.listdir(self.point_v_dir)) != len(os.listdir(self.visible_dir)):
        #     messagebox.showinfo(title='错误',message='Z和Z_point内文件数不一致')
        #     sys.exit()

        # if len(os.listdir(self.point_i_dir)) != len(os.listdir(self.infrared_dir)):
        #     messagebox.showinfo(title='错误',message='T和T_point内文件数不一致')
        #     sys.exit()
        #     file_order = "{:0>3}".format(file_order + 1) 
        #     file_num = len(os.listdir(self.v_file_path))
        #     file_name_i = file_name_v.replace('v','i')
        self.img_num = len(os.listdir(self.visible_dir))
        self.text_num = len(os.listdir(self.point_v_dir))
        homo_save_path_h1 = self.exp_path + '/gt_homography.txt'
        homo_save_path_h2 = self.exp_path + '/gt_and_random_homography.txt'
        if os.path.exists(homo_save_path_h1):
            os.remove(homo_save_path_h1)
        if os.path.exists(homo_save_path_h2):
            os.remove(homo_save_path_h2)
        if os.path.exists(self.warp_save_path ):
            shutil.rmtree(self.warp_save_path )
        H1_all_list = []
        H2_all_list = []
        #     file_num ="{:0>3}".format(file_num)
        #     print('file_name: '+file_name_i.replace('_i','')+' file_num: %s'%file_order+'/%s'%file_num)
        # for self.img_order,(img_name_v,img_name_i) in enumerate(zip(os.listdir(self.visible_dir),os.listdir(self.infrared_dir))):
        for self.text_order,(text_name_v,text_name_i) in enumerate(zip(os.listdir(self.point_v_dir),os.listdir(self.point_i_dir))):
            #self.img_order = "{:0>3}".format(self.img_order + 1) 
            #original_image = cv.imread(exp_path+'infrared/'+'i%s'%order+'.jpg')
            img_name_v = text_name_v.replace('txt','jpg')
            img_name_i = text_name_i.replace('txt','jpg')

            img_path_i = os.path.join(self.infrared_dir,img_name_i)
            if not os.path.exists(img_path_i):
                messagebox.showerror(title='错误',message=f'未找到{img_path_i}图片')
                sys.exit()
            original_image = cv.imread(img_path_i)
            
            #target_image = cv.imread(exp_path+'visible/'+'v%s'%order+'.jpg')
            img_path_v = os.path.join(self.visible_dir,img_name_v)
            if not os.path.exists(img_path_v):
                messagebox.showerror(title='错误',message=f'未找到{img_path_v}图片')
                sys.exit()
            target_image = cv.imread(img_path_v)

            annotation_point_i = os.path.join(self.point_i_dir,text_name_i)
            print(annotation_point_i)
            annotation_point_v = os.path.join(self.point_v_dir,text_name_v)
            print(annotation_point_v)
            src_more_i_point = np.float32(
                self.read_points(annotation_point_i)
                ).reshape(-1,1,2)

            den_more_v_point = np.float32(
                self.read_points(annotation_point_v)
                ).reshape(-1,1,2)

            points_name_i = img_name_i.replace('jpg','txt')
            points_name_v = img_name_v.replace('jpg','txt')
            if len(src_more_i_point) > len(den_more_v_point):
                messagebox.showwarning(title='警告',message=f'{points_name_i} 的行数大于{points_name_v} 的行数,请检查')
                sys.exit()
            if len(src_more_i_point) < len(den_more_v_point):
                messagebox.showwarning(title='警告',message=f'{points_name_i} 的行数小于{points_name_v} 的行数,请检查')   
                sys.exit()
            #H, status = cv.findHomography(src_more_i_point, den_more_v_point, cv.RANSAC ,6.0)#num from 1 to 10
            H1, status = cv.findHomography(src_more_i_point, den_more_v_point, 0)
            H1_list = []
            # H2_list = []
            H1_list.append(img_name_i)
            for h1_i in range(0,3):
                for h1_j in range(0,3):
                    H1_list.append(str('{:.10f}'.format(H1[h1_i][h1_j])))
            H1_all_list.append(H1_list)

            warped_i = cv.warpPerspective(original_image, H1, (target_image.shape[1], target_image.shape[0]))
            if self.entry_set_chessboard.get() != '2':
                checker_board_path = os.path.join(self.warp_save_path,"check_board")
                if not os.path.exists(checker_board_path):
                    os.makedirs(checker_board_path)
            if self.entry_set_chessboard.get() != '1':
                warp_i_save_path = os.path.join(self.warp_save_path, 'warp_i')
                if not os.path.exists(warp_i_save_path):
                    os.makedirs(warp_i_save_path)

                print(img_name_i)
                warp_i_img_path = os.path.join(warp_i_save_path,img_name_i.replace('i','warp_i'))
                cv.imwrite(warp_i_img_path,warped_i)
            if self.entry_set_chessboard.get() != '3':
                if self.entry_set_chessboard.get() != '2':  
                    checker_board_path_2 = os.path.join(checker_board_path,"random_warp")

                    if not os.path.exists(checker_board_path_2):
                        os.makedirs(checker_board_path_2)
                setting_random_num = self.entry_set_rand.get()
                random_v_save_path = os.path.join(self.warp_save_path,'random_visible')
                warp_i_random_save_path = os.path.join(self.warp_save_path,'warp_i_random')
                if not os.path.exists(warp_i_random_save_path):
                    os.makedirs(warp_i_random_save_path)
                if not os.path.exists(random_v_save_path):
                    os.makedirs(random_v_save_path)
                
                for random_num in range(0,int(setting_random_num)):
                    H2_list = []
                    H_Random = self.Random_H()
                    # if int(self.img_order)%7 == 0:
                    #     H_Random = self.Random_rotate_H()
                    #     rotate_random_num = rotate_random_num + 1
                    H2 = np.dot(H_Random,H1)
                    for i in range(0,3):
                        for j in range(0,3):
                            H2[i][j] = H2[i][j]/H2[2][2]
                    
                    
                    for h2_i in range(0,3):
                        for h2_j in range(0,3):
                            H2_list.append(str('{:.10f}'.format(H2[h2_i][h2_j])))

                    H2_all_list.append(H2_list)

                    warp_random_i_1 = cv.warpPerspective(original_image, H2, (target_image.shape[1], target_image.shape[0]))
                    target_random_v = cv.warpPerspective(target_image, H_Random, (target_image.shape[1], target_image.shape[0]))
                    if self.entry_set_rand.get() == 1 :
                        random_v_img_path = os.path.join(random_v_save_path,img_name_v.replace('v','random_v'))
                    else:
                        random_v_img_path = os.path.join(random_v_save_path,img_name_v.replace('v','random_v').replace('.jpg','_'+str(random_num+1)+'.jpg'))

                    cv.imwrite(random_v_img_path,target_random_v)

                    #warp_random_i_2 = cv.warpPerspective(warped_i, H_Random, (target_image.shape[1], target_image.shape[0]))
                    if self.entry_set_rand.get() == 1 :
                        cv.imwrite(os.path.join(warp_i_random_save_path,img_name_i.replace('i','warp_i_gt2random')),warp_random_i_1)
                    else:
                        cv.imwrite(os.path.join(warp_i_random_save_path,img_name_i.replace('i','warp_i_gt2random').replace('.jpg','_'+str(random_num+1)+'.jpg')),warp_random_i_1)

                    if self.entry_set_chessboard.get() != '2':
                        if self.entry_set_rand.get() == 1 :
                            checker_name2 = os.path.join(checker_board_path_2,img_name_v.replace('v','random_v_i'))
                        else:
                            checker_name2 = os.path.join(checker_board_path_2,img_name_v.replace('v','random_v_i').replace('.jpg','_'+str(random_num+1)+'.jpg'))
                        self.checker_board(warp_random_i_1,target_random_v,checker_name2)
                
            if self.entry_set_chessboard.get() != '2':            
                checker_board_path_1 = os.path.join(checker_board_path,"normal_warp")
                if not os.path.exists(checker_board_path_1):
                        os.makedirs(checker_board_path_1)
                checker_name1 = os.path.join(checker_board_path_1,img_name_v.replace('v','v_warp_i'))
                self.checker_board(warped_i,target_image,checker_name1)
            
            if int(self.entry_set_rand.get()) > 1:
                self.blur_noise_times(random_v_save_path)
            step_strip = int(((self.text_order+1)/self.text_num)*200)
            self.pbar1['value']=step_strip  ##
            #progressbarVar.set(i)
            self.pbar1.update()
            # self.text_show_len = str(str((self.img_order+1))+'/'+ str(self.img_num))
        
        if self.entry_set_chessboard.get() != '1':
            self.homo_writer(H1_all_list,homo_save_path_h1)
            if self.entry_set_chessboard.get() != '3':
                self.homo_writer(H2_all_list,homo_save_path_h2)
        # messagebox.showinfo(
        #         title='完成', message=f"此文件夹中 {len(os.listdir(self.point_v_dir))}/{str(len(os.listdir(self.visible_dir)))} 张图像已完成扭曲增广变换!")

    def all_warp(self):
        sub_folder_list = os.listdir(self.root_path)
        self.img_all_num = 0

        for list_order,sub_folder_name in enumerate(sub_folder_list):

            self.exp_path = os.path.join(self.root_path,sub_folder_name)
            self.warp()
            self.img_all_num = self.img_all_num + self.img_num 
            print(f'{list_order + 1} : {sub_folder_name} 已完成！')
        print(f'\n共{self.img_all_num}张图片已完成！\n')

    def check_challenges_lines(self):
        self.challenges_text_path = os.path.join(self.exp_path,'Challenge_Attributes.txt')
        if not os.path.exists(self.challenges_text_path):
            messagebox.showwarning(
                title='提醒', message="没有找到 Challenge_Attributes.txt,请检查路径! ")
            sys.exit()
        else:
            self.chellenges_dic = {}
            self.chellenges_list = []
            self.chellenges_imgname_list = []
            self.img_v_list = os.listdir(self.visible_dir)
            self.img_v_list = natsort.natsorted(self.img_v_list)
            with open (self.challenges_text_path,'r') as f:
                for line in f.readlines():
                    line_dic = {line.split('\n')[0].split(':')[0] : line.split('\n')[0].split(':')[1]}
                    if line.split('\n')[0].split(':')[0] in self.img_v_list:
                        self.chellenges_dic.update(line_dic)
                        self.chellenges_list.append(line_dic)
                        self.chellenges_imgname_list.append(line.split('\n')[0].split(':')[0] )
                len_challenges_text = len(self.chellenges_list)
            self.chellenges_imgname_list = natsort.natsorted(self.chellenges_imgname_list)
            self.chellenges_list = natsort.natsorted(self.chellenges_list)
            with open(self.challenges_text_path,'w') as f:
                for dic_item in self.chellenges_list:
                    for dic_item_key,dic_item_value in dic_item.items():
                        print(dic_item_key+':'+dic_item_value + '\n')
                        f.write(dic_item_key+':'+dic_item_value + '\n')
                    # f.write(str(dic_item[0])+':'+str(dic_item[1]) + '\n')
            print(len_challenges_text ,len(os.listdir(self.point_i_dir)),len(os.listdir(self.point_v_dir)))
            print(self.chellenges_dic)

            if len_challenges_text < len(os.listdir(self.point_i_dir)) and len_challenges_text < len(os.listdir(self.point_v_dir)):

                messagebox.showwarning(
                title='警告', message="Challenge_Attributes.txt 行数小于 point.text 数量,请检查")
                sys.exit()


    def homo_writer(self, H_all_list,homo_txt_path):
        with open(homo_txt_path,'w') as f:
            for H_list in H_all_list:
                H_str = ''
                for H_item in H_list:
                    if not "DJI" in H_item:
                        H_str = H_str + H_item + ' '
                H_str = H_list[0] + ',' +H_str + '\n'
                f.write(H_str)

    def homo_reader(self, homo_txt_path):
        H = np.zeros((3,3))
        H_all = []
        with open(homo_txt_path,'r') as f:
            for line in f.readlines():
                line = line.strip('\n').split(',')[-1]
                num = 0
                for i in range(0,3):
                    for j in range(0,3):
                        H[i][j] = float(line.split(' ')[num])
                        num = num +1
                H_all.append(H)
        return H

    def get_angel_points():
        point_list = []
        return point_list

    def checker_board(self, img_i,img_v,checker_name):
        checker_img = img_v
        block_width = 1920//16
        block_height = 1080//10
        black_block = img_i
        for row in range(10):
            for col in range(16):
                if (row+col)%2==0:
                    row_begin = row*block_height
                    row_end = row_begin+block_height
                    col_begin = col*block_width
                    col_end = col_begin+block_width
                    checker_img[row_begin:row_end,col_begin:col_end] = black_block[row_begin:row_end,col_begin:col_end]
        cv.imwrite(checker_name,checker_img)


    def Random_H(self):
        H = np.zeros((3,3))
        H[0][0] = random.uniform(0.9, 1.1)
        H[1][1] = random.uniform(0.9, 1.1)
        H[0][1] = random.uniform(-0.2, 0.2)
        H[1][0] = random.uniform(-0.2, 0.2)
        H[0][2] = random.randint(-150, 150)
        H[1][2] = random.randint(-100, 100)
        H[2][0] = random.uniform(-0.0001, 0.0001)
        H[2][1] = random.uniform(-0.0001, 0.0001)
        H[2][2] = 1

        return H

    def Random_rotate_H(self):

        num = random.uniform(-0.1,0.1)

        #大于0时向下旋转
        theta = math.pi * num
        H = np.zeros((3,3))
        H[2][2] = 1
        H[0][0] = math.cos(theta)
        H[1][1] = math.cos(theta)
        H[0][1] = -math.sin(theta)
        H[1][0] = math.sin(theta)
        if num>0:
            H[0][2] = 2500 * num
            H[1][2] = -2500 * num
        else:
            H[0][2] = 1300 * num
            H[1][2] = -3000 * num
        H[2][0] = 0
        H[2][1] = 0
        print('random rotate theta:',theta)

        return H

    def blur_noise_times(self,img_fold_path):
        #img_fold_path = img_fold_path
        mb_num = int(self.entry_set_mb.get())
        gb_num = int(self.entry_set_gb.get())
        sp_num = int(self.entry_set_sp.get())

        self.mb_blur_change(mb_num,img_fold_path)
        self.gb_blur_change(gb_num,img_fold_path)
        self.sp_noise_change(sp_num,img_fold_path)

    def mb_blur_change(self, mb_num,img_fold_path,mb_angle=20):
        mb_order = 0
        entry_mb_degree = self.entry_set_mb_degree.get()
        if entry_mb_degree:
            mb_degree = int(entry_mb_degree)
        else:
            mb_degree = random.randint(8,30)

        file_list = os.listdir(img_fold_path)
        random.shuffle(file_list)
        for mb_img_name in file_list:#如果有mb gb sp 则跳过这些图片 
            is_string_in = ("mb" in mb_img_name) or ("gb" in mb_img_name) or ("sp" in mb_img_name)
            while (not is_string_in) and (mb_order < mb_num) :
                mb_order+=1
                img = cv.imread(os.path.join(img_fold_path,mb_img_name))
                img_blur = self.motion_blur(img,degree=mb_degree, angle=mb_angle)
                blur_imgpath = os.path.join(img_fold_path,mb_img_name.replace(".jpg","_mb.jpg"))
                origin_img_path = os.path.join(img_fold_path,mb_img_name)
                os.remove(origin_img_path)
                cv.imwrite(blur_imgpath,img_blur)
                with open(os.path.join(self.warp_save_path,'Noise_Parameter.txt'),mode='a') as f:
                    f.write(mb_img_name.replace(".jpg","_mb.jpg") + ' MB:'+ str(mb_degree) + '\n')


    def gb_blur_change(self, gb_num,img_fold_path):
        gb_order = 0
        entry_gb_degree = self.entry_set_gb_degree.get()
        if entry_gb_degree:
            gb_degree = int(entry_gb_degree)
        else:
            gb_degree = 2 * random.randint(5,11) + 1

        file_list = os.listdir(img_fold_path)
        random.shuffle(file_list)

        for img_name in file_list:
            is_string_in = ("mb" in img_name) or ("gb" in img_name) or ("sp" in img_name)
            while (not is_string_in) and (gb_order < gb_num) :
                gb_order+=1
                img = cv.imread(os.path.join(img_fold_path,img_name))
                img_blur = self.GaussianBlur(img,degree=gb_degree)
                blur_imgpath = os.path.join(img_fold_path,img_name.replace(".jpg","_gb.jpg"))
                origin_img_path = os.path.join(img_fold_path,img_name)
                os.remove(origin_img_path)
                cv.imwrite(blur_imgpath,img_blur)
                with open(os.path.join(self.warp_save_path,'Noise_Parameter.txt'),mode='a') as f:
                    f.write(img_name.replace(".jpg","_gb.jpg")+' GN:'+ str(gb_degree)+ '\n')

    def sp_noise_change(self, sp_num,img_fold_path):
        sp_order = 0
        entry_sp_prob = self.entry_set_sp_prob.get()
        if entry_sp_prob:
            sp_prob = float(entry_sp_prob)
        else:
            sp_prob = random.uniform(0.01,0.04)

        file_list = os.listdir(img_fold_path)
        random.shuffle(file_list)
        for img_name in file_list:
            is_string_in = ("mb" in img_name) or ("gb" in img_name) or ("sp" in img_name)
            while (not is_string_in) and (sp_order < sp_num) :
                sp_order+=1
                img = cv.imread(os.path.join(img_fold_path,img_name))
                img_blur = self.sp_noise(img,prob=sp_prob)
                blur_imgpath = os.path.join(img_fold_path,img_name.replace(".jpg","_sp.jpg"))
                origin_img_path = os.path.join(img_fold_path,img_name)
                os.remove(origin_img_path)
                cv.imwrite(blur_imgpath,img_blur)
                with open(os.path.join(self.warp_save_path,'Noise_Parameter.txt'),mode='a') as f:
                    f.write(img_name.replace(".jpg","_sp.jpg") + ' SP:'+ str(round(sp_prob,4))+ '\n')


    def sp_noise(self,image,prob):
        '''
        添加椒盐噪声
        prob:噪声比例
        '''
        output = np.zeros(image.shape,np.uint8)
        thres = 1 - prob
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                rdn = random.random()
                if rdn < prob:
                    output[i][j] = 0
                elif rdn > thres:
                    output[i][j] = 255
                else:
                    output[i][j] = image[i][j]
        return output


    def motion_blur(self, image, degree=10, angle=20):
        image = np.array(image)
        # 这里生成任意角度的运动模糊kernel的矩阵， degree越大，模糊程度越高
        M = cv.getRotationMatrix2D((degree/2, degree/2), angle, 1)
        motion_blur_kernel = np.diag(np.ones(degree))
        motion_blur_kernel = cv.warpAffine(motion_blur_kernel, M, (degree, degree))
        
        motion_blur_kernel = motion_blur_kernel / degree        
        blurred = cv.filter2D(image, -1, motion_blur_kernel)
        # convert to uint8
        cv.normalize(blurred, blurred, 0, 255, cv.NORM_MINMAX)
        blurred = np.array(blurred, dtype=np.uint8)
        return blurred

    def GaussianBlur(self, image,degree=13):
        image = cv.GaussianBlur(image, ksize=(degree, degree), sigmaX=0, sigmaY=0)
        return image

    # def gaussian_noise(self, image, degree=None):
    #     row, col, ch = image.shape
    #     mean = 0
    #     if not degree:
    #         var = np.random.uniform(0.004, 0.01)
    #     else:
    #         var = degree
    #     sigma = var ** 0.5
    #     gauss = np.random.normal(mean, sigma, (row, col, ch))
    #     gauss = gauss.reshape(row, col, ch)
    #     noisy = image + gauss
    #     cv.normalize(noisy, noisy, 0, 255, norm_type=cv.NORM_MINMAX)
    #     noisy = np.array(noisy, dtype=np.uint8)
    #     return noisy


if __name__=="__main__":

    # open_icon = open("D:\py36\chessboard.ico","rb")
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
    # ## Delete the tempfile
    # os.remove(tempFile)

    root.title('配准棋盘格生成3.0—lf')
    root.geometry("300x505+750+200") 
    
    tool = warp_lf_2(master = root)
    root.mainloop()






