

基于DNSlog修改：

https://github.com/BugScanTeam/DNSLog

基于docker的自动化部署：

http://www.code2sec.com/shi-yong-dockerda-jian-dnslogfu-wu-qi-pythonban-kai-yuan-cloudeyede-bu-shu.html

https://github.com/bit4woo/code2sec.com/blob/master/%E4%BD%BF%E7%94%A8docker%E6%90%AD%E5%BB%BAdnslog%E6%9C%8D%E5%8A%A1%E5%99%A8%EF%BC%9Apython%E7%89%88%E5%BC%80%E6%BA%90cloudeye%E7%9A%84%E9%83%A8%E7%BD%B2.md



API接口调用：

```
http://127.0.0.1:8000/apilogin/{username}/{password}/
http://127.0.0.1:8000/apilogin/test/123456/
#登陆以获取token

http://127.0.0.1:8000/apiquery/{logtype}/{subdomain}/{token}/
http://127.0.0.1:8000/apiquery/dns/test/a2f78f403d7b8b92ca3486bb4dc0e498/
#查询特定域名的某类型记录

http://127.0.0.1:8000/apidel/{logtype}/{udomain}/{token}/
http://127.0.0.1:8000/apidel/dns/test/a2f78f403d7b8b92ca3486bb4dc0e498/
#删除特定域名的某类型记录
```



changelog:

2018-01-16：修改api接口的返回内容为实际的数据而不再简单是True or False; 

2018-01-16：新增3个API接口实现：登陆获取token、带token查询特定记录、带token删除特定记录

2019-04-16：调整显示格式，显示整个http请求的请求头

2019-07-22：调整记录的显示顺序，最新的记录显示在最前面