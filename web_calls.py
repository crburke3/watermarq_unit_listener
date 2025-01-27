import re
from bs4 import BeautifulSoup
import helpers
from Unit import Unit
import random
import requests


class FloorPlan:
    def __init__(self, name, id_, type_):
        self.name = name
        self.id = id_
        self.type = type_

    def __eq__(self, other):
        if not isinstance(other, FloorPlan):
            return False
        return self.name == other.name and self.id == other.id

    def __hash__(self):
        return hash((self.name, self.id))

    def __repr__(self):
        return f"FloorPlan(name={self.name!r}, id={self.id!r})"




def extract_parameters(onclick_string):
    match = re.search(r"getUnitListByFloor\((.*?)\);", onclick_string)
    if match:
        # Extract the parameter string
        param_str = match.group(1)
        # Split the parameters by commas and strip extra spaces or quotes
        parameters = [param.strip(" '\"") for param in param_str.split(",")]
        return parameters
    return []


def getFloorPlansHtml() -> str:
    url = "https://app.repli360.com/public/admin/template-render"
    payload = {
        "site_id": "1682",
        "action": "",
        "ready_script": "dom_load",
        "template_type": "",
        "source": "",
        "property_id": ""
    }
    print(f"requesting floor plans: {url}")
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f'Failed to get floor plans: {response.status_code} | {response.text}')
        # Parse the HTML response using BeautifulSoup
    return response.text


def getFloorPlansHtmlProxy(proxy_url: str=None) -> str:
    print(f"using proxy to gather floor plans: {proxy_url}")
    url = "https://app.repli360.com/public/admin/template-render"
    payload = {
      "site_id": "1682",
      "action": "",
      "ready_script": "dom_load",
      "template_type": "",
      "source": "",
      "property_id": ""
    }
    if proxy_url:
        response = requests.post(url, data=payload, proxies={"http": proxy_url, "https": proxy_url})
    else:
        response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f'Failed to get floor plans: {response.status_code} | {response.text}')
    return response.text


def getAvailableFloorplans(proxy_url: str=None) -> [FloorPlan]:
    # html = getFloorPlansHtml()
    html = getFloorPlansHtmlProxy(proxy_url)
    soup = BeautifulSoup(html, 'html.parser')
    parent_div = soup.find('div', id='all_available_tab')
    if not parent_div:
        print("Failed to find parent div. heres where we were trying to find it")
        print(html)
        raise Exception(f'failed to find parent div from floor plans. web resp: {html}')
    # Find all div elements inside the parent div
    div_elements = parent_div.find_all('div')
    # parse each floor plan
    floor_plans: [FloorPlan] = []
    for div in div_elements:
        floor_plan_name = None
        floor_plan_id = None
        floor_plan_type = None
        h2 = div.find('h2')
        if h2:
            floor_plan_name = h2.get_text(strip=True)
            # print("Extracted Text:", floor_plan_name)
        else:
            continue
        all_text: str = div.get_text(separator=' ', strip=True)
        if ("|" in all_text):
            parts = all_text.split("|")
            floor_plan_type = f"{parts[0].strip()} {parts[1].strip()} {parts[2].strip()}"
        # Gind the buttons
        buttons = div.find_all('a', class_="btn btn-primary")
        for button in buttons:
            onClick = button.get('onclick')
            if onClick:
                btn_text = button.get_text(strip=True)
                if btn_text == 'View Availability':
                    on_click_params = extract_parameters(onClick)
                    floor_plan_id = on_click_params[0]
            else:
                print("No onClick function found for this button.")
        if not floor_plan_type:
            print(f"Failed to find floor plan type: {floor_plan_name}")
        new_unit = FloorPlan(name=floor_plan_name, id_=floor_plan_id, type_=floor_plan_type)
        if not new_unit.id:
            continue
        floor_plans.append(new_unit)
    floor_plans = list(set(floor_plans))
    sorting_shit = sorted(floor_plans, key=lambda floor_plan: floor_plan.name, reverse=False)
    return sorting_shit




def getUnitListByFloor(floorPlan: FloorPlan, moveinDate, site_id="1682", template_type="2", mode="", type_="2d", currentanuualterm="",
                       AcademicTerm="", RentalLevel="", proxy_url: str=None):
    url = "https://app.repli360.com/public/admin/getUnitListByFloor"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {
        "floorPlanID": floorPlan.id,
        "moveinDate": moveinDate,
        "site_id": site_id,
        "template_type": template_type,
        "mode": mode,
        "type": type_,
        "currentanuualterm": currentanuualterm,
        "AcademicTerm": AcademicTerm,
        "RentalLevel": RentalLevel
    }

    if proxy_url:
        print(f"Using proxy to gather {floorPlan.name} data: {proxy_url}")
        response = requests.post(url, headers=headers, data=payload, proxies={"http": proxy_url, "https": proxy_url})
    else:
        response = requests.post(url, headers=headers, data=payload)
    try:
        response.raise_for_status()
        resp_json = response.json()
        resp_html = resp_json['str']
        soup = BeautifulSoup(resp_html, 'html.parser')
        housing_rows = soup.find_all('tr')
        units: [Unit] = []
        for row in housing_rows:
            try:
                cells = row.find_all('td')  # Find all <td> elements (cells) in the row
                row_text = [cell.get_text(strip=True) for cell in cells]  # Extract text and strip whitespace
                if "Unit Number" not in row_text[0]: continue
                number = row_text[0].replace("Unit Number", "")
                price = row_text[1].replace("Starting At", "")
                availabilty = row_text[2].replace("Availability", "")
                unit_for_row = Unit(unit_number=number, price=price, availability_date=availabilty)
                helpers.add_csv_data(unit_for_row)
                unit_for_row.floor_plan_type = floorPlan.type
                units.append(unit_for_row)
            except Exception as e:
                continue
        return set(units)
    except Exception as e:
        raise Exception(f'Failed to pull floor plan {floorPlan.name} | {response.status_code} | {response.text} | {e}')

