from doc2html_scrapper import navigate_to_main_webpage, scrap_and_download_files, dataframe_to_xml

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Scrapping the California Court Website
    base_url = "https://www.courts.ca.gov"
    sub_url = "/opinions-slip.htm"
    query = "?Courts=X"
    file_extension = ".docx"
    soup = navigate_to_main_webpage(base_url, sub_url)
    new_dataset_dict = scrap_and_download_files(soup, base_url, file_extension)
    dataframe_to_xml(new_dataset_dict)