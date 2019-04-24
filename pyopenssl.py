import requests
import xmltodict
from OpenSSL import crypto


class Common(object):

    def __init__(self, api_user=None, api_key=None, username=None, client_ip=None, test=True):
        """
        :param api_user:  调用namecheap API 时所需的 ApiUser
        :param api_key:   调用namecheap API 时所需的 ApiKey
        :param username:  调用namecheap API 时所需的 UserName, 若不传入，默认和ApiUser相同
        :param client_ip: 调用namecheap API 时所需的 ClientIp
        :param test:      布尔值，True：沙箱测试环境 ；False 正式环境
        """
        self.ApiUser = api_user
        self.ApiKey = api_key
        self.UserName = username if username else api_user
        self.ClientIp = client_ip
        self.test = test

        if self.test:
            self.url = "https://api.sandbox.namecheap.com/xml.response"
        else:
            self.url = "https://api.namecheap.com/xml.response"

        self.data = {
            "ApiUser": self.ApiUser,
            "ApiKey": self.ApiKey,
            "UserName": self.UserName,
            "ClientIp": self.ClientIp,
        }


class ACCOUNT(Common):

    def get_balances(self):
        return_data = dict()
        self.data["Command"] = "namecheap.users.getBalances"

        try:
            r = requests.post(self.url, data=self.data, json=True)
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
                available_balance = result_dict["ApiResponse"]["CommandResponse"]["UserGetBalancesResult"][
                    "@AvailableBalance"]
                return_data["data"] = f"{currency} {available_balance}"
            return return_data


class SSL(Common):

    def create(self, Type=None, Years=None):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.create"
        self.data["Type"] = Type
        self.data["Years"] = Years

        try:
            r = requests.post(self.url, data=self.data, json=True)
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
                data = dict()
                create_result = result_dict["ApiResponse"]["CommandResponse"]["SSLCreateResult"]

                data["IsSuccess"] = create_result["@IsSuccess"]
                data["ChargedAmount"] = create_result["@ChargedAmount"]

                create_info = create_result["SSLCertificate"]

                data["CertificateID"] = create_info["@CertificateID"]
                data["Created"] = create_info["@Created"]
                data["SSLType"] = create_info["@SSLType"]
                data["Years"] = create_info["@Years"]
                data["Status"] = create_info["@Status"]

                return_data["data"] = data
            return return_data

    def getinfo(self, CertificateID=None, returncertificate=True, returntype="Individual"):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.getInfo"

        self.data["CertificateID"] = CertificateID
        self.data["returncertificate"] = returncertificate
        self.data["returntype"] = returntype

        try:
            r = requests.post(self.url, data=self.data, json=True)
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
                data = dict()

                ssl_info = result_dict["ApiResponse"]["CommandResponse"]["SSLGetInfoResult"]

                data["Status"] = ssl_info["@Status"]
                data["Type"] = ssl_info["@Type"]
                data["IssuedOn"] = ssl_info["@IssuedOn"]
                data["Years"] = ssl_info["@Years"]
                data["Expires"] = ssl_info["@Expires"]
                data["ActivationExpireDate"] = ssl_info["@ActivationExpireDate"]
                data["OrderId"] = ssl_info["@OrderId"]

                # 更加证书不同的状态返回不同的信息
                if data["Status"] in ["newpurchase", ]:
                    return_data["data"] = data
                    return return_data

                if data["Status"] in ["purchased", ]:
                    ssl_details = result_dict["ApiResponse"]["CommandResponse"]["SSLGetInfoResult"]["CertificateDetails"]
                    data["CSR"] = ssl_details["CSR"]
                    data["CommonName"] = ssl_details["CommonName"]
                    data["AdministratorEmail"] = ssl_details["AdministratorEmail"]
                    return_data["data"] = data
                    return return_data
                else:
                    ssl_details = result_dict["ApiResponse"]["CommandResponse"]["SSLGetInfoResult"]["CertificateDetails"]
                    data["CSR"] = ssl_details["CSR"]
                    data["CommonName"] = ssl_details["CommonName"]
                    data["AdministratorEmail"] = ssl_details["AdministratorEmail"]

                    if self.data["returncertificate"]:
                        # 是否返回证书
                        data["CertificateReturned"] = ssl_details["Certificates"]["@CertificateReturned"]
                        data["ReturnType"] = ssl_details["Certificates"]["@ReturnType"]
                        # 证书详细信息

                        data["crt"] = ssl_info["CertificateDetails"]["Certificates"]["Certificate"]

                        ca_info = ssl_info["CertificateDetails"]["Certificates"]["CaCertificates"]["Certificate"]

                        # 沙箱测试环境下，不返回EV OV 证书
                        if self.test:
                            data["ca1"] = ca_info["Certificate"]
                        else:
                            data["ca1"] = ca_info[0]["Certificate"]
                            data["ca2"] = ca_info[1]["Certificate"]
                            data["ca3"] = ca_info[2]["Certificate"]
                    return_data["data"] = data
                    return return_data

    def getlist(self, PageSize=20, CurrentPage=1, SortBy="EXPIREDATETIME_DESC", ListType=None, SearchTerm=None):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.getList"
        self.data["PageSize"] = PageSize
        self.data["CurrentPage"] = CurrentPage
        self.data["SortBy"] = SortBy
        self.data["ListType"] = ListType
        self.data["SearchTerm"] = SearchTerm


        try:
            r = requests.post(self.url, data=self.data, json=True)
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
                data = list()
                list_result = result_dict["ApiResponse"]["CommandResponse"]["SSLListResult"]["SSL"]

                if not isinstance(list_result, (list,)):
                    tmp = [list_result, ]
                    list_result = tmp

                for obj in list_result:
                    item = {}
                    for k, v in obj.items():
                        item[k.strip("@")] = v
                    data.append(item)
                return_data["data"] = data
            return return_data

    def activate(self, CertificateID=None, CSR=None, AdminEmailAddress=None, WebServerType=None, DNSDCValidation=True, ApproverEmail=None):
        return_data = dict()
        self.data["Command"] = "namecheap.ssl.activate"
        self.data["CertificateID"] = CertificateID
        self.data["CSR"] = CSR
        self.data["AdminEmailAddress"] = AdminEmailAddress
        self.data["WebServerType"] = WebServerType
        self.data["DNSDCValidation"] = DNSDCValidation
        self.data["ApproverEmail"] = ApproverEmail

        try:
            r = requests.post(self.url, data=self.data, json=True)
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
                active_result = result_dict['ApiResponse']['CommandResponse']['SSLActivateResult']
                active_dns_info = active_result["DNSDCValidation"]['DNS']

                data["IsSuccess"] = active_result["@IsSuccess"]
                data["DNSDCValidation"] = active_result["DNSDCValidation"]["@ValueAvailable"]
                data["Domain"] = active_dns_info["@domain"]
                data["HostName"] = active_dns_info["HostName"]
                data["Target"] = active_dns_info["Target"]
                return_data["data"] = data
            return return_data


def create_key_and_csr(**name):
    """
        Create a certificate request.
        Arguments: pkey   - The key to associate with the request
                   digest - Digestion method to use for signing, default is md5
                   **name - The name of the subject of the request, possible
                            arguments are:
                              C     - Country name
                              ST    - State or province name
                              L     - Locality name
                              O     - Organization name
                              OU    - Organizational unit name
                              CN    - Common name
                              emailAddress - E-mail address
    """
    digest = "md5"
    _key = crypto.PKey()
    mykey = _key.generate_key(crypto.TYPE_RSA, 2048)

    req = crypto.X509Req()
    subj = req.get_subject()
    for (key, value) in name.items():
        setattr(subj, key, value)
    req.set_pubkey(_key)
    req.sign(_key, digest)

    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, _key).decode("utf-8")
    public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, _key).decode("utf-8")
    csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode("utf-8")

    return private_key, public_key, csr


# 用例
if __name__ == "__main__":

    # 1 获取余额
    user = ACCOUNT(api_user="sapaytest", api_key="e56162800f824dee910173a364de5409", client_ip="103.24.94.53", test=True)
    print(user.get_balances())

    # 证书相关
    # ssl = SSL(api_user="sapaytest", api_key="e56162800f824dee910173a364de5409", client_ip="103.24.94.53", test=True)

    # 创建证书
    # myssl = ssl.create(Type="EssentialSSL Wildcard", Years=2)

    # CertificateID = myssl["data"]["CertificateID"]

    # 获取证书列表(按照证书状态 ListType 查询时，不区分大小写,"active", "newpurchase", "all", and so on....)
    # print(ssl.getlist(ListType="all"))

    # 生成公钥 私钥 并创建CSR请求
    # info = {
    #     "C": "HK",
    #     "ST": "HK",
    #     "L": "HK",
    #     "O": "HK",
    #     "OU": "HK",
    #     "CN": "*.test.com",
    #     "emailAddress": "map@test.com",
    # }

    # a, b, c = create_key_and_csr(**info)

    # 激活证书 提交的CSR请求中 单根还是通配 要与证书本身的类型一致
    # print(ssl.activate(
    #         CertificateID=CertificateID,
    #         CSR=c,
    #         AdminEmailAddress="map@test.com",
    #         WebServerType="nginx",
    #         DNSDCValidation=True
    #     )
    # )

    # 证书详情 若证书状态为新购买，则返回数据中无证书相关信息
    # print(ssl.getinfo(CertificateID=1069126))


