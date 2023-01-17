from bs4 import BeautifulSoup
import requests
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import schedule
import time

#Todays Date
today = date.today()
formated_day = date.strftime(today, "%m/%d/%Y")

# Market Watch URL
url = "https://www.marketwatch.com/tools/earnings-calendar"
result = requests.get(url)
doc = BeautifulSoup(result.text, "html.parser")

#Date Parser
today_date = doc.find_all("div", {"data-tab-pane":formated_day})

#Table Parser
earnings_table = today_date[0].find("table", {"id":"risk-table"})
updated_earnings_table = earnings_table.find_all("tr")[1:]

#Create array of company data
earnings_array = []
def create_company_dictionary(row):
    company = {
        "Name": row.find_all("a")[0].string,
        "Symbol": row.find_all("a")[-1].string,
        "Fiscal Quarter": row.find_all("td")[-4].find("div").string,
        "EPS Forecast": row.find_all("td")[-3].find("div").string,
        "EPS Actual": row.find_all("td")[-2].find("div").string,
        "Surprise": row.find_all("td")[-1].find("div").string
    }
    earnings_array.append(company)
    return
#Create dictionary for each company
for row in updated_earnings_table:
    create_company_dictionary(row)
   
#email body
table_rows = []
for company in earnings_array:
    table_row = "<tr><td>" + str(company.get('Name')) + "</td><td>" + str(company.get('Symbol')) + "</td><td>" + str(company.get('Fiscal Quarter')) + "</td><td>" + str(company.get('EPS Forecast')) +  "</td><td>" + str(company.get('EPS Actual')) + "</td><td>" +str(company.get('Surprise'))+ "</td></tr>"
    table_rows.append(table_row)

email_body = f"""
<html>
    <head>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                font-family: Arial, Helvetica, sans-serif;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}

            p {{
                font-size: 14px;
                font-weight: normal;
                margin: 0 0 10px;
                text-align: center;
            }}

            h1 {{
                font-size: 24px;
                font-weight: normal;
                margin: 10px 0;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>Earnings Report</h1>
        <p>Companies Reporting earnings on {formated_day}</p>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Symbol</th>
                    <th>Fiscal Quarter</th>
                    <th>EPS Forecast</th>
                    <th>EPS Actual</th>
                    <th>Surprise</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </body>
</html>
"""

# email send
email_list = []
def send_email():
    for email in email_list:
        message = MIMEMultipart()
        message["from"] = "Jack Scanlan"
        message["to"] = email
        message["subject"] = f"Earning Reports for {formated_day}"
        message.attach(MIMEText(email_body, "html"))
        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login("scansdev@gmail.com", "tneaohmsafvuczhi")
            smtp.send_message(message)
            print("Sent...")
    return
    

schedule.every().day.at("07:00").do(send_email,)
while True:
    schedule.run_pending()
    time.sleep(60)
    
