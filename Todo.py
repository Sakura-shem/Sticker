import time, json, os, win32com.client, tkinter, sys, getpass
from tkinter import *
from apscheduler.schedulers.background import BackgroundScheduler

class Todo:  # 定义class类，GUI界面
    # __init__方法，导入类时自动执行这里的语句
    def __init__(self):
        self.colorthemes = {"yellow":["#FFFACD","#F0E68C"],"Zima blue":["#16B8F3","#00E5EE"],"red":["#E9967A","#EE6363"],"green":["#90ee90","#32CD32"]}  # 主题的字典
        self.size = [200, 300, 400]
        self.powerboot = 0
        self.url = os.getcwd() if sys.executable[-10::1] == 'python.exe' else os.path.dirname(sys.executable)
        self.name = getpass.getuser()
        try: 
            with open(file = os.path.join(self.url, "config.json"), mode = 'r', encoding = 'utf-8') as f:
                config = json.load(f)
            x = config['x']
            y = config['y']
            size = config['size'] if config['size'] in self.size else 200
            themecolor = config['themecolor']
            powerboot = config['powerboot']
        except Exception as e:
            self.setgui(200, 100, 100, ["#FFFACD","#F0E68C"], 0)
        else:
            self.setgui(size, x, y, themecolor, powerboot)


    # GUI界面    
    def setgui(self, size, x, y, themecolor, powerboot):
        self.root = Tk()     # 窗口
        self.root.title('Todo')    # 窗口标题
        self.root.attributes('-alpha', 0.75)
        self.root.geometry('{0}x{0}+{1}+{2}'.format(size, x, y))   # 初始化窗口
        # self.root.wm_attributes("-topmost", True)   # 窗口总在最前
        self.root.overrideredirect(True)    # 窗口去边框
        self.themecolor = themecolor
        self.powerboot = IntVar()
        self.powerboot.set(powerboot)


        # 标题栏
        self.titleframe = Frame(self.root, bg = self.themecolor[0], bd = 0)
        self.titleframe.grid(row = 0, column = 0, sticky = 'nswe')
        
        # ICON
        self.icon = Label(self.titleframe, text = 'S', font = ('宋体', 14), anchor = 'center', bg = self.themecolor[0]) 
        self.icon.grid(row = 0, column = 0, sticky = 'nswe')
        # 绑定事件 -- change the size of the window
        self.icon.bind('<Button-1>', self.changewindow) 
        self.icon.bind('<Enter>', self.enter)
        self.icon.bind('<Leave>', self.leave)   

        # 标题
        self.title = Label(self.titleframe, text = "Todo", cursor='fleur', anchor = 'center', font = ("微软雅黑", 14), bd = 0, bg = self.themecolor[0], justify = 'center')
        self.title.grid(row = 0, column = 1, sticky = 'nswe')
        # 绑定拖动事件
        self.title.bind('<ButtonPress-1>', self.setxy)
        self.title.bind('<B1-Motion>', self.resize) 

        # 设置按钮
        self.sets = Label(self.titleframe, text = '…', font = ("宋体", 14), anchor = 'center', bg = self.themecolor[0])
        self.sets.grid(row = 0, column = 3, sticky = 'nswe')
        # 绑定单击事件，调用 self.postsetsmenu() 方法弹出菜单
        self.sets.bind('<ButtonRelease-1>', self.postsetsmenu)

        # 关闭按钮
        self.quit = Label(self.titleframe, text = '×',font = ("宋体", 14), anchor = 'center', bg = self.themecolor[0])
        self.quit.grid(row = 0, column = 4, sticky = 'nswe')
        self.quit.bind('<ButtonRelease-1>',self.quitapp)

        # 文本区域
        self.text = Text(self.root, font = ("宋体", 14), bd = 0, bg = self.themecolor[0], undo = True, maxundo = 5)
        # 加载数据
        # todo: 每插入一个字，加一个回调分割。
        text = self.load()
        if text != None:
            self.text.insert(tkinter.INSERT, text)
        self.text.grid(row = 1, column = 0, sticky = 'nswe')
        def callback(event):
            self.contentunsaved()
            self.text.edit_separator()
        self.text.bind('<Key>', callback)
        
        # 给所有组件通用事件绑定
        self.root.bind_all('<Control-s>', self.savecontent)
        # self.root.bind_all('<Enter>', self.enter)
        # self.root.bind_all('<Leave>', self.leave)

        # 设置填充
        self.root.grid_columnconfigure(0, weight = 1)
        self.root.grid_rowconfigure(1, weight = 1)
        self.titleframe.grid_columnconfigure(1, weight = 1)

        # 颜色主题菜单的绑定变量
        self.themesvar = IntVar()
        index = list(self.colorthemes.values()).index(self.themecolor)
        self.themesvar.set(index)

        # 创建菜单
        self.setsmenu = Menu(self.root, tearoff = False)
        # self.setsmenu.add_command(label = 'New', command = Todo())  # 实例化新的gui，新建一个窗口
        # self.setsmenu.add_separator()   #添加分隔线

        # 颜色主题菜单
        self.themesmenu = Menu(self.setsmenu, tearoff = False)
        for i in range(len(self.colorthemes.keys())):
            self.themesmenu.add_radiobutton(label = list(self.colorthemes.keys())[i], variable = self.themesvar, value = i, command = self.setcolor)   #调用self.setcolor()方法设置所有组件的颜色
        self.setsmenu.add_cascade(label = 'Theme', menu = self.themesmenu)
        
        # powerboot
        self.themesmenu = Menu(self.setsmenu, tearoff = False)
        self.themesmenu.add_radiobutton(label = 'open', variable = self.powerboot, value = 1, command = self.openpowerboot)   # open powerboot
        self.themesmenu.add_radiobutton(label = 'close', variable = self.powerboot, value = 0, command = self.closepowerboot)   # close powerboot
        self.setsmenu.add_cascade(label = 'powerboot', menu = self.themesmenu)

        self.root.update()
        self.savecontent(event = '')
        if self.powerboot.get() == 0:
            self.closepowerboot()
        else:
            # check the ink

            self.openpowerboot()

        # auto save erverday
        scheduler = BackgroundScheduler(timezone = 'Asia/Shanghai')
        scheduler.add_job(
            self.saveconfig,
            trigger = 'cron',
            second = 1,
            minute = 1,
            hour = 1
        )
        scheduler.start() 

        self.root.mainloop()    # 窗体进入事件循环

    #下面两个为窗体移动的方法
    def setxy(self, event):
        self.xr = event.x
        self.yr = event.y
        self.saveconfig()

    def resize(self, event):
        self.root.geometry('+{0}+{1}'.format(self.root.winfo_x() + event.x-self.xr, self.root.winfo_y() + event.y-self.yr))
        self.saveconfig()
    
    def changewindow(self, event):
        index = self.size.index(self.root.winfo_width())
        index = 0 if index == 2 else index + 1 
        size = self.size[index]
        self.root.geometry('{0}x{0}+{1}+{2}'.format(size, self.root.winfo_x() + event.x, self.root.winfo_y() + event.y))   # 改变窗口
        self.saveconfig(size)
    
    # 点击菜单的颜色选项后，设置所有组件的颜色
    def setcolor(self):
        self.includes = [self.titleframe, self.icon, self.title, self.sets, self.quit, self.text]    # 列出所有组件
        for r in self.includes:
            r.configure(bg = list(self.colorthemes.values())[self.themesvar.get()][0])    # 设置组件的颜色
        self.saveconfig()

    #弹出设置菜单
    def postsetsmenu(self, event):
        self.setsmenu.post(event.x_root, event.y_root)

    def contentunsaved(self, event = None):
        text = self.title["text"]
        self.title['text'] = "*Todo"
    
    def contentsaved(self, event = None):
        text = self.title["text"]
        self.title['text'] = "Todo"
    
    # 读取文件
    def load(self):
        Now = str(time.strftime("%d %m %Y", time.localtime()))
        text = None
        try:
            with open(os.path.join(self.url, 'Notes/{0}.txt'.format(Now)), 'r', encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            url = os.listdir("Notes")
            if url:
                with open(os.path.join(self.url, 'Notes/{0}.txt'.format(url[-1])), 'r', encoding="utf-8") as f:
                    text = f.read()
        finally:
            return text

    #保存文件
    def savecontent(self, event):
        #以事件命名保存文件
        text = self.text.get(1.0, 'end')
        Now = str(time.strftime("%d %m %Y", time.localtime()))
        with open(os.path.join(self.url, 'Notes/{0}.txt'.format(Now)), 'w', encoding='utf-8') as f:
            f.write(text)    #写入文件
        self.contentsaved()
    
    # C:\Users\Shem\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    # open powerboot
    def openpowerboot(self):
        url = "C:\\Users\\{0}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(self.name)
        path = os.path.join(url, 'Todo.lnk') # 要生成的快捷方式路径及文件名
        target = icon = sys.executable # 要生成快捷方式的原文件路径
        shell = win32com.client.Dispatch("WScript.Shell") # 绑定
        shortcut = shell.CreateShortCut(path) # 生成
        shortcut.Targetpath = target # 指定路径
        shortcut.IconLocation = icon # 指定图标
        shortcut.save() # 保存
        self.saveconfig()

    # close powerboot
    def closepowerboot(self):
        url = "C:\\Users\\{0}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(self.name)
        if os.path.exists(url):
            os.remove(url)
        else:
            pass
        self.saveconfig()
    
    #卸载窗体
    def quitapp(self, event):
        self.root.destroy()
    
    def saveconfig(self, *args):
        if args != ():
            size = args[0]
        else:
            size = self.root.winfo_width()
        size = size if size in self.size else 200
        config = {
            'size': size,
            'x': self.root.winfo_x(),
            'y': self.root.winfo_y(),
            'themecolor': list(self.colorthemes.values())[self.themesvar.get()],
            'powerboot': self.powerboot.get()
        }
        print(config)
        with open(file = os.path.join(self.url, "config.json"), mode = 'w', encoding = 'utf-8') as f:
            json.dump(config, f)

    #鼠标进入组件事件
    def enter(self,event):
        event.widget['bg'] = list(self.colorthemes.values())[self.themesvar.get()][1]   #背景颜色改变

    #鼠标离开组件事件
    def leave(self,event):
        event.widget['bg'] = list(self.colorthemes.values())[self.themesvar.get()][0]   #背景颜色还原

if __name__ == '__main__':
    Todo()