from selenium import webdriver
import webdriver_manager.chrome
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from log import email, password, itemList
import random


class AmazonBot:
    def __init__(self):
        # Create a browser we can play on
        self.driver = webdriver.Chrome(webdriver_manager.chrome.ChromeDriverManager().install())

    def login(self):
        # Go to Amazon
        self.driver.get('https://amazon.com')

        # Log in
        element = WebDriverWait(self.driver, 10)
        self.driver.find_element_by_xpath("/html/body/div[1]/header/div/div[3]/div[9]/div[2]/a").click()

        # Enter e-mail
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[1]/input[1]").send_keys(email)

        # Continue
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[2]/span/span/input").click()

        # Enter password
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[1]/input").send_keys(password)

        # Continue
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[2]/span/span/input").click()
        sleep(20)
        # Press not now for adding phone
        try:
            self.driver.find_element_by_xpath(
                "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[3]/div/a").click()
        except NoSuchElementException:
            pass
        sleep(1)

    def purchase(self):
        # Shuffles link order for bots
        random.shuffle(itemList)

        # Creates a variable called continueRunning to monitor if the while loop should break out or not
        continueRunning = True
        while continueRunning:
            for item in itemList:
                print(item["url"], item["max_price"])

                # Goes to current link
                self.driver.get(item["url"])

                # Clicks on buy now button
                try:
                    self.driver.find_element_by_id("buy-now-button").click()

                    # Checks normal delivery option
                    self.driver.find_element_by_xpath(
                        "html/body/div[5]/div/div[2]/form/div/div/div/div[1]/div[5]/div/div/div/div[3]/div/div/div[2]/div[2]/div[1]/fieldset/div[1]/input").click()
                    sleep(4)

                    # Retrieves price and removes commas, then turns it into an int
                    priceString = self.driver.find_element_by_xpath(
                        "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[3]/div[2]/table[1]/tbody/tr[8]/td[2]").text

                    finalPrice = float(priceString[1:].replace(",", ""))

                    # Compares the final total
                    print(finalPrice)
                    if finalPrice < item["max_price"]:
                        continueRunning = False
                        print("Ordering item...")
                        # Orders
                        self.driver.find_element_by_xpath(
                            "/html/body/div[5]/div[1]/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input").click()
                        sleep(15)
                        break
                except NoSuchElementException:
                    print("Couldn't order, going next link")
                    pass


bot = AmazonBot()
bot.login()
bot.purchase()
