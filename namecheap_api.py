import json
import shutil
import requests
import xmltodict
from contextlib import ExitStack
import os, re, datetime, logging
from subprocess import Popen, PIPE, STDOUT
from logging.handlers import TimedRotatingFileHandler as _TimedRotatingFileHandler

#目录定义
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Build_DIR = os.path.join(BASE_DIR, 'files/build_file/')
Result_DIR = os.path.join(BASE_DIR, 'files/result_file/')
Backup_DIR = '/opt/backup/'

#日志器
mylogger = logging.getLogger('logger1')
mylogger.setLevel(logging.INFO)
myhandler = _TimedRotatingFileHandler('{}/logs/all_operate.log'.format(BASE_DIR), when='D', backupCount=7)
myhandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [line:%(lineno)d] - %(message)s'))
mylogger.addHandler(myhandler)


'''
测试环境：
  ApiUser = 'api_test'
  ApiKey = 'api_key_test'
  UserName = 'api_test'
  ClientIP = '8.8.8.8'
  AdminEmailAddress = 'testa@gamil.com'
'''

class Common(object):

    def __init__(self, api_user=None, api_key=None, username=None, client_ip=None, test=True):
        self.ApiUser = api_user
        self.ApiKey = api_key
        self.UserName = username if username else api_user
        self.ClientIp = client_ip

        if test:
            self.url = "https://api.sandbox.namecheap.com/xml.response"
        else:
            self.url = "https://api.namecheap.com/xml.response"

        self.data = {
            "ApiUser": self.ApiUser,
            "ApiKey": self.ApiKey,
            "UserName": self.UserName,
            "ClientIp": self.ClientIp,
        }


class User(Common):

    def get_balances(self):
        return_data = {}
        self.data["Command"] = "namecheap.users.getBalances"

        try:
            r = requests.post(self.url, data=self.data)
            result_dict = xmltodict.parse(r.text)
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"{self.url} 连接失败: {e.__str__()}"
            return return_data
        else:
            return_data["status"] = result_dict["ApiResponse"]["@Status"]

            if return_data["status"] == "ERROR":
                error_num = result_dict["ApiResponse"]["Errors"]["Error"]["@Number"]
                error_text = result_dict["ApiResponse"]["Errors"]["Error"]["#text"]
                return_data["msg"] = f"<ERROR Number={error_num} text={error_text}>"
                return_data["data"] = {}
            else:
                return_data["msg"] = "success"
                currency = result_dict["ApiResponse"]["CommandResponse"]["UserGetBalancesResult"]["@Currency"]
                available_balance = result_dict["ApiResponse"]["CommandResponse"]["UserGetBalancesResult"]["@AvailableBalance"]
                return_data["data"] = f"{currency} {available_balance}"
            return return_data


class SSL(Common):

    def create(self, ssl_type=None, years=None):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.create"
        self.data["Type"] = ssl_type
        self.data["Years"] = years

        try:
            r = requests.post(self.url, data=self.data)
            result_dict = xmltodict.parse(r.text)
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"{self.url} 连接失败: {e.__str__()}"
            return return_data
        else:
            return_data["status"] = result_dict["ApiResponse"]["@Status"]

            if return_data["status"] == "ERROR":
                error_num = result_dict["ApiResponse"]["Errors"]["Error"]["@Number"]
                error_text = result_dict["ApiResponse"]["Errors"]["Error"]["#text"]
                return_data["msg"] = f"<ERROR Number={error_num} text={error_text}>"
                return_data["data"] = {}
            else:
                return_data["msg"] = "success"
                data = {}
                create_result = result_dict["ApiResponse"]["CommandResponse"]["SSLCreateResult"]
                create_info = create_result["SSLCertificate"]

                data["IsSuccess"] = create_result["@IsSuccess"]
                data["CertificateID"] = create_info["@CertificateID"]
                data["Created"] = create_info["@Created"]
                data["SSLType"] = create_info["@SSLType"]
                data["Years"] = create_info["@Years"]
                data["Status"] = create_info["@Status"]
                return_data["data"] = data
            return return_data

    def getlist(self, list_type=None, **kwargs):
        '''
        常用查询类型：ALL,Active,NewPurchase
        1、当传入NewPurchase时，本次操作返回一个CertificateID给当前实例激活证书
        2、当传入Active时，本次操作返回一个CertificateID和HostName给当前实例获取crt证书（返回所有激活过的，用HostName过滤要操作的域名）
        '''
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.getList"
        self.data["ListType"] = list_type

        try:
            r = requests.post(self.url, data=self.data)
            result_dict = xmltodict.parse(r.text)
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"{self.url} 连接失败：{e.__str__()}"
            return return_data
        else:
            return_data["status"] = result_dict["ApiResponse"]["@Status"]

            if return_data["status"] == "ERROR":
                error_num = result_dict["ApiResponse"]["Errors"]["Error"]["@Number"]
                error_text = result_dict["ApiResponse"]["Errors"]["Error"]["#text"]
                return_data["msg"] = f"<ERROR Number={error_num} text={error_text}>"
                return_data["data"] = {}
            else:
                return_data["msg"] = "success"
                data = []
                if list_type == 'NewPurchase':
                    getlist_result = result_dict['ApiResponse']['CommandResponse']['SSLListResult']['SSL']
                    getlist_result = json.loads(json.dumps(getlist_result))

                    #返回数据为单个时不是列表，转换一下
                    if isinstance(getlist_result, list):
                        getlist_result = getlist_result
                    else:
                        L = []
                        L.append(getlist_result)
                        getlist_result = L

                    for i in range(len(getlist_result)):
                        data.append(dict())
                        data[i]["CertificateID"] = getlist_result[i]["@CertificateID"]
                        data[i]["SSLType"] = getlist_result[i]["@SSLType"]
                        data[i]["PurchaseDate"] = getlist_result[i]["@PurchaseDate"]
                        data[i]["ExpireDate"] = getlist_result[i]["@ExpireDate"]
                        data[i]["Status"] = getlist_result[i]["@Status"]
                        data[i]["Years"] = getlist_result[i]["@Years"]
                    return_data["data"] = data
                elif list_type == 'Active':
                    getlist_result = result_dict['ApiResponse']['CommandResponse']['SSLListResult']['SSL']
                    getlist_result = json.loads(json.dumps(getlist_result))

                    #返回数据为单个时不是列表，转换一下
                    if isinstance(getlist_result, list):
                        getlist_result = getlist_result
                    else:
                        L = []
                        L.append(getlist_result)
                        getlist_result = L

                    for i in range(len(getlist_result)):
                        data.append(dict())
                        data[i]["CertificateID"] = getlist_result[i]["@CertificateID"]
                        data[i]["SSLType"] = getlist_result[i]["@SSLType"]
                        data[i]["HostName"] = getlist_result[i]["@HostName"]
                        data[i]["PurchaseDate"] = getlist_result[i]["@PurchaseDate"]
                        data[i]["ExpireDate"] = getlist_result[i]["@ExpireDate"]
                        data[i]["IsExpiredYN"] = getlist_result[i]["@IsExpiredYN"]
                        data[i]["Status"] = getlist_result[i]["@Status"]
                        data[i]["Years"] = getlist_result[i]["@Years"]
                    return_data["data"] = data
            return return_data

    def active(self, keytype="nginx" ,email="testa@gmail.com", certificateid=None, csr=None, dnsvalidation=True):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.activate"
        self.data["WebServerType"] = keytype
        self.data["AdminEmailAddress"] = email
        self.data["CertificateID"] = certificateid
        self.data["CSR"] = csr
        self.data["DNSDCValidation"] = dnsvalidation

        try:
            r = requests.post(self.url, data=self.data)
            result_dict = xmltodict.parse(r.text)
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"{self.url} 连接失败：{e.__str__()}"
            return return_data
        else:
            return_data["status"] = result_dict["ApiResponse"]["@Status"]

            if return_data["status"] == "ERROR":
                error_num = result_dict["ApiResponse"]["Errors"]["Error"]["@Number"]
                error_text = result_dict["ApiResponse"]["Errors"]["Error"]["#text"]
                return_data["msg"] = f"<ERROR Number={error_num} text={error_text}>"
                return_data["data"] = {}
            else:
                return_data["msg"] = "success"
                data = {}
                active_result = result_dict['ApiResponse']['CommandResponse']['SSLActivateResult']
                active_dns_info = active_result["DNSDCValidation"]['DNS']

                data["IsSuccess"] = active_result["@IsSuccess"]
                data["DNSDCValidation"] = active_result["DNSDCValidation"]["@ValueAvailable"]
                data["Domain"] = active_dns_info["@domain"]
                data["HostName"] = active_dns_info["HostName"]
                data["Target"] = active_dns_info["Target"]
                return_data["data"] = data
            return return_data

    def getinfo(self, certificateid=None, domain=None):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.getInfo"
        self.data["CertificateID"] = certificateid
        self.data["returncertificate"] = "true"
        crt_file = f"{domain}.crt"
        key_file = f"{domain}.key"
        cer_file = f"{domain}.cer"
        os.chdir(Result_DIR)

        try:
            r = requests.post(self.url, data=self.data)
            result_dict = xmltodict.parse(r.text)
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"{self.url} 连接失败：{e.__str__()}"
            return return_data
        else:
            return_data["status"] = result_dict["ApiResponse"]["@Status"]

            if return_data["status"] == "ERROR":
                error_num = result_dict["ApiResponse"]["Errors"]["Error"]["@Number"]
                error_text = result_dict["ApiResponse"]["Errors"]["Error"]["#text"]
                return_data["msg"] = f"<ERROR Number={error_num} text={error_text}>"
                return_data["data"] = {}
            else:
                return_data["msg"] = "success"
                data = {}
                getinfo_result = result_dict['ApiResponse']['CommandResponse']['SSLGetInfoResult']
                main_crt_info = getinfo_result['CertificateDetails']['Certificates']['Certificate']
                intermediate_crt = getinfo_result['CertificateDetails']['Certificates']['CaCertificates']['Certificate']
                if isinstance(intermediate_crt, list):
                    pass
                else:
                    L = []
                    L.append(intermediate_crt)
                    intermediate_crt = L

                data["Domain"] = domain
                data["status"] = getinfo_result["@StatusDescription"]
                data["Type"] = getinfo_result["@Type"]
                data["IssueOn"] = getinfo_result["@IssuedOn"]
                data["Years"] = getinfo_result["@Years"]
                data["Expires"] = getinfo_result["@Expires"]

                # 备份目录再写入
                Time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                shutil.copytree(Build_DIR, f"{Backup_DIR}build_file_{Time}")
                shutil.copytree(Result_DIR, f"{Backup_DIR}result_file{Time}")
                with open(crt_file, 'w+') as f:
                    f.write(f"{main_crt_info}\n")
                    for i in intermediate_crt:
                        f.write(f"{i['Certificate']}\n")

                shutil.copy2(f"{Build_DIR}{domain}.key", f"{domain}.key")

                with ExitStack() as stack:
                    files = [stack.enter_context(open(fname, 'w+')) if fname == f"{cer_file}" else stack.enter_context(open(fname, 'r+')) for fname in [f"{crt_file}", f"{key_file}", f"{cer_file}"]]
                    for crt in files[0]:
                        files[2].write(crt)
                    for key in files[1]:
                        files[2].write(key)

                data["build_dir_bak"] = f"{Backup_DIR}build_file_{Time}"
                data["result_dir_bak"] = f"{Backup_DIR}result_file_{Time}"
                data["crt_file"] = f"{Result_DIR}{crt_file}"
                data["key_file"] = f"{Result_DIR}{key_file}"
                data["cer_file"] = f"{Result_DIR}{cer_file}"
                data["crt_size"] = os.path.getsize(f"{Result_DIR}{crt_file}")

                return_data["data"] = data
            return return_data


    def parseCSR(self):
        pass

    def _get_key_and_csr(self, domain=None, single=False, only_select=True):
        """
        return key csr:
        """
        return_data = dict()
        key_file = f"{domain}.key"
        csr_file = f"{domain}.csr"
        type = "single" if single else "wildcard"
        os.chdir(Build_DIR)

        try:
            if only_select:
                if not os.path.exists(key_file):
                    return_data["status"] = "Error"
                    return_data["msg"] = f"Domain <{domain}> key file isn't exists, Please check!!!"
                    return return_data
                else:
                    return_data["status"] = "ok"
                    return_data["msg"] = f"select success"

                    data = {}
                    data["Domain"] = domain
                    data["Type"] = type
                    data["csr_file"] = f"{Build_DIR}{csr_file}"
                    data["key_file"] = f"{Build_DIR}{key_file}"
                    return_data["data"] = data
                return return_data
            else:
                if os.path.exists(key_file):
                    return_data["status"] = "Error"
                    return_data["msg"] = f"Domain <{domain}> key file is exists, Please check!!!"
                    return return_data
                else:
                    CN = domain if single else f"*.{domain}"
                    cmd = f""" openssl req -new -newkey rsa:2048 -nodes -keyout {key_file} -out {csr_file} -subj "/C=US/ST=US/L=US/O=US/OU=US/CN={CN}" """
                    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
                    p.wait()

                data = {}
                return_data["status"] = "ok"
                return_data["msg"] = f"build domain <{domain}> csr and key file success"

                data["Domain"] = domain
                data["Type"] = type
                data["csr_file"] = f"{Build_DIR}{csr_file}"
                data["key_file"] = f"{Build_DIR}{key_file}"
                return_data["data"] = data
                return return_data
        except Exception as e:
            return_data["status"] = "ERROR"
            return_data["msg"] = f"Error info: {e.__str__()}"
        else:
            pass



# 用例
if __name__=="__main__":
    # 获取余额
    # user = User(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # print(user.get_balances())

    # 购买证书
    # ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # print(ssl.create(ssl_type='EssentialSSL Wildcard', years='2'))

    # 查询证书信息
    # ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # print(ssl.getlist(list_type='NewPurchase'))
    # ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # print(ssl.getlist(list_type='Active'))

    # 生成csr和key文件
    # ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # print(ssl._get_key_and_csr(domain="testaaa.com", only_select=False))

    # 激活证书
    # ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    # cid = "1066746"   #certificateid从getList手动选择（getList返回数据选择单根或通配、一年或两年的证书  选择要激活的cid）
    # with open(ssl._get_key_and_csr(domain="testaaa.com", only_select=True)["data"]["csr_file"], "r") as f:
    #     csr = f.read()
    # print(ssl.active(certificateid=cid, csr=csr, dnsvalidation=True))

    # 获取crt，合成cer
    ssl = SSL(api_user="api_test", api_key="api_key_test", client_ip="8.8.8.8", test=True)
    cid = "1234567"  #从getList拿到所有已激活的cid，选择所要的cid和domain
    print(ssl.getinfo(certificateid=cid, domain="testaaa.com"))


