#!/usr/bin/env python3
#coding=utf-8

import sys

from multiprocessing import Process,Queue

queue2 = Queue()
queue3 = Queue()

config = {} #存储社保比例配置信息

# 获取配置文件的内容
def get_cfg_file(configfile):
        cfg_file = configfile
        # 打开社保比例配置文件，读取配置信息，存储到config字典
        with open(cfg_file) as file:
            for line in file:
                # 去掉空格
                ss_line = line.replace(" ","")
                s_line = ss_line.strip()
                # 分割字符串
                f_line = s_line.split("=",1) 
                # 去掉空行
                if f_line != [""]:
                    config[f_line[0]] = f_line[1]

class UserData(Process):
    """用户类，计算工资并写入指定文件"""
    def __init__(self,userdatafile):
        self.usr_file = userdatafile
        
    #计算税后工资 
    def run(self):
        #userdata = {}  ＃用来存储用户数据
 
        with open(self.usr_file) as file:
            for line in file:
                # 去掉空格
                ss_line = line.replace(" ","")
                s_line = ss_line.strip()
                # 分割字符串
                f_line = s_line.split(",",1) 
                # 去掉空行
                if f_line != [""]:
                    #通过yield关键字，实现生成器，逐行返回并处理数据
                    yield queue1.put(f_line)
                    #将用户数据存储到userdata字典里
                    #userdata[f_line[0]] = f_line[1]
        queue1.task_done()

class CalSolution(Process):
        """
        进程二
        计算类
        计算社保金额，个税金额，税后工资
        
        """
    def __init__(self):
	#读取社保比例信息
        try:
            self.low = float(config['JiShuL'])
            self.high = float(config['JiShuH'])
            self.x_yl = float(config['YangLao'])
            self.x_yiliao = float(config['YiLiao'])
            self.x_shiye = float(config['ShiYe'])
            self.x_gs = float(config['GongShang'])
            self.x_shengyu = float(config['ShengYu'])
            self.x_gjj = float(config['GongJiJin']) 
            self.x_sb = (self.x_yl+self.x_shiye+self.x_gs
                    +self.x_shengyu+self.x_gjj+self.x_yiliao)
        except TypeError:
            print("type error")        

    def run(self):
        u_data = queue1.get()
        #计算五险一金的基数
        try:
            u_data[2] = float(u_data[2])
            if u_data[2] < self.low:
                j_shu = self.low
            elif u_data[2] > self.high:
                j_shu = self.high
            else:
                j_shu = u_data[2] 
            sb = j_shu * self.x_sb
            t = u_data[2] - sb - 3500
            if t < 0: tax = 0
            elif t<=1500: tax = t * 0.03
            elif t<=4500: tax = t * 0.1 - 105
            elif t<=9000: tax = t * 0.2 - 555
            elif t<=35000: tax = t * 0.25 - 1005
            elif t<=55000: tax = t * 0.3 - 2755
            elif t<=80000: tax = t * 0.35 - 5505
            else: tax = t * 0.45 -13505
            # 将数据修改为2位小数的数字形式字符串
            
            #社保金额
            sb_d = format(sb,'.2f')
            #税收金额
            tax_d = format(tax,'.2f')
            #税后工资
            mon = u_data[2] - tax - sb
            shgz_d = format(mon,'.2f')
            #税前工资
            sqgz_d = format(u_data[2],'.0f') 
            info_list=[u_data[1],sqgz_d,sb_d,tax_d,shgz_d]
            queue2.put(info_list)

        except TypeError:
            print("type error2")
                
class DumpFile(Process):
    #将计算结果写入指定文件
    def __init__(self,outputfile):
        self.outputfile=outputfile

    def run(self):
        w_list = queue2.get()            
        #存储格式：工号，税前工资，社保金额，个税金额，税后工资
        with open(self.outputfile,'w') as file:
            for item in w_list:
                for i in item:
                    file.write(i)
                    if item.index(i)<len(item)-1:
                        file.write(",")
                file.write("\n")
        	


def main():
    args = sys.argv[1:]
    
    index_c = args.index('-c')
    cfg_file = args[index_c+1]

    index_d = args.index('-d')
    usr_file = args[index_d+1]
    
    index_o = args.index('-o')
    gz_file = args[index_o+1]

    

    con = Config(cfg_file)
    u = UserData(usr_file,con)

    #p1 = Process(target=u.get_info,args=(queue2,))
    #p2 = Process(target=u.write_solution,args=(queue2,queue3))
    #p3 = Process(target=u.dumptofile,args=(gz_file,queue3))

    p1.start()
    p1.join()

    p2.start()
    p2.join()

    p3.start()
    p3.join()
				
if __name__=='__main__':
    main()

