class quest:
    def __init__(self,init=0):
        sign=0
        self.ret=0
        self.init=init
        self.proxy=""
        self.error=None
        try:
            if self.init==0:
                import httpx as qx
                self.qx=qx
            elif self.init==1:
                import httpx
                http_client = httpx.Client(timeout=20, transport=httpx.HTTPTransport(retries=10), follow_redirects=True,
                                   **kwargs)
                self.qx=http_client
            else:
                raise Exception
            sign=1
            print('[+]using httpx for base quest')
        except:
            if self.init==0:
                import requests as qx
                self.qx=qx
            elif self.init==1:
                print('load')
                import requests
                from requests.adapters import HTTPAdapter
                http_client = requests.Session()
                http_client.mount('http://', HTTPAdapter(max_retries=10))
                http_client.mount('https://', HTTPAdapter(max_retries=10))
                self.qx=http_client
                print(self.qx)
            else:
                raise Exception('method not allowd')
            sign=2
            print('[+]using requests for base quest')
        finally:
            if sign==0:
                print('[-]you need install requests or httpx')
    def __del__(self):
        pass
    def __str__(self):
        self.text=self.ret.text
        return self.text
    def __bytes__(self):
        self.content=self.ret.content
        return self.content
    def __getattribute__(self, str):
        attr_value = object.__getattribute__(self, str)
        return attr_value
    def __getitem__(self,index):
        try:
            return self.js[index]
        except Exception as e:
            if self.error==None:
                self.error=self.ret.text+"\n"+str(e)
            return None
    def __contains__(self,ele):
        try:
            return self.js[ele]
        except:
            return None
    def pre_ready(self):
        self.error=None
        if self.proxy.find("http") == -1:
            self.proxy="http://"+self.proxy
        if self.proxy=="http://":
            self.proxy=""
    def get(self,url):
        self.pre_ready()
        try:
            self.ret = self.qx.get(url,proxies={'http': self.proxy, 'https': self.proxy})
        except Exception as e:
            if self.error==None:
                self.error=str(e)
        return self
    def post(self,url,postdata):
        self.pre_ready()
        try:
            self.ret = self.qx.post(url,proxies={'http': self.proxy, 'https': self.proxy},params=postdata)
        except Exception as e:
            if self.error==None:
                self.error=str(e)
    def post_json(self,url,json):
        self.pre_ready()
        try:
            self.ret = self.qx.post(url,proxies={'http': self.proxy, 'https': self.proxy},json=json)
        except Exception as e:
            if self.error==None:
                self.error=str(e)

        return self
    def json(self):
        if self.error!=None:
            return self
        import json
        try:
            self.text=self.ret.text
            self.js= json.loads(self.text)
        except Exception as e:
            if self.error==None:
                self.error=self.text+"\n"+str(e)
        return self
    def set_proxy(self,proxy=None):
        #self.proxy="127.0.0.1:58952"
        #return self
        if proxy!=None:
            self.proxy=proxy
        else:
            self.proxy=self.get_proxy()
        return self
    def get_proxy(self):
        import os
        ps=os.getenv('http_proxy')
        if ps==None:
            ps=os.getenv('https_proxy')
        if ps==None:
            ps=os.getenv('proxy')
        if ps==None:
            return ""
        return ps
    def get_json(self):
        if self.error!=None:
            return None
        self.json()
        return self.js
    def get_error(self):
        return self.error
if __name__ =='__main__':
    request = quest(1)
    ret=request.set_proxy().get(url="https://api.live.bilibili.com/ip_service/v1/ip_service/get_ip_addr?ip=1.1.1.1").json()
    code=ret['code']
    if code==None:
        print(ret.get_error())
    else:
        print(code)
