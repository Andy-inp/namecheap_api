#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
from namecheap_api import *


while True:
    Menu = input("\n\t\t \033[4m功能说明\033[0m\n\n"
                   "\t\033[34m1\033[0m \t本地生成csr和key文件(可生成单根或通配)\n"
                   "\t\033[34m2\033[0m \t查询功能\n"
                   "\t\033[34m3\033[0m \t购买、激活证书\n"   #返回本次激活域名的所有dns解析，需手动操作，后续调用dnspodapi自行处理
                   "\t\033[34m4\033[0m \t完全获取crt、key、cer文件\n"
                   "\t\033[34m5\033[0m \t1-4完整操作，并返回本次操作的域名证书压缩包(未实现)\n"
                   "\t\033[34m6\033[0m \t退出\n\n"
                   "请输入您要操作任务的序号：")



# t = Certificate_Operation()       #本地生成csr和key文件
# t.Create_keycsr()
# Command = 'namecheap.users.getBalances'   #获取余额
# t = Namecheap_User()
# t.get_balance(Command)
# Command = 'namecheap.ssl.create'   #购买证书
# t = Namecheap_SSL()
# t.Create_ssl(Command)
# Command = 'namecheap.ssl.activate'   #激活证书
# t = Namecheap_SSL()
# l = t.Get_list('namecheap.ssl.getList', 'NewPurchase')
# t.Active_ssl(Command, l)
# Command = 'namecheap.ssl.getList'   #获取证书列表和激活状态
# t = Namecheap_SSL()
# t.Get_list(Command, 'NewPurchase')
# t.Get_list('namecheap.ssl.getList', 'Active')
# Command = 'namecheap.ssl.getInfo'   #获取crt并合成cer，完成3个证书
# t = Namecheap_SSL()
# l, d = t.Get_list('namecheap.ssl.getList', 'Active')
# t.CRT_CER(Command, l, d)



# if __name__ == '__main__':
#     pass
