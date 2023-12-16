import tkinter as tk
from PIL import ImageTk
from tkinter import messagebox, ttk
import cv2
import random
import os
from PIL import Image
from utils.utils import test_log
from SMLB.k_restart import KR
from SMLB.pso import PSO
from SMLB.kr_transfer import TKR
from model.rn50 import Rn50
from model.mbv2 import Mbv2
from model.dn121 import Dn121
from model.swin import Swin_b
from model.vitB import Vit_b
from laser.Vector import Vector
from laser.Constained_Vector import Cons_Vector
import time
from laser.laser import makeLB, multiLB
from utils.utils import image_transformer
# tkinter GUI 超参数
laser_size = 10
img = None
laserMask = False
multiLaserMask = False
laser = None
laserList = []
FPS = 50
# 创建视频捕捉对象
CAMERA_ID = 0
cap = cv2.VideoCapture(CAMERA_ID)

# 目标模型超参数
# 1 基本实例
rn50 = Rn50()
mbv2 = Mbv2()
dn121 = Dn121()
vit_b = Vit_b()
swin = Swin_b()
random.seed(3407)
n_vct = Vector()
c_vct = Cons_Vector()
# 2 超参数设置
target_model = rn50
vct = c_vct
atk_kr = KR(target_model, vct)
atk = PSO(target_model, vct)


# 510 绿色 750 红色  440 蓝色 415 紫色
# 下拉框选择事件
def on_combobox_select(event):
    # 获取选中的值
    global target_model
    selected_value = combobox.get()
    if selected_value == 'Resnet50':
        target_model = rn50
    elif selected_value == 'MobileNetV2':
        target_model = mbv2
    elif selected_value == 'DenseNet121':
        target_model = dn121
    elif selected_value == 'Swin-B':
        target_model = swin
    elif selected_value == 'ViT-B':
        target_model = vit_b


# 弹窗，展示当前图片以及标签
def show_image_window(image, text):
    # 创建新的Toplevel窗口
    image_window = tk.Toplevel(root)
    image_window.title(text)
    # 显示图片
    image_label = tk.Label(image_window)
    image_label.pack()
    photo = ImageTk.PhotoImage(image=image)
    image_label.configure(image=photo)
    image_label.image = photo


# 攻击当前图片，产生多个对抗激光
def multi_adv():
    update_setting()
    global img
    global multiLaserMask
    global laserList
    suc_times = 0
    suc_num = 0
    for i in range(laser_size):
        new_img = image_transformer(img) if i > 0 else img
        theta, atk_times = atk.getAdvLB(image=img, num_particles=30, inertia_weight_max=0.9,inertia_weight_min=0.5, cognitive_weight=1.4,
                                        social_weight=2, max_iterations=20)
        if atk_times == -1:
            theta, atk_times = atk_kr.getAdvLB(image=new_img, S=30, tmax=100, k=3, theta=theta)
            if theta is None:
                print('攻击失败')
                continue
        suc_times += atk_times
        suc_num += 1
        print('攻击成功 查询次数 %d' % (suc_times / suc_num))
        laserList.append(theta)

    multiLaserMask = True


# 攻击当前图片，产生一个对抗激光
def adv():
    update_setting()
    global img
    global laserMask
    global laser
    suc_times = 0
    suc_num = 0
    theta, atk_times = atk.getAdvLB(image=img, num_particles=30, inertia_weight_max=0.9, inertia_weight_min=0.5,
                                    cognitive_weight=1.4,
                                    social_weight=2, max_iterations=20)
    if atk_times == -1:
        theta, atk_times = atk_kr.getAdvLB(image=img, S=30, tmax=100, k=3, theta=theta)
        if theta is None:
            print('攻击失败')
            messagebox.showinfo("攻击结果", "攻击失败！")
            return
    suc_times += atk_times
    suc_num += 1
    print('攻击成功 查询次数 %d' % (suc_times / suc_num))
    laserMask = True
    laser = theta


# 验证当前图片
def val():
    conf_list = atk.modelApi.get_conf(img)
    text_conf.set("%s, 置信%f" % (conf_list[0][0], conf_list[0][1]))
    # show_image_window(img, "%s, 置信%f" % (conf_list[0][0], conf_list[0][1]))


# 将图像上所有提示激光清除
def reset():
    global cap
    global laserMask
    global multiLaserMask
    global laserList
    multiLaserMask = False
    laserList = []
    laserMask = False
    # root.after_cancel(update_frame.timer_id)
    # cap = cv2.VideoCapture(CAMERA_ID)
    # update_frame()


def update_frame():
    global img
    global laserMask
    global laser
    global multiLaserMask
    global laserList
    k = 1.5
    VIDEO_SIZE = (int(1152 / k), int(648 / k))
    ret, frame = cap.read()
    if not ret:
        print("无法读取视频帧")
        return
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    img = img.resize(VIDEO_SIZE, Image.LANCZOS)
    if laserMask:
        photo = ImageTk.PhotoImage(image=makeLB(laser, img))
    elif multiLaserMask:
        photo = ImageTk.PhotoImage(image=multiLB(laserList, img))

    else:
        photo = ImageTk.PhotoImage(image=img)
    video_label.configure(image=photo)
    video_label.image = photo
    timer_id = root.after(int(1000 / FPS), update_frame)  # 每隔10毫秒更新画面
    update_frame.timer_id = timer_id


# 更新激光参数
def update_setting():
    if phi_entry.get() == '' or width_entry.get() == '' or alpha_entry.get() == '':
        messagebox.showwarning("警告", "请输入参数")
        return
    c_vct.set_laser(float(phi_entry.get()), float(width_entry.get()), float(alpha_entry.get()))


# 单选框
def selected():
    if color.get() == 'Red':
        text_phi.set('750')
    elif color.get() == 'Green':
        text_phi.set('510')
    elif color.get() == 'Blue':
        text_phi.set('440')


# 检查视频捕捉对象是否成功打开
if not cap.isOpened():
    print("无法打开视频流")
    exit()
start_time = time.time()

# ======================================GUI======================================
root = tk.Tk()
root.title("实时摄像头画面")
# 实时置信标签
text_conf = tk.StringVar(value='')
# 单选按钮的值
color = tk.StringVar(value='Red')
# 激光参数
text_phi = tk.StringVar(value='750')
text_width = tk.StringVar(value='20')
text_alpha = tk.StringVar(value='0.7')
# 视频标签
video_label = tk.Label(root)
video_label.pack(padx=10, pady=10)

# 更新帧
update_frame()

# 按钮Frame
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)
# 下拉选择框
conf_label = tk.Label(buttons_frame, textvariable=text_conf)
conf_label.pack(side=tk.LEFT, padx=10)

# 创建按钮并添加到按钮Frame
button1 = tk.Button(buttons_frame, text="生成对抗激光", command=lambda: adv())
button1.pack(side=tk.LEFT, padx=10)

button2 = tk.Button(buttons_frame, text="生成对抗激光组", command=lambda: multi_adv())
button2.pack(side=tk.LEFT, padx=10)

button3 = tk.Button(buttons_frame, text="查询当前分类", command=lambda: val())
button3.pack(side=tk.LEFT, padx=10)

button4 = tk.Button(buttons_frame, text="重置画面", command=lambda: reset())
button4.pack(side=tk.LEFT, padx=10)

# 下拉选择框
label = tk.Label(buttons_frame, text="模型选择")
label.pack(side=tk.LEFT, padx=10)
choices = ['ResNet50', 'MobileNet-V2', 'DenseNet-121', 'Vit-B', 'Swin-B', 'WRN-101']
combobox = ttk.Combobox(buttons_frame, values=choices)
combobox.set("ResNet50")  # 设置默认值
combobox.bind("<<ComboboxSelected>>", on_combobox_select)  # 绑定选择事件
combobox.pack(pady=10)

# 创建红色单选按钮
red_radio = tk.Radiobutton(root, text="红色", variable=color, value="Red", fg="red", command=selected)
red_radio.pack(side=tk.LEFT)

# 创建绿色单选按钮
green_radio = tk.Radiobutton(root, text="绿色", variable=color, value="Green", fg="green", command=selected)
green_radio.pack(side=tk.LEFT)

# 创建蓝色单选按钮
blue_radio = tk.Radiobutton(root, text="蓝色", variable=color, value="Blue", fg="blue", command=selected)
blue_radio.pack(side=tk.LEFT)

# 输入框Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# 波长
laser_phi = tk.Label(input_frame, text="波长:")
laser_phi.pack(side=tk.LEFT, padx=10)
phi_entry = tk.Entry(input_frame, textvariable=text_phi)
phi_entry.pack(side=tk.LEFT, padx=10)

# 宽度
laser_width = tk.Label(input_frame, text="宽度:")
laser_width.pack(side=tk.LEFT, padx=10)
width_entry = tk.Entry(input_frame, textvariable=text_width)
width_entry.pack(side=tk.LEFT, padx=10)

# 强度
laser_alpha = tk.Label(input_frame, text="强度:")
laser_alpha.pack(side=tk.LEFT, padx=10)
alpha_entry = tk.Entry(input_frame, textvariable=text_alpha)
alpha_entry.pack(side=tk.LEFT, padx=10)

root.mainloop()

# 释放视频捕捉对象和窗口
cap.release()
cv2.destroyAllWindows()
