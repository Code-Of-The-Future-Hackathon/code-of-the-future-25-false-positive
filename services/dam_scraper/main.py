import requests

url = "https://dams.damtn.government.bg/"

querystring = {"formdata[title]":"","formdata[oblast]":"-1","formdata[obstina]":"PDV01","Itemid":"107","option":"com_webregister","view":"items","tmpl":"none","format":"json","lang":"en","page":"-1","formdata[searchType]":"item","task":"items.getItems"}

response = requests.get(url, params=querystring)

print(response.json())