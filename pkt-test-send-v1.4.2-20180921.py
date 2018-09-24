# -*- coding: utf-8 -*-
#jazhu@hillstonenet.com
#2018-6-10
#v1.4
#根据用户提供数据创建数据包并发送出去
import csv
import logging
import time
import random
import threading
import re
import wx
import wx.xrc
import traceback
import sqlite3
import webbrowser
import IPy
#界面类代码
class MyFrame ( wx.Frame ):
	version='1.4.2'
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"发包测试工具-发送端v"+self.version, pos = wx.DefaultPosition, size = wx.Size( 800,620 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetExtraStyle( wx.FRAME_EX_METAL )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		table = wx.GridBagSizer( 0, 0 )
		table.SetFlexibleDirection( wx.BOTH )
		table.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.file = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"选择模板文件", u"*.*", wx.DefaultPosition, wx.Size( 440,-1 ), wx.FLP_DEFAULT_STYLE )
		self.file.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		self.file.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		
		table.Add( self.file, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self, wx.ID_ANY, u"发送数据包", wx.DefaultPosition, wx.Size( 160,-1 ), wx.NO_BORDER )
		self.m_button1.SetFont( wx.Font( 11, 74, 90, 92, False, "微软雅黑" ) )
		self.m_button1.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
		self.m_button1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTIONTEXT ) )
		
		table.Add( self.m_button1, wx.GBPosition( 1, 6 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( 50,-1 ), wx.TE_CENTRE )
		self.m_textCtrl2.SetFont( wx.Font( 11, 70, 90, 90, False, "微软雅黑" ) )
		self.m_textCtrl2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		
		table.Add( self.m_textCtrl2, wx.GBPosition( 1, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"发包间隔:", wx.DefaultPosition, wx.Size( -1,30 ), wx.ALIGN_CENTRE )
		self.m_staticText1.Wrap( -1 )
		self.m_staticText1.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		
		table.Add( self.m_staticText1, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.show = wx.TextCtrl( self, wx.ID_ANY, u"使用说明：\n1、根据模板填写csv内容，选择csv文件后点击发送数据包按钮即可；\n2、程序在发包时候会将csv中的内容作为data部分进行发送，接收端会通过data部分识别并打印出收到的数据包信息。 ", wx.DefaultPosition, wx.Size( 760,450 ), wx.TE_MULTILINE )
		table.Add( self.show, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 6 ), wx.ALL, 5 )
		
		#self.capbtn = wx.Button( self, wx.ID_ANY, u"捕获数据包", wx.DefaultPosition, wx.Size( 160,-1 ), wx.NO_BORDER)
		#self.capbtn.SetFont( wx.Font( 11, 74, 90, 92, False, "微软雅黑" ) )
		#self.capbtn.SetForegroundColour( wx.Colour( 255, 255, 255 ) )
		#self.capbtn.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INACTIVECAPTIONTEXT ) )
		
		#table.Add( self.capbtn, wx.GBPosition( 2, 6 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		#self.stopcap = wx.Button( self, wx.ID_ANY, u"停止", wx.DefaultPosition, wx.DefaultSize, 0 )
		#table.Add( self.stopcap, wx.GBPosition( 2, 5 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		#self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"抓包规则：", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		#self.m_staticText2.Wrap( -1 )
		#self.m_staticText2.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		
		#table.Add( self.m_staticText2, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		#self.exp = wx.TextCtrl( self, wx.ID_ANY, u"tcp or udp or icmp", wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
		#self.exp.SetFont( wx.Font( 11, 74, 90, 90, False, "微软雅黑" ) )
		#table.Add( self.exp, wx.GBPosition( 2, 2 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
		
		self.gaugebar = wx.Gauge( self, wx.ID_ANY, 0, wx.DefaultPosition, wx.Size( 750,-1 ), wx.GA_HORIZONTAL )
		table.Add( self.gaugebar, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 6 ), wx.ALL, 5 )
		
		
		self.SetSizer( table )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button1.Bind( wx.EVT_BUTTON, self.dotest )
		#self.capbtn.Bind( wx.EVT_BUTTON, self.startcap )
		#self.stopcap.Bind( wx.EVT_BUTTON, self.capstop )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def dotest( self, event ):
		self.m_button1.Enable(False)
		#frame.capbtn.Enable(False)
		t=threading.Thread(target=dotest,args=(self.m_textCtrl2.GetValue()))
		t.start()
	

	#输出发送结果
	def report(self):
		pass



			

html='<!DOCTYPE html><html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />'\
		'<title>发送端-测试报告</title><style type="text/css">'\
		'body {margin:0px;padding:0px;font-size:12px;line-height:22px;}'\
		'.model_table {background:#fff;border:1px solid #CCC;}'\
		'.model_table th {background:#ccc;color:#666;text-align:left;padding:0 5px;}'\
		'.model_table td {background:#f2f2f2;text-align:left;padding:0 5px;}'\
		'.title {height:60px;clear:both;margin:0 20px;border-bottom:3px solid #6fc144;}'\
		'.title_text {border-bottom:3px solid #0d4c99;border-right:3px solid #FFF;float:left;'\
		'line-height:60px;font-family:"Arial Black", Gadget, sans-serif;font-size:22px;font-weight:bold;'\
		'color:#0d4c99;text-align:left;width:260px;}'\
		'.title_time {float:right;text-align:right;line-height:60px;padding-right:15px;vertical-align:bottom;color:#999;}'\
		'</style><body><div class=title><div class=title_text>发送端-测试报告</div><div class=title_time>'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'</div></div>'\
		'<br><div style="overflow-x: auto; overflow-y: auto;  width:98%;margin:0 20px;">'\
		'<table cellspacing="1" cellpadding="1" border="0" class="model_table" width="98%"> <tbody>'\
		'<tr><th>ID</th><th>源地址</th><th>目标地址</th><th>服务</th><th>描述</th><th>结果</th></tr>'

#随机从地址段中取地址
def randomip(ip):
	ipall=IPy.IP(ip)
	if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}',ip):
		if int(ip[-2:])<32:
			addr=str(ipall[random.randint(1,ipall.len()-1)])
		else:
			addr=ip[:-3]
	else:
		addr = ip
	return addr
#执行发包函数
def dotest(t):
    frame.show.Clear()  
    frame.show.AppendText('加载scapy模块，这里需要点时间！请耐心等待！\n')
    from  scapy.all import IP,ICMP,UDP,TCP,send
    report_file='send_report'+str(int(time.time()))+'.html'
    report=open(report_file,'w',encoding='utf-8')
    global html
    report.write(html)
    #判断是否为csv文件
    if len(frame.file.GetPath())>0:
        policy_Filename = frame.file.GetPath()#获取csv文件路径
    else:
        frame.show.AppendText('请选择csv文件或数据库文件！！！\n')
        frame.m_button1.Enable()
        exit()
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='scapy.log',
                    filemode='w')
    frame.show.AppendText('读取 '+policy_Filename+' 文件中....\n')
    #print(re.match('\.csv',str(policy_Filename)))
    if '.csv' in policy_Filename[-4:]:
        policy_File = open(policy_Filename)
        policy_Reader = csv.reader(policy_File)
        policy_Data = list(policy_Reader)
        i=1
    elif '.db' in policy_Filename[-3:]:
        conn=sqlite3.connect(policy_Filename )
        c=conn.cursor()
        sql='select * from packet'
        c.execute(sql)
        policy_Data=c.fetchall()
        conn.commit()
        conn.close()
        i=0
    else:
        frame.show.AppendText('只支持csv或db文件！\n')
        frame.m_button1.Enable()
        exit()		
    frame.show.AppendText('读取完成！共计'+str(len(policy_Data)-i)+'条规则\n开始发送数据包.....\n')
    #预定义常用服务端口
    sysdefine={'ssh':'tcp-22','ftp':'tcp-21','mysql':'tcp-3306','sqlnet':'tcp-1521','icmp':'icmp-2048',
              'http':'tcp-80','https':'tcp-443','http-ext':'tcp-8080','radius':'udp-1812','dns':'udp-53',
             'snmp':'udp-161','ntp':'udp-123','ping':'icmp-2222','sftp':'tcp-22','telnet':'tcp-23',
             'rdp':'tcp-3389','pop3':'tcp-110','smtp':'tcp-25','mssql':'tcp-1411','pptp':'tcp-1721'
              }
    #进度条
    #frame.gaugebar.Pulse()
    frame.gaugebar.SetRange(len(policy_Data)-1)
    #frame.gaugebar.SetShadowWidth(len(policy_Data))
    for row in range(i,len(policy_Data)):
        if t:
            time.sleep(int(t))
        frame.gaugebar.SetValue(row)
        try:
            id=policy_Data[row][0]
            policy_srcadd=policy_Data[row][1]
            policy_dstadd=policy_Data[row][2]
            #判断地址格式，如果是网段则最随机地址进行发包
            src_addr=randomip(policy_srcadd)
            #判断目标地址的格式，如果是网段则取随机地址
            dst_addr=randomip(policy_dstadd)
            src_port = random.randint(1024, 65535)
            #根据预定义的服务使用对应的端口发包
            policy_service=policy_Data[row][3]
            if re.match('\w{1,4}-\d{1,5}',policy_service):
                s=policy_service.split('-')
                service=s[0]
                dst_port=int(s[1])
            else:
                ser=sysdefine[policy_service.lower()]
                s=ser.split('-')
                service=s[0]
                dst_port=int(s[1])
            description=''#描述字段，暂未启用
            ipLayer = IP(src=src_addr, dst=dst_addr)#构造数据包的源目地址
            dataload = 'hs_send_pkt ID '+str(id)+' '+policy_srcadd+' '+policy_dstadd+' '+policy_service+' '+str(description)  #发送数据包的data内容
            #发送ICMP包
            if 'icmp' in str(service).lower() or 'ping' in str(service).lower():
                #ipLayer = IP(src=src_addr, dst=dst_addr)
                packet = ipLayer/ICMP()/str(dataload)
                send(packet)
                frame.show.AppendText('ID:'+str(id)+' '+src_addr+'---->'+dst_addr+' icmp包发送成功！\n')
                frame.show.AppendText('数据包内容：'+dataload[11:] + '\n')
                report.write('<tr><td>'+str(id)+'</td><td>'+policy_srcadd+'</td><td>'+policy_dstadd+'</td><td>'+policy_service+'</td><td>'+str(policy_service)+'</td><td>'+str(description)+'</td><td style="color:#090;">发送成功</td></tr>')
                logging.info(src_addr+','+str(src_port)+','+dst_addr+',icmp'+',success')
                continue


            elif 'udp' in str(service).lower():
                #ipLayer = IP(src=src_addr, dst=dst_addr)
                udpLayer = UDP(sport=src_port, dport=dst_port)
                packet = ipLayer / udpLayer/str(dataload)
                send(packet)
                frame.show.AppendText('ID:'+id+' '+src_addr+':'+str(src_port)+'---->'+dst_addr+':'+str(dst_port)+' UDP包发送成功！\n')
                frame.show.AppendText('数据包内容：' + dataload[11:] + '\n')
                logging.info(src_addr+','+str(src_port)+','+dst_addr+',UDP_'+str(dst_port)+',success')
                report.write('<tr><td>'+str(id)+'</td><td>'+policy_srcadd+'</td><td>'+policy_dstadd+'</td><td>'+policy_service+'</td><td>'+str(description)+'</td><td style="color:#090;">发送成功</td></tr>')
                continue

            elif 'tcp' in str(service).lower():                
                tcpLayer = TCP(sport=src_port, dport=dst_port, flags="S")
                packet = ipLayer / tcpLayer/str(dataload)
                send(packet)
                frame.show.AppendText('ID:'+str(id)+' '+src_addr+':'+str(src_port)+'---->'+dst_addr+':'+str(dst_port)+' TCP包发送成功！\n')
                report.write('<tr><td>'+str(id)+'</td><td>'+policy_srcadd+'</td><td>'+policy_dstadd+'</td><td>'+policy_service+'</td><td>'+str(description)+'</td><td style="color:#090;">发送成功</td></tr>')
                frame.show.AppendText('数据包内容：' + dataload[11:] + '\n')
                logging.info(src_addr+','+str(src_port)+','+dst_addr+',TCP_'+str(dst_port)+',success')
                continue
           
            else:
                tcpLayer = TCP(sport=src_Port, dport=dst_port, flags="S")
                packet = ipLayer / tcpLayer/str(dataload)
                send(packet)
                frame.show.AppendText('ID:'+id+' '+src_addr+':'+src_port+'---->'+dst_addr+dst_port+' 未知协议包发送成功！\n')
                report.write('<tr><td>'+str(id)+'</td><td>'+policy_srcadd+'</td><td>'+policy_dstadd+'</td><td>'+policy_service+'</td><td>'+str(description)+'</td><td style="color:#090;">发送成功</td></tr>')
                logging.info(src_addr+','+str(src_port)+','+dst_addr+',TCP_'+str(dst_port)+',success')
        
        except Exception as e:
            traceback.print_exc(file=open('pkt-error.log','a'))
            frame.show.AppendText('ID:'+str(id)+' '+policy_Data[row][1]+':'+str(src_port)+'---->'+policy_Data[row][2]+':'+str(dst_port)+' '+policy_Data[row][3]+'包发送失败!!!!!!\n')
            logging.info(policy_Data[row][1]+','+str(src_port)+','+policy_Data[row][2]+','+policy_Data[row][3]+',fail')
            report.write('<tr><td>'+str(id)+'</td><td>'+str(policy_Data[row][1])+'</td><td>'+str(policy_Data[row][2])+'</td><td>'+policy_service+'</td><td>'+str(description)+'</td><td style="color:#ff0000;">失败</td></tr>')
        #send(IP(dst="192.168.31.1")/ICMP())
    frame.show.AppendText('\n数据包发送完毕！\n报告已生成！\n')
    frame.m_button1.Enable()
    report.write('</tbody></table></div></body></html>')
    report.close()
    #get=wx.MessageBox('数据包发送完毕！是否打开报告？', "测试报告" ,wx.YES_NO | wx.ICON_INFORMATION)
    #if get==wx.YES:
    webbrowser.open(report_file)




#程序开始
app = wx.App()
frame = MyFrame(None)
frame.Show(True)
app.MainLoop() 



