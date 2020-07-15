import selenium
from selenium import webdriver 
import os 
import time 
import io
import requests
from PIL import Image 
import hashlib


#Chrome driver path  
DRIVER_PATH = "D:\Webscraping\chromedriver_win32\chromedriver"


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")                                              #Synchronously Executes JavaScript in the current window/frame.
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"                  # feed this in to web browser by replacing q with search term 

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()                                               # no repeated entries 
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")          # all individual images in google have class =img.rg_i.Q4LuWd.tx8vtf
        number_results = len(thumbnail_results)

        
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls     
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            

            for actual_image in actual_images:
                print(actual_image)
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))
                    print("*__________*_________*")
                    

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(20)
            #return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path:str,url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')      # hashes the filename according to the content of the image 
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term:str,driver_path:str,target_path='D:\Webscraping\images\India',number_images=500):
    
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))     #os.path.join() method in Python join one or more path components intelligently. 

    if not os.path.exists(target_folder):                            # if folder doesnt exist create the folder 
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:                              # start the google webdriver that opens a window to google chrome 
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)
        
    for elem in res:
        persist_image(target_folder,elem)



search_term = "Ansal API floor plan" 

search_and_download(search_term=search_term, driver_path=DRIVER_PATH)

print("Done with code")

