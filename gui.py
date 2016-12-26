# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 23:12:15 2016

@author: Administrator
"""
import xml.dom.minidom as minidom
import xml.parsers.expat as expat
import tkinter as Tk
import sys
import tkinter.filedialog as filedialog
import manager.listener as listener



class ConfigDom(object):
    def __init__(self):
        self.applayout=['browser','player','app_1','app_2','app_3','app_4']
        self.filename='config.xml'
        self.dom=self._exception_handle(self._getdom)
#        print('dom:',self.dom)

    def _exception_handle(self,func, *params, **paramMap):
        try:
            return func(*params, **paramMap)
        except (FileNotFoundError,expat.ExpatError):
            return self._initialxmlfile()

        except :
            print("Unexpected error:", sys.exc_info()[0])
            raise


    def _getdom(self):
        return minidom.parse(self.filename)
    def _initialxmlfile(self):
        impl = minidom.getDOMImplementation()
        newdom = impl.createDocument(None, 'AppConfig' , None)
        root = newdom.documentElement
        root.setAttribute('AppName','Application-Helper')
        root.setAttribute('verson','v1.0')

        applications=newdom.createElement('applications')
        root.appendChild(applications)

        for each in self.applayout:
            application=newdom.createElement('application')
            application.setAttribute('layout',each)
            application.appendChild(self._addattribute(newdom,'source'
                                                       ,'filepath',''))
            application.appendChild(self._addattribute(newdom,'icon'
                                                       ,'filepath',''))
            applications.appendChild(application)
#        application.appendChild(self.editnode(newdom,'source',''))
#        application.appendChild(self.editnode(newdom,'icon',''))
#        application.appendChild(self.editnode(newdom,'history',''))
        voice=newdom.createElement('voice')
        root.appendChild(voice)
        '''
        I want to use a assignment to initial the self.dom.
        I also want to use a  exception handling function.
        I also also want to write dom to the file
        sooooo, I assign the self.dom two times in self.dom=newdom
            and self.dom= return newdom
        '''
        self.dom=newdom
        self._writefile()
#        print('newdom:',newdom)
        return newdom

    def _addtext(self,dom,tagname,text):
        '''
        create a node like:<name>text</name>
        '''
        node=dom.createElement(tagname)
        nodetext=dom.createTextNode(text)
        node.appendChild(nodetext)
        return node

    def _addattribute(self,dom,nodename,atrname,value):
        node=dom.createElement(nodename)
        node.setAttribute(atrname,value)
        return node
    def _eidttext(self,dom,tagname,text):
        pass
    def _editattribute(self,dom,atrname,value):
        pass
    def _writefile(self):
        '''
        In minidom the '\n' also is a TEXT_NODE, so the xml file will
        be biger and biger:-) In the process of reading and writing over and
        over again if I use newl = '\n'.
        maybe I can open the file after xmlwrite and delete '\n',
        but it's difficult to update the dom.
        I also think about use removeChild to delete them layer by layer.
        And my soul ASK me: are you kidding me?
        '''
        f = open(self.filename, 'w', encoding='utf-8')
        self.dom.writexml(f, addindent = '' , newl = '' ,encoding = 'utf-8' )
        f.close()


    #this methods are provided to gui
    def change_application(self,layout,target):
        applications=self.dom.getElementsByTagName('application')
        application=applications[0]
        for each in applications:
            if each.getAttribute('layout')==layout:
                application=each
                break
        source=application.getElementsByTagName('source')
        source[0].setAttribute('filepath',target)

        self._writefile()

    def change_history(self,layout,target):
        applications=self.dom.getElementsByTagName('application')
        application=applications[0]
        for each in applications:
            if each.getAttribute('layout')==layout:
                application=each
                break
        history=application.getElementsByTagName('history')
        if len(history)<3:
            application.appendChild(self._addtext(self.dom,'history',target))
        else:
            #if the len(history)>3, this code does not word
            application.removeChild(history[0])
            application.appendChild(self._addtext(self.dom,'history',target))

        self._writefile()

    def record_sound(self,function,target):
        pass

    def load_application(self):
        '''
        return a dict
        '''
        applications=self.dom.getElementsByTagName('application')
        apps={}
        for each in applications:
            layout=each.getAttribute('layout')
            source=each.getElementsByTagName('source')[0]
            filepath=source.getAttribute('filepath')
            apps[layout]=filepath

        return apps
        
    def load_icon(self):
        applications=self.dom.getElementsByTagName('application')
        apps={}
        for each in applications:
            layout=each.getAttribute('layout')
            source=each.getElementsByTagName('icon')[0]
            filepath=source.getAttribute('filepath')
            apps[layout]=filepath

        return apps
        
    def load_history(self,layout):
#        print('layout:',layout)
        '''
        return a list
        '''
        applications=self.dom.getElementsByTagName('application')
#        print('applications',applications)
#        application=applications[3]
        for each in applications:
#            print('?????',each.getAttribute('layout'),layout)
            if each.getAttribute('layout')==layout:
#                print('i get you')
                application=each
                break
        history=application.getElementsByTagName('history')
        print('164:history:',history)
        if len(history)==0:
            return []
        historyfile=[]
        for each in history:
            historyfile.append(each.childNodes[0].data)

        return historyfile



#this is a window used to config
class SetFrame(Tk.Toplevel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, original):
        """Constructor"""
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.geometry(self.set_initial_position())
        self.title("SetFrame")

        self.set_weight(self)

    def set_initial_position(self):
        ori_x=self.original_frame.root.winfo_x()
        ori_y=self.original_frame.root.winfo_y()
        return '{0}x{1}+{2}+{3}'.format(self.original_frame.size_x,
                                        self.original_frame.size_y,
                                        ori_x,ori_y)
    def set_weight(self,root):
        canvas = Tk.Canvas(root)
        canvas.configure(width = self.original_frame.size_x)
        canvas.configure(height = self.original_frame.size_y)
        canvas.configure(bg = "blue")
        canvas.configure(highlightthickness = 0)

        global BACKGROUND
        canvas.create_image(0,0,anchor='nw',image=BACKGROUND)
        canvas.place(x=0, y=0, anchor='nw')
        canvas.bind("<Button-3>",self.close)
        
        self.create_custom_applications(root)
        self.create_builtin_application(root)

    def create_custom_applications(self,root):
        first_line=['app_1','app_2','app_3','app_4']
        global IMAGEADD1
        label_x=self.original_frame.margin
        label_y=self.original_frame.margin
        
        for each in first_line:
            label_image=self.original_frame.appicon[each] \
                     if self.original_frame.appicon[each]!=None and \
                        self.original_frame.appicon[each]!='' else IMAGEADD1
            self.create_application_label(root,label_x,label_y,label_image,each)
            label_x+=self.original_frame.interval
    
    def create_application_label(self,root,label_x,label_y,label_image,app):
        lb01 = Tk.Label(root, image=label_image,
                        height=self.original_frame.buttonsize,
                        width=self.original_frame.buttonsize) 
        lb01.place(x=label_x, y=label_y, anchor='nw')
        lb01.bind(r"<Button-1>",lambda event:self.set_custom_source(layout=app))
        lb01.bind(r"<Button-3>",lambda event:self.set_custom_icon(layout=app))
    def create_builtin_application(self,root):
        global IBROWSERVOICE
        global IPLAYERVOICE
        global ISTOPVOICE
        global IMAGEHI
        
        lb10 = Tk.Label(root, image=IBROWSERVOICE,
                        height=self.original_frame.buttonsize,
                        width=self.original_frame.buttonsize) 
        lb10.place(x=self.original_frame.margin, 
                   y=self.original_frame.margin+self.original_frame.interval, anchor='nw')
        lb10.bind(r"<Button-1>",self.record_sound)
        
        lb11 = Tk.Label(root, image=IPLAYERVOICE,
                        height=self.original_frame.buttonsize,
                        width=self.original_frame.buttonsize) 
        lb11.place(x=self.original_frame.margin+self.original_frame.interval,
                   y=self.original_frame.margin+self.original_frame.interval, anchor='nw')
        lb11.bind(r"<Button-1>",self.record_sound)
        
        lb12 = Tk.Label(root, image=ISTOPVOICE,
                        height=self.original_frame.buttonsize,
                        width=self.original_frame.buttonsize) 
        lb12.place(x=self.original_frame.margin+2*self.original_frame.interval,
                   y=self.original_frame.margin+self.original_frame.interval, anchor='nw')
        lb12.bind(r"<Button-1>",self.record_sound)
        
        lb13 = Tk.Label(root, image=IMAGEHI,
                        height=self.original_frame.buttonsize,
                        width=self.original_frame.buttonsize) 
        lb13.place(x=self.original_frame.margin+3*self.original_frame.interval,
                   y=self.original_frame.margin+self.original_frame.interval, anchor='nw')
        lb13.bind(r"<Button-1>",self.record_sound)
        
        
    #----------------------------------------------------------------------
    def set_custom_source(self,layout):
        pass
    def set_custom_icon(self,layout):
        pass
    def record_sound(self,purpose):
        pass
    #----------------------------------------------------------------------
    def close(self,event):
        """"""
        self.destroy()
        self.original_frame.show()


#this is a window used to open some file by a application
class OpenFrame(Tk.Toplevel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, original,layout):
        """Constructor"""
        self.original_frame = original
        Tk.Toplevel.__init__(self)
        self.geometry(self.set_initial_position())
        self.title("SetFrame")
        self.bind(r"<Button-3>",self.close)
        self.app_layout=layout
        self.application=self.original_frame.applications[layout]
        self.history=self.original_frame.domclass.load_history(layout)
#        print('history'+str(self.history))

        canvas = Tk.Canvas(self)
        canvas.configure(width = self.original_frame.size_x)
        canvas.configure(height = self.original_frame.size_y)

        global BACKGROUND
        canvas.create_image(0,0,anchor='nw',image=BACKGROUND)
        canvas.place(x=0, y=0, anchor='nw')
        self.create_lables()
        
    def create_lables(self):
        y_position=15
        for each in self.history[::-1]:
            self.create_label(each,y_position)
            y_position+=52
            
        btn=Tk.Button(self,
                      text='OTHER',
                      font=("宋体", 15, "normal"),anchor='center',
                      width=6,
                      height=1,
                      borderwidth=2,
                      relief='groove',
                      command=self.open_other_file)
        btn.place(x=252,y=118,anchor='nw')

    def set_initial_position(self):
        ori_x=self.original_frame.root.winfo_x()
        ori_y=self.original_frame.root.winfo_y()
        return '{0}x{1}+{2}+{3}'.format(self.original_frame.size_x,
                                        self.original_frame.size_y,
                                        ori_x,ori_y)
    def create_label(self,content,position):
        lb=Tk.Label(self,
                    text=self.modify_filename(content),
                    font=("宋体", 12, "normal"),anchor='nw',
                    justify='left',
                    state='normal',
                    wraplength=230,
                    width=28,
                    height=2,
                    background=r"#fcf1db")
        lb.place(x=10,y=position,anchor='nw')
        lb.bind(r"<Button-1>",  lambda event:self.open_history_file(content))
        lb.bind(r"<Enter>",    lambda event:self.enter_label(weight=lb))
        lb.bind(r"<Leave>",    lambda event:self.leave_label(weight=lb))
        
    def modify_filename(self,filename):
        name=filename.split('/')
        name=[name[-1],' from: ']+list(map(lambda x:x+'/', name[:-1]))
        return ''.join(name)

            
    #some method to function
    def enter_label(self,weight):
        weight.configure(font=("宋体", 13, "underline"),
                         foreground='green')
    def leave_label(self,weight):
        weight.configure(font=("宋体", 12, "normal"),
                         foreground='black')
    def open_history_file(self,filename):
        print('will open a history file',filename)
        self.original_frame.winclass.open_applicaiton(self.application,
                                                      file=filename)
        self.close()
        
    def open_other_file(self):
        print('will open a new file')
        newhistory=filedialog.askopenfilename()
        if newhistory!=None and len(newhistory)!=0:
            if newhistory not in self.history:
                self.original_frame.domclass.change_history(self.app_layout,newhistory)
            print(self.history,newhistory)
            self.original_frame.winclass.open_applicaiton(self.application,
                                                          file=newhistory)
            self.close()
            
        
    #----------------------------------------------------------------------
    def close(self,event='have a good night'):
        """"""
        self.destroy()
        self.original_frame.show()

#this is the main window
class MyApp(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        #get dom
        self.winclass=listener.WindowController()
        self.domclass=ConfigDom()
        self.applications=self.domclass.load_application()
        self.appicon=self.domclass.load_icon()
        
        #style
        self.root = parent
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.85)
        self.root.resizable(width = False, height = False)
        
        self.root.title(r"PM:v0.5@2016-12-25")
        
        self.size_x=330
        self.size_y=170
        self.root.geometry(self.set_initial_position(root))
        self.x=0
        self.y=0
        self.margin=15
        self.interval=80    #20+60
        self.buttonsize=60
        self.set_weight(self.root)

        
        self.root.bind(r"<Leave>",self._onleave)
        self.root.bind(r"<Enter>",self._onenter)
        self._hiding=False


        '''
        self.frame = Tk.Frame(parent)
        self.frame.pack()

        btn = Tk.Button(self.frame, text='set',command=self.SetSomething)
        btn.grid(row=0,column=1)
        btn = Tk.Button(self.frame, text='open',command=self.SetSomething)
        btn.grid(row=0,column=2)
        '''
    def guitest(self,event):
        print('a func to test something')
    #some method use for __init__
    def set_weight(self,root):
        canvas = Tk.Canvas(root)
        canvas.configure(width = self.size_x)
        canvas.configure(height = self.size_y)
        canvas.configure(bg = "blue")
        canvas.configure(highlightthickness = 0)
        #here is a crazy problem of canvas:
            #the image and the mainloop should in the same scope
        global BACKGROUND
        canvas.create_image(0,0,anchor='nw',image=BACKGROUND)
        canvas.place(x=0, y=0, anchor='nw')
        canvas.bind("<B3-Motion>",self.move)
        canvas.bind("<Button-3>",self.button_3)
        
        self.create_custom_applications(root)
        self.create_builtin_application(root)

    def _onleave(self,event):
        if self._mouse_in_root(event.x_root,event.y_root):
            self._hiding=False
            print("leave P")
            return
        
        root_right=self.root.winfo_x()+self.root.winfo_width()
        if root_right<self.root.winfo_screenwidth():
            self._hiding=False
            return
        
        self.hide_in_edge()
        self.winclass.set_self_top(r"PM:v0.5@2016-12-25")
        self._hiding=True

        print('you should hide',self._hiding)

        
    def _onenter(self,event):
        print('enter')
        if self._hiding==False:
            return
        self.emerge_from_edge()
        
    def _mouse_in_root(self,x,y):
        w_edge=self.root.winfo_x()
        e_edge=self.root.winfo_x()+self.size_x
        n_edge=self.root.winfo_y()
        s_edge=self.root.winfo_y()+self.size_y

        if w_edge<=x<=e_edge and n_edge<=y<=s_edge:
            return True
        else:
            return False

            
    def hide_in_edge(self,event=''):
        self.root.geometry('{0}x{1}+{2}+{3}'.format(
                            self.size_x,
                                self.size_y,
                                    self.root.winfo_screenwidth()-10,
                                        self.root.winfo_y()))

            
    def emerge_from_edge(self,event=''):
        temp_x=self.root.winfo_screenwidth()-self.root.winfo_width()+5
        self.root.geometry('{0}x{1}+{2}+{3}'.format(
                            self.size_x,
                                self.size_y,
                                    temp_x,
                                        self.root.winfo_y()))
        
    def set_initial_position(self,root):
        scr_x=root.winfo_screenwidth()
        scr_y=root.winfo_screenheight()
        return '{0}x{1}+{2}+{3}'.format(self.size_x,self.size_y,scr_x-450,scr_y-400)

    def create_custom_applications(self,root):
        first_line=['app_1','app_2','app_3','app_4']
        global IMAGEADD1
        label_x=self.margin
        label_y=self.margin
        
        for each in first_line:
            label_image=self.appicon[each] if self.appicon[each]!=None and\
                                 self.appicon[each]!='' else IMAGEADD1
            self.create_application_label(root,label_x,label_y,label_image,each)
            label_x+=self.interval
    
    
    def create_application_label(self,root,label_x,label_y,label_image,app):
        lb01 = Tk.Label(root, image=label_image,
                        height=self.buttonsize,width=self.buttonsize) 
        lb01.place(x=label_x, y=label_y, anchor='nw')
        lb01.bind(r"<Button-1>",lambda event:self.custom_application_left(layout=app))
        lb01.bind(r"<Button-3>",lambda event:self.custom_application_right(layout=app))
    
    def create_builtin_application(self,root):
        global IMAGEBROWSER
        global IMAGEPLAYER
        global IMAGESET1
        global IMAGEQUIT
        
        lb10 = Tk.Label(root, image=IMAGEBROWSER,
                        height=self.buttonsize,width=self.buttonsize) 
        lb10.place(x=self.margin, y=self.margin+self.interval, anchor='nw')
        lb10.bind(r"<Button-1>",self.custom_browser_left)
        
        lb11 = Tk.Label(root, image=IMAGEPLAYER,
                        height=self.buttonsize,width=self.buttonsize) 
        lb11.place(x=self.margin+self.interval,
                   y=self.margin+self.interval, anchor='nw')
        lb11.bind(r"<Button-1>",lambda event:self.custom_application_left(layout='player'))
        lb11.bind(r"<Button-3>",lambda event:self.custom_application_right(layout='player'))
        
        lb12 = Tk.Label(root, image=IMAGESET1,
                        height=self.buttonsize,width=self.buttonsize) 
        lb12.place(x=self.margin+2*self.interval,
                   y=self.margin+self.interval, anchor='nw')
        lb12.bind(r"<Button-1>",self.open_setting_window)
        
        lb13 = Tk.Label(root, image=IMAGEQUIT,
                        height=self.buttonsize,width=self.buttonsize) 
        lb13.place(x=self.margin+3*self.interval,
                   y=self.margin+self.interval, anchor='nw')
        lb13.bind(r"<Button-1>",self.system_quit)
        

    #some method to move the main window
    def move(self,event):
        new_x = (event.x-self.x)+root.winfo_x()
        new_y = (event.y-self.y)+root.winfo_y()
        root.geometry('{0}x{1}+{2}+{3}'.format(self.size_x,self.size_y,new_x,new_y))

    def button_3(self,event):
        self.x,self.y = event.x,event.y

    #some mothed use to change between the windows
    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()
        self.winclass.set_self_top(r"PM:v0.5@2016-12-25")
        
    #open the setFrame. will be used when user click the set button
    def open_setting_window(self,event):
        """"""
        self.hide()
        setWindow = SetFrame(self)
        if 1>2:
            print(setWindow.__doc__)
    #open the openFrame. will be used when user click app they add
    def open_oepnfile_window(self,layout):
        """"""
        self.hide()
        openWindow = OpenFrame(self,layout)
        if 1>2:
            print(openWindow.__doc__)

    def system_quit(self,event):
        self.root.destroy()
        
    def open_application(self,filepath=''):
        pass
    #some method to function #this method bind with four button and use index to distinguish them
    def custom_browser_left(self,event):
        homepage=r"https://www.baidu.com/"
        app=r"C:\Users\Administrator\AppData\Roaming\360se6\Application\360se.exe"
        self.winclass.open_applicaiton(app,file=homepage)

    
    def custom_application_left(self,layout):
        # key-->value
        if self.applications[layout]==None or self.applications[layout]=='':
            self.applications[layout]=filedialog.askopenfilename()
            print(self.applications)
            self.domclass.change_application(layout,self.applications[layout])
        else:
            print('will open the applicaiton',self.applications[layout])
            self.winclass.open_applicaiton(self.applications[layout])

    def custom_application_right(self,layout):
        if self.applications[layout]!=None and self.applications[layout]!='':
#            print('custom_application_right:',self.applications[layout])
#            print('custom_application_right_layout:',layout)
#            print(self.applications[layout]!=None)
#            print(self.applications[layout]!='')
            self.open_oepnfile_window(layout)


#----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk.Tk()
    #the current path, if another program open this file, the code won't work
    import os
    CurrentPath = os.getcwd()
    
    BACKGROUND=Tk.PhotoImage(file=CurrentPath+r'\background.gif')
    IMAGEBROWSER=Tk.PhotoImage(file=CurrentPath+r'\browser1.gif')
    IMAGEPLAYER=Tk.PhotoImage(file=CurrentPath+r'\player1.gif')
    IMAGESET1=Tk.PhotoImage(file=CurrentPath+r'\set1.gif')
    IMAGEADD1=Tk.PhotoImage(file=CurrentPath+r'\add1.gif')
    IMAGEQUIT=Tk.PhotoImage(file=CurrentPath+r'\quit1.gif')
    
    IBROWSERVOICE=Tk.PhotoImage(file=CurrentPath+r'\browservoice.gif')
    IPLAYERVOICE=Tk.PhotoImage(file=CurrentPath+r'\playervoice.gif')
    ISTOPVOICE=Tk.PhotoImage(file=CurrentPath+r'\stop.gif')
    IMAGEHI=Tk.PhotoImage(file=CurrentPath+r'\hi.gif')

    app = MyApp(root)


    root.mainloop()
