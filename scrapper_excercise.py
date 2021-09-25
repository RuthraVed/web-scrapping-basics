import os
import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from os.path import exists as file_exists


def navigate_to_main_webpage(base_url, sub_url, query=""):
    page = requests.get(base_url + sub_url + query)
    soup = BeautifulSoup(page.content, "lxml")
    return soup


def scrap_and_download_files(soup, base_url, file_extension = ".pdf"):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists("scrapped_datafiles"):
        os.makedirs("scrapped_datafiles")

    csv_filepath = os.path.join(base_dir, "scrapped_datafiles/")
    csv_filename = "california_courts_scrapping"
    date_stamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    csv_file = open(csv_filepath + csv_filename + date_stamp + ".csv", 'w', newline='')
    csv_writer = csv.writer(csv_file)
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
                file_path = os.path.join(base_dir, "scrapped_datafiles/")
                for a in link_tags:
                    if file_extension.lower() in a['href'].lower() and not file_exists(
                                file_path + case_docket + file_extension.lower()):
                        # Get response object for link
                        response = requests.get(base_url + a['href'])
                        # Write content in file(.)ext
                        new_file = open(file_path + case_docket + file_extension.lower(), 'wb')
                        new_file.write(response.content)
                        new_file.close()

    csv_file.close()