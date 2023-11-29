from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import json
import time

driver = webdriver.Chrome("")
def getAmazonUsers(url):
    driver.get(url) 
    driver.find_element(By.ID, "acrCustomerReviewText").click()
    driver.find_element(By.XPATH, '//*[@data-hook="see-all-reviews-link-foot"]').click()
    
    time.sleep(2)
    
    for i in range(0, 10):
        count = i+1
        temp1 = driver.find_elements(By.XPATH, '//div[@id="cm_cr-review_list"]/div/div[@class="a-row a-spacing-none"]/div/div/a[@class="a-profile"]')
        temp2 = driver.find_elements(By.XPATH, '//div[@id="cm_cr-review_list"]/div/div[@class="a-row a-spacing-none"]/div/div/a[@class="a-profile"]/div[@class="a-profile-content"]/span')
        usersDetails = []
        for j in range(len(temp1)):
            userDetail = {}
            userDetail["userPageLink"] = temp1[j].get_attribute('href')
            userDetail["userName"] = temp2[j].text
            usersDetails.append(userDetail)
        pageOfUsers.append(usersDetails)
        time.sleep(2)
        try:
            driver.find_element(By.XPATH, '//ul[@class="a-pagination"]/li[2]/a').click()
            driver.refresh()
        except:
            break
        print("Review page", count, "grabbed.")
    print("---DONE---")
    
def getReviewValue(s):
    arr = [1, 2, 3, 4, 5]
    for el in arr:
        if str(el) in s:
            return el

def hasEnoughReviews(u):
    global totalNumOfUsers
    driver.get(u["userPageLink"])
    time.sleep(4)
    
    totalNumOfUsers += 1
    return len(driver.find_elements(By.XPATH, '//div[@class="your-content-tab-container"]/div'))

def determineBias(u):
    global biasUsersFound
    scoreArr = [0, 0, 0, 0, 0, 0]
    userReviews = driver.find_elements(By.XPATH, '//div[@class="your-content-tab-container"]/div/a/div/div/div/div/i')
    for i in range(len(userReviews)):
        scoreArr[getReviewValue(userReviews[i].get_attribute('class'))] += 1
    
    total = sum(scoreArr)
    percentageHelper = 100/total
    if(scoreArr[5] * percentageHelper) >= 80 or (scoreArr[1] * percentageHelper) >= 80:
        print("***",u["userName"], "is a bias user. ***")
        biasUsersFound += 1
    else:
        print("***", u["userName"], "is a NOT bias user. ***")
    

pageOfUsers = []
biasUsersFound = 0
totalNumOfUsers = 0
option = int(input("Enter 1 to get the reviews of the default of product given.\nEnter 2 to enter a link to a different product.\nOption: "))
while option != 1 and option != 2:
    option = input("Enter valid option:")
if option == 1:
    getAmazonUsers('https://a.co/d/hahQlID')
elif option == 2:
    customUrl = input("Enter your custom URL:")
    getAmazonUsers(customUrl)

with open('users.json','w') as outFile:
    if pageOfUsers:
        print("Dumping Users!")
        json.dump(pageOfUsers, outFile)
        outFile.write("\n")

for page in pageOfUsers:
    for entry in page:
        if hasEnoughReviews(entry) >= 15:
            print(entry["userName"], "has enough reviews to determine bias!!")
            determineBias(entry)
        else:
            print(entry["userName"], "does not have enough reviews to determine bias.")
print("\n\nTotal number of users:", totalNumOfUsers)
print("Total number of bias users found: " + str(biasUsersFound) + "(" + str(round((100/totalNumOfUsers) * biasUsersFound, 2)) + "%)")
driver.quit()