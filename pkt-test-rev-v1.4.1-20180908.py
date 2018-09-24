# -*- coding: utf-8 -*-
#jazhu@hillstonenet.com
#2018-6-10
#v1.2
#支持发包和收包功能
import csv
import logging
import time
import random
import threading
import wx
import wx.xrc
import traceback
from scapy.all import *
import webbrowser
#界面类代码
class MyFrame ( wx.Frame ):
	version='1.4.1'
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"发包测试工具-接收端v"+self.version, pos = wx.DefaultPosition, size = wx.Size( 800,620 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.FRAME_EX_METAL )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		table = wx.GridBagSizer( 0, 0 )
		table.SetFlexibleDirection( wx.BOTH )
		table.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.show = wx.TextCtrl( self, wx.ID_ANY, u"使用说明：\n1、用于抓取发包工具发出的数据包； ", wx.DefaultPosition, wx.Size( 760,480 ), wx.TE_MULTILINE )
		table.Add( self.show, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 6 ), wx.ALL, 5 )
		
		self.capbtn = wx.Button( self, wx.ID_ANY, u"捕获数据包", wx.DefaultPosition, wx.Size( 160,-1 ), wx.NO_BORDER)
		self.capbtn.SetFont( wx.Font( 11, 74, 90, 92, False, "微软雅黑" ) )
		self.capbtn.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
		self.capbtn.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTIONTEXT ) )
		
		table.Add( self.capbtn, wx.GBPosition( 1, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.stopcap = wx.Button( self, wx.ID_ANY, u"查看报告", wx.DefaultPosition, wx.DefaultSize, 0 )
		table.Add( self.stopcap, wx.GBPosition( 1, 5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"抓包规则：", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText2.Wrap( -1 )
		self.m_staticText2.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		
		table.Add( self.m_staticText2, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.exp = wx.TextCtrl( self, wx.ID_ANY, u"tcp or udp or icmp", wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
		self.exp.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		table.Add( self.exp, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
		
		
		
		self.SetSizer( table )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		#self.m_button1.Bind( wx.EVT_BUTTON, self.dotest )
		self.capbtn.Bind( wx.EVT_BUTTON, self.startcap )
		self.stopcap.Bind( wx.EVT_BUTTON, self.capstop )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class	
	def startcap( self, event ):
		runcap()
	
	def capstop( self, event ):
		runstop()

	
#停止抓包暂未解决
def runstop():
    #frame.m_button1.Enable()
    global report_file
    #get=wx.MessageBox('数据包发送完毕！是否打开报告？', "测试报告" ,wx.YES_NO | wx.ICON_INFORMATION)
    #if get==wx.YES:
    webbrowser.open(report_file)
    frame.capbtn.Enable()     
#启动抓包线程    
def runcap():
    #frame.m_button1.Enable(False)
    frame.capbtn.Enable(False)
    #ex=list(frame.exp.GetValue())
    t=threading.Thread(target=cap)
    t.start()

#report_file='rev_report'+str(int(time.time()))+'.html'
html='<!DOCTYPE html><html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />'\
		'<title>接收端-测试报告</title><style type="text/css">'\
		'body {margin:0px;padding:0px;font-size:12px;line-height:22px;}'\
		'.model_table {background:#fff;border:1px solid #CCC;}'\
		'.model_table th {background:#ccc;color:#666;text-align:left;padding:0 5px;}'\
		'.model_table td {background:#f2f2f2;text-align:left;padding:0 5px;}'\
		'.title {height:60px;clear:both;margin:0 20px;border-bottom:3px solid #6fc144;}'\
		'.title_text {border-bottom:3px solid #0d4c99;border-right:3px solid #FFF;float:left;'\
		'line-height:60px;font-family:"Arial Black", Gadget, sans-serif;font-size:22px;font-weight:bold;'\
		'color:#0d4c99;text-align:left;width:260px;}'\
		'.title_time {float:right;text-align:right;line-height:60px;padding-right:15px;vertical-align:bottom;color:#999;}'\
		'</style><body><div class=title><div class=title_text>接收端-测试报告</div><div class=title_time>'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'</div></div>'\
		'<br><div style="overflow-x: auto; overflow-y: auto; max-height:400px; width:98%;margin:0 20px;">'\
		'<table cellspacing="1" cellpadding="1" border="0" class="model_table" width="98%"> <tbody>'\
		'<tr><th>ID</th><th>源地址(原始源地址)</th><th>目标地址(原始目标地址)</th><th>协议</th><th>端口(原始端口)</th><th>描述</th><th>结果</th></tr>'

report_file='rev_report'+str(int(time.time()))+'.html'
#开始抓包    
def cap():
    frame.show.Clear()
    frame.show.AppendText('开始抓包.....\n')
    global report_file
    global html
    rt=open(report_file,'w',encoding='utf-8')
    rt.write(html)
    rt.close()
    sniff(filter=str(frame.exp.GetValue()),prn=packet_callback)

#回调函数，过滤包内容中含有hillstone_send_packet字符的包并打印到界面
def packet_callback(packet):
    if hasattr(packet,'load'):
        if 'hs_send_pkt' in  str(packet.load):
            global report_file
            report=open(report_file,'a',encoding='utf-8')
            id=1
            playload=str(packet.load)[13:-1]
            plist=playload.split()
            if len(plist)>6:
                d=plist[6].encode('raw_unicode_escape')
                description=d.decode()
            else:
                description=''
            if int(packet.proto)==6:
                frame.show.AppendText(str(packet[IP].src)+':'+str(packet[TCP].sport)+'-->'+str(packet[IP].dst)+':'+str(packet[TCP].dport)+' \n 数据包内容:'+playload+'\n')
                report.write('<tr><td>'+str(plist[1])+'</td><td>'+str(packet[IP].src)+'('+plist[2]+')</td><td>'+str(packet[IP].dst)+'('+plist[3]+')</td><td>tcp'+'('+plist[4]+')</td><td>'+str(packet[TCP].dport)+'('+plist[5]+')</td><td>'+description+'</td><td style="color:#090;">成功捕获</td></tr>')
            if int(packet.proto)==1:
                frame.show.AppendText(str(packet[IP].src)+'-->'+str(packet[IP].dst)+' \n 数据包内容:'+playload+'\n')
                report.write('<tr><td>'+str(plist[1])+'</td><td>'+str(packet[IP].src)+'('+plist[2]+'</td><td>'+str(packet[IP].dst)+'('+plist[3]+')</td><td>icmp</td><td>any</td><td>'+description+'</td><td style="color:#090;">成功捕获</td></tr>')
            if int(packet.proto)==17:
                frame.show.AppendText(str(packet[IP].src)+':'+str(packet[UDP].sport)+'-->'+str(packet[IP].dst)+':'+str(packet[UDP].dport)+'  \n数据包内容:'+playload+'\n')
                report.write('<tr><td>'+str(plist[1])+'</td><td>'+str(packet[IP].src)+'('+plist[2]+')</td><td>'+str(packet[IP].dst)+'('+plist[3]+')</td><td>udp'+'('+plist[4]+')</td><td>'+str(packet[UDP].dport)+'('+plist[5]+')</td><td>'+description+'</td><td style="color:#090;">成功捕获</td></tr>')
            report.close()


#程序开始
app = wx.App()
frame = MyFrame(None)
frame.Show(True)
app.MainLoop() 





