import sys
import os
import re
import requests
import clipboard
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as wait
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

print(f"os.environ[AWS_ACCESS_KEY_ID]: {os.environ['AWS_ACCESS_KEY_ID']}")
# session = boto3.Session(
#     aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
#     aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
# )

# print(session.get_credentials())

CHROME_PATH = os.environ["CHROME_PATH"]#'/home/jl/chromedriver'
client = boto3.resource('dynamodb',
                        region_name="ap-northeast-2",
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                        )
tb_name = "FND_DETAILS"


def putToTable(dictToPut):

    table = client.Table(tb_name)
    print(table)
    try:
        table.load()
        response = table.put_item(
            Item=dictToPut
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response


class Crawler:
    def __init__(self, url) -> None:
        options = Options()
        options.headless = True
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(CHROME_PATH, options=options)
        driver.set_window_size(1920, 1080)
        self.driver = driver
        self.setProfileUrl(url)
        self.driver.get(url)

    def getEverything(self):
        self.getUserName(self.profileUrl)
        self.getName()
        self.getSocials()
        self.getAllCollections()
        return {
            "username": self.username,
            "name": self.name,
            "profileUrl": self.profileUrl,
            "socials": self.socials,
            "collections": self.collection,
        }

    def getCurUrl(self):
        return self.driver.current_url

    def setProfileUrl(self, url):
        self.profileUrl = url

    def getUserName(self, url):
        self.username = os.path.basename(url)
        return self.username

    def getName(self):
        nameClass = "st--c-PJLV st--c-kxmHLk st--c-PJLV-boLyXY-size-3 st--c-PJLV-jCZVon-size-4 st--c-kxmHLk-dIdTVS-leading-tight st--c-PJLV-ifOmecJ-css".replace(
            " ", ".")
        el = self.driver.find_element(By.CLASS_NAME, nameClass)
        self.name = el.get_attribute('innerHTML')
        return self.name

    def getAllCollections(self):
        ctClass = "st--c-PJLV st--c-kFlVdX st--c-cvvxlb st--c-PJLV-ifcglaT-css".replace(
            " ", ".")
        collectionClass = "st--c-PJLV st--c-bQzyIt st--c-cpoXkf st--c-dTHMXF".replace(
            " ", ".")
        collectionUrl = f"{self.profileUrl}?tab=collections"
        # if (collectionUrl == self.getCurUrl()):
        self.driver.get(collectionUrl)
        collectionsContainer = wait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, collectionClass)))
        children = collectionsContainer.find_elements(By.XPATH, "*")

        toRet = []

        for child in children:
            # print("===============")
            innerHTML = child.get_attribute('innerHTML')
            # print(innerHTML)
            collectionToken = wait(child, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, ctClass)))
            # collectionToken = child.find_element(By.CLASS_NAME, ctClass)
        #     print(type(innerHTML))
        #     print(innerHTML)
            collectionLink = collectionToken.get_attribute('href')

            print(f"CT: {os.path.basename(collectionLink)} -> {collectionLink}")
            toRet.append({
                "token": os.path.basename(collectionLink),
                "link": collectionLink
            })

        self.collection = toRet
        return toRet

    def getSocials(self):
        socialClass = "st--c-bzQViP st--c-bzQViP-gbFqzR-size-1 st--c-bzQViP-IQnmy-variant-outline st--c-bzQViP-eEEdam-cv".replace(
            " ", ".")
        socials = self.driver.find_elements(By.CLASS_NAME, socialClass)
        toAdd = {}
        for social in socials:
            print("=" * 50)
            link = social.get_attribute('href')
            print(link)
            if ("twitter" in link):
                toAdd["twitter"] = link
            elif ("instagram" in link):
                toAdd["instagram"] = link
            elif ("etherscan" in link):
                toAdd["etherscan"] = link
        self.socials = toAdd
        return toAdd


def main():
    url = sys.argv[1]
    wallet = sys.argv[2]
    crawler = Crawler(url)
    toAdd = crawler.getEverything()
    toAdd["wallet"] = wallet
    res = putToTable(toAdd)
    print(res)


if __name__ == "__main__":
    main()
