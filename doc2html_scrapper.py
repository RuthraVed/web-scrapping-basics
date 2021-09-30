import os
import requests
import csv
import re
import mammoth
import pandas as pd
from dicttoxml import dicttoxml
from bs4 import BeautifulSoup
from datetime import datetime
from os.path import exists as file_exists

base_dir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists("scrapped_datafiles"):
    os.makedirs("scrapped_datafiles")
filepath = os.path.join(base_dir, "scrapped_datafiles/")
csv_courts_filename = "california_courts_scrapping_"
csv_casefiles_filename = "casefile_details_"
date_stamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")


def navigate_to_main_webpage(base_url, sub_url, query=""):
    page = requests.get(base_url + sub_url + query)
    soup = BeautifulSoup(page.content, "lxml")
    return soup


def scrap_and_download_files(soup, base_url, file_extension = ".pdf"):
    new_dataset_dict = {'Filed Date': [],
                        'Court Name': [],
                        'Full Name': [],
                        'Case Number': [],
                        'Opinion': [],
                        'Disposition': [],
                        }

    iframe_list = soup.find_all("iframe")
    for iframe in iframe_list:
        iframe_page = requests.get(base_url + iframe['src'])
        iframe_soup = BeautifulSoup(iframe_page.content, "lxml")
        table_list = iframe_soup.find_all("table")
        for table in table_list:
            tr_list = iframe_soup.find_all("tr")
            th_list = tr_list[0].find_all("th")
            date_posted = th_list[0].text
            case_docket = 'Case ' + th_list[1].text.replace(" #/File Format", "")
            case_desc = th_list[2].text
            case_link = "More Details"

            # Saving header info into csv file
            with open(filepath + csv_courts_filename + date_stamp + ".csv", 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([
                    date_posted,
                    case_docket,
                    case_desc,
                    case_link
                ])
                # Printing header info to console
                print(f'{date_posted}\t---\t'
                    f'{case_docket}\t---\t'
                    f'{case_desc}\t\t\t---\t'
                    f'More Details')
                for i in range(1, len(tr_list)):
                    td_list = tr_list[i].find_all("td")
                    date_posted = td_list[0].text
                    case_docket = td_list[1].text.replace("[PDF][DOC]", "")
                    case_desc = td_list[2].text.replace(" Case Details", "")
                    filename_raw = case_docket
                    try:
                        case_link = td_list[2].a["href"]
                    except TypeError as e:
                        case_link = "Not Available"

                    # Saving details into csv file
                    csv_writer.writerow(
                        [
                            date_posted,
                            case_docket,
                            case_desc,
                            case_link
                        ]
                    )
                    # Printing details to console
                    print(f'{date_posted}\t---\t'
                        f'{case_docket}\t---\t'
                        f'{case_desc}\t---\t'
                        f'{case_link}')

                    # Saving the case files in desired (.)extensions, if any
                    link_tags = td_list[1].find_all('a')
                    for a in link_tags:
                        full_filepath = filepath + filename_raw + file_extension.lower()
                        if file_extension.lower() in a['href'].lower() and not file_exists(full_filepath):

                            # Get response object for link and write new content in file
                            response = requests.get(base_url + a['href'])
                            with open(full_filepath, "wb") as new_file:
                                new_file.write(response.content)

                        if file_exists(full_filepath):
                            # Convert into html from the (.docx)file
                            with open(full_filepath, "rb") as docx_file:
                                result = mammoth.convert_to_html(docx_file)
                                html = result.value
                                messages = result.messages

                            # Save as (.html)file
                            with open(filepath + filename_raw + ".html", "w", encoding="utf8") as html_file:
                                html_file.write(result.value)

                            soup = BeautifulSoup(html, "html.parser")
                            parsed_data_dict = casefile_parser(soup, filename_raw)
                            new_dataset_dict['Filed Date'].append(date_posted)
                            new_dataset_dict['Court Name'].append(parsed_data_dict['court_name'])
                            new_dataset_dict['Full Name'].append(parsed_data_dict['full_name'])
                            new_dataset_dict['Case Number'].append(parsed_data_dict['case_number'])
                            new_dataset_dict['Opinion'].append([])
                            new_dataset_dict['Disposition'].append([])
                return new_dataset_dict


def casefile_parser(soup, filename):
    filed_date = ""
    court_name = ""
    full_name = ""
    case_number = filename
    opinion = ""
    disposition = ""

    regex_filed_date = r'Filed [0-9]?[0-9]/[0-9]?[0-9]/[0-9][0-9]'
    regex_court_name = r'\w*COURT\w*'
    regex_full_name = r'\w*(Plaintiff[s]?)\w*|\w*(Respondent[s]?)\w*|\w*(Defendant[s]?)\w*|\w*(Appellant[s]?)\w*|\w*(Petitioner[s]?)\w*'
    regex_ct_no = r'\w*\sCt. No.\s\w*'
    regex_disposition = r'\w*DISPOSITION\w*'
    party_names = []
    party_roles = []
    count = 0
    para_list = soup.find_all('p')
    for i in range(len(para_list)):
        regex_filter = r'\n|\.|\,'
        # Search for Filed Date
        if re.search(regex_filed_date, para_list[i].get_text(strip=True), re.I):
            filed_date = para_list[i].get_text(strip=True).split(' ')[1]

        # Search for Court Name
        if re.search(regex_court_name, para_list[i].get_text(strip=True)):
            court_name = para_list[i].get_text(strip=True)

        # Search for Full Case Name
        if (re.search(regex_full_name, para_list[i].text)) and count != 2:
            for j in range(i - 1, -1, -1):
                if len(para_list[j].text) == 1:
                    continue
                party_names.append(re.sub(regex_filter, "", para_list[j].get_text(strip=True)))
                break
            party_roles.append(re.sub(regex_filter, "", para_list[i].get_text(strip=True)))
            count = count + 1

        # Search for Case Content
        if re.search(regex_ct_no, para_list[i].get_text(strip=True), re.I):
            for j in range(i + 1, len(para_list), 1):
                opinion = opinion + para_list[j].get_text(strip=True) + '\n'

        # Search for Disposition
        if re.search(regex_disposition, para_list[i].get_text(strip=True)):
            disposition = para_list[i + 1].get_text(strip=True)

    full_name = party_names[0] + " - " + party_roles[0] + " v. " + party_names[1] + " - " + party_roles[1]
    return {'filed_date': filed_date,
            'court_name': court_name,
            'full_name': full_name,
            'case_number': case_number,
            'opinion': opinion,
            'disposition': disposition
            }


def dataframe_to_xml(new_dataset_dict):
    df = pd.DataFrame(new_dataset_dict)
    df.to_csv(filepath + csv_casefiles_filename + date_stamp + ".csv", index=False)
    # Converting the dataframe to a dictionary
    data_dict = df.to_dict(orient="records")
    # Converting the dataframe to XML
    xml_data = dicttoxml(data_dict).decode()
    # Then save it to file
    with open(filepath + csv_casefiles_filename + date_stamp + ".xml", "w+", encoding="utf8") as f:
        f.write(xml_data)



