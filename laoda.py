from lxml import html
import csv,os,json
import requests
from selenium import webdriver
import argparse
from time import sleep

productList = []

class Product:
    def _init_(self):
        self.name = ""
        self.commentLink = ""
        self.pageCount=""
        self.comments=[]



def getPage(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    number = 0
    doc = html.fromstring(page.content)

    XPATH_number = '//li[@class="page-button"][last()]//text()'
    RAW_number = doc.xpath(XPATH_number)
    number = ''.join(RAW_number).strip() if RAW_number else None

    return number

def AmzonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        sleep(1)
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_COMMENTS = '//a[@data-hook="see-all-reviews-link-foot"]//@href'

            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_COMMENT = doc.xpath(XPATH_COMMENTS)




            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            COM = ''.join(RAW_COMMENT).strip() if RAW_COMMENT else None


            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'NAME':NAME,
                    'URL':url,
                    'COMMENT':"https://www.amazon.com"+COM,
                    }



            return data
        except Exception as e:
            print (e)

def add_Comment(product,star):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
#product.pageCount
    for index in range(product.pageCount):
        link = product.commentLink.replace("ref=cm_cr_dp_d_show_all_btm","ref=cm_cr_arp_d_paging_btm_" + str(index + 1))
        link += "&pageNumber="
        link += str(index + 1)
        link += "&filterByStar="
        link += star
        page = requests.get(link,headers=headers)
        doc = html.fromstring(page.content)
        product.comments.append([])

        for ind in range(10):
            CC = '(//div[@class="a-row review-data"])[' + str(ind) + ']//text()'
            RAW_CC = doc.xpath(CC)
            COMMENT = ''.join(RAW_CC).strip() if RAW_CC else None
            #COMMENT.replace("  ","\n")

            product.comments[index].append(COMMENT)






def ReadAsin(star):
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    #AsinList = ['/B004164SRA/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=avp_only_reviews&sortBy=helpful&filterByStar='+ star +'&pageNumber=1']
    AsinList = ['B004164SRA','B0113UZJE2']
    extracted_data = []

    # read argument from asinList
    for i in AsinList:
        new_product = Product()
        url = "http://www.amazon.com/dp/"+i
        print ("Processing: "+url)
        extracted_data.append(AmzonParser(url))
        new_product.name = extracted_data[0]['NAME']
        new_product.commentLink = extracted_data[0]['COMMENT']
        new_product.pageCount =int(getPage(extracted_data[0]['COMMENT']).replace(",",""))
        new_product.comments =[]
        add_Comment(new_product,star)
        productList.append(new_product)
        sleep(3)

    #write basic arguments to data.json in json format
    f=open('data.json','w')
    json.dump(extracted_data,f,indent=4)
    filename = star + "_output.txt"
    with open(filename, "w") as text_file:
        for product in productList:
            for index_t in range(product.pageCount):
                text_file.write("Page number is :" + str(index_t + 1))
                text_file.write("                 \n")
                text_file.write("                 \n")
                for com in product.comments[index_t]:
                    if(com!= None):
                        text_file.write(com)
                        text_file.write("                 ")
                        text_file.write("                 \n")
                        text_file.write("                 \n")

if __name__ == "__main__":
    # write out txt file with all positive and critical comments
    ReadAsin("positive")
    ReadAsin("critical")
