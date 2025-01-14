import requests


url = "https://app.repli360.com/public/admin/template-render"
payload = {
  "site_id": "1682",
  "action": "",
  "ready_script": "dom_load",
  "template_type": "",
  "source": "",
  "property_id": ""
}
print(url)
proxy_url = "http://brd-customer-hl_ceb3d9f9-zone-datacenter_proxy1:a9iprakm5w98@brd.superproxy.io:33335"
response = requests.post(url, data=payload, proxies={"http": proxy_url, "https": proxy_url})
if response.status_code != 200:
  raise Exception(f'Failed to get floor plans: {response.status_code} | {response.text}')
  # Parse the HTML response using BeautifulSoup
print(response.text)
