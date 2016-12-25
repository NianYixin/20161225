# -*- coding: utf-8 -*-
import win32api
import win32con
import win32gui
import win32process
import subprocess
import time
import win32com.client
import ctypes


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_int),
                ('top', ctypes.c_int),
                ('right', ctypes.c_int),
                ('bottom', ctypes.c_int)]


class WindowController(object):
    '''
    some method provided for gui to control the application by hwnd
    user win32
    '''
    def __init__(self):
        '''
        self._opended_app is a dict. a message in opened_app contain:
            app_name :(precessid,  hwnd, ClassName, WindowText)
            data_type:(int       , int , string   , string)
        someday will append the function to add a file path to the custom_app
        '''
        self._opened_app={}
        self._rect = RECT()
        self._shell = win32com.client.Dispatch("WScript.Shell")
    def set_self_top(self,title):

        def callback (hwnd, hwnds):
            if win32gui.IsWindowVisible (hwnd) and \
               win32gui.IsWindowEnabled(hwnd) and \
               win32gui.GetClassName(hwnd)==r'TkTopLevel' and \
               win32gui.GetWindowText(hwnd)==title:
                   
                hwnds.append(hwnd)

            return True
        
        hwnds = [ ]
        win32gui.EnumWindows (callback, hwnds)
        if len(hwnds)==1:
            self.set_top(hwnds[0])
    
    
        
    def _search_from_wmi(self,app_name):
        print('info from _search_from_wmi')
        name=app_name.split("\\")[-1]
        process_wmi={}
        wmi=win32com.client.GetObject('winmgmts:')
        
        for p in wmi.InstancesOf('win32_process'):
            if p.name not in process_wmi:
                process_wmi[p.Name]=p.Properties_('ProcessId')
        
        if name in process_wmi:
            process=process_wmi[name]
            hwnds=self._filter_hwnds_by_pid(int(process))

            if len(hwnds)<1:
                return -1

            self._opened_app[app_name]=(int(process),hwnds[0],
                                        win32gui.GetClassName(hwnds[0]),
                                        win32gui.GetWindowText(hwnds[0]))
            return hwnds[0]
        else:
            return -1

    def _check_app_exist(self,app_name):
        '''
        a process create by this may closed by user
        if both hwnd and pid exist,and the hwnd's creater is the process pid
        I judge the process is still alive
        but if user open a application doesn't by this app, what should I do
        how can I judge if the exist?
        '''
        if app_name not in self._opened_app:
            return False
        try:
            class_name=win32gui.GetClassName(self._opened_app[app_name][1])
        except:
            class_name=None
        try:
            pid_number=win32process.GetWindowThreadProcessId(self._opened_app[app_name][1])[1]
        except:
            pid_number=None
        if self._opened_app[app_name][0]==pid_number and \
           self._opened_app[app_name][2]==class_name:
            return True
        else:
            return False

    def _invoke_app(self,app_name):
        '''
        
        '''
        print('come on')
        hwnd=self._opened_app[app_name][1]
        now=win32gui.GetForegroundWindow()
        self._hide_window(now)

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)

    def _show_window(self,hwnd):
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(self._rect))
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST,
                              self._rect.left,
                              self._rect.top,
                              self._rect.right-self._rect.left,
                              self._rect.bottom-self._rect.top,
                              win32con.SWP_NOSENDCHANGING|win32con.SWP_SHOWWINDOW)
    def _hide_window(self,hwnd):
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(self._rect))
        win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM,
                              self._rect.left,
                              self._rect.top,
                              self._rect.right-self._rect.left,
                              self._rect.bottom-self._rect.top,
                              win32con.SWP_NOSENDCHANGING|win32con.SWP_SHOWWINDOW)

    def set_top(self,hwnd=0):
        #hwnd=win32gui.GetForegroundWindow()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(self._rect))
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                              self._rect.left,
                              self._rect.top,
                              self._rect.right-self._rect.left,
                              self._rect.bottom-self._rect.top,
                              win32con.SWP_NOSENDCHANGING|win32con.SWP_SHOWWINDOW)
    def cancal_top(self,hwnd=0):
        #hwnd=win32gui.GetForegroundWindow()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(self._rect))
        win32gui.SetWindowPos(hwnd, win32con.HWND_DOTTOPMOST,
                              self._rect.left,
                              self._rect.top,
                              self._rect.right-self._rect.left,
                              self._rect.bottom-self._rect.top,
                              win32con.SWP_NOSENDCHANGING|win32con.SWP_SHOWWINDOW)
        
        
    def _sendSpacebar():
        win32api.keybd_event(0x20,0,0,0)     
        win32api.keybd_event(0x20,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
    def _sendEnter():
        win32api.keybd_event(0x0d,0,0,0)     
        win32api.keybd_event(0x0d,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键


    def _stop_or_start(self,app_name):
        pass

    def _filter_hwnds_by_pid (self,pid):
        def callback (hwnd, hwnds):
            if win32gui.IsWindowVisible (hwnd) and \
               win32gui.IsWindowEnabled(hwnd):
                found_pid = win32process.GetWindowThreadProcessId(hwnd)[1]

                if found_pid == pid:
                    hwnds.append (hwnd)
            return True
        
        hwnds = [ ]
        win32gui.EnumWindows (callback, hwnds)
        return hwnds

    def open_applicaiton(self,app,file=''):
        '''
        open a application may spend a lot of time ,
        so I should found a method to solve the problem that the precess can't
        get the true hwnd

        when !file, try to invoke a exist process
        '''
        if file==None or file=='':
            if self._check_app_exist(app):
                print('exist')
                self._invoke_app(app)

                return
                
            exist_pid=self._search_from_wmi(app)
            print(exist_pid,'exist_pid')
            if exist_pid!=-1:
                print('wim_exist',exist_pid)
                self._invoke_app(app)

                return
        
        print('open a new process')
        process=subprocess.Popen([app,file])
        time.sleep (3.0)
        hwnds=self._filter_hwnds_by_pid(int(process.pid))
        if len(hwnds)>0:
            hwnd=hwnds[0]
            self._opened_app[app]=(process.pid,hwnd,win32gui.GetClassName(hwnd),win32gui.GetWindowText(hwnd))

    
    def listen(self):
        pass

if __name__ == '__main__':
    tfile=r'E:\迅雷下载\9931722-1hd.mp4'
    qt="C:\Program Files (x86)\Tencent\QQPlayer\QQPlayer.exe"
    n=WindowController()
    
    #n.open_applicaiton(qt,tfile)
    #time.sleep(0.5)
    #print(n._opened_app)
    #n.open_applicaiton(qt)
    
    webapp=r"C:\Users\Administrator\AppData\Roaming\360se6\Application\360se.exe"
    n.open_applicaiton(webapp)
#    web=r"http://www.python.org"
#    n.open_applicaiton(webapp,web)


