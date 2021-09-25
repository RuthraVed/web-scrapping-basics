from scrapper_excercise import navigate_to_main_webpage, scrap_and_download_files

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Scrapping the California Court Website
    base_url = "https://www.courts.ca.gov"
    sub_url = "/opinions-slip.htm"
    query = "?Courts=X"
    file_extension = ".doc"
    soup_obj = navigate_to_main_webpage(base_url, sub_url, query)
    scrap_and_download_files(soup_obj, base_url, file_extension)