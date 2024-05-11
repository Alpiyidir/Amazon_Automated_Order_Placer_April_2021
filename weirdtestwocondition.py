from selenium import webdriver
import webdriver_manager.chrome

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from log import email, password, itemList
import random
from time import sleep
import sys

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"


class AmazonBot:
    def __init__(self):
        # Create a browser we can play on
        self.driver = webdriver.Chrome(webdriver_manager.chrome.ChromeDriverManager().install())

    def login(self):
        # Initializes a wait
        wait = WebDriverWait(self.driver, 10, poll_frequency=0.1)

        def waitUntilXPATH(xpath):
            wait.until(ec.presence_of_element_located((By.XPATH, f"{xpath}")))

        # Go to Amazon
        self.driver.get('https://amazon.com')

        # Log in
        waitUntilXPATH("/html/body/div[1]/header/div/div[3]/div[9]/div[2]/a")
        self.driver.find_element_by_xpath("/html/body/div[1]/header/div/div[3]/div[9]/div[2]/a").click()

        # Enter e-mail
        waitUntilXPATH("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[1]/input[1]")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[1]/input[1]").send_keys(email)

        # Continue
        waitUntilXPATH("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[2]/span/span/input")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/form/div/div/div/div[2]/span/span/input").click()

        # Enter password
        waitUntilXPATH("/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[1]/input")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[1]/input").send_keys(password)

        # Continue
        waitUntilXPATH("html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[2]/span/span/input")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div/form/div/div[2]/span/span/input").click()
        sleep(2)

    def purchase(self):
        # Initializes wait
        wait = WebDriverWait(self.driver, 10, poll_frequency=0.1)
        impatientWait = WebDriverWait(self.driver, 4, poll_frequency=0.1)

        # Shuffles link order for bots
        random.shuffle(itemList)
        print("List length:", len(itemList))

        # Creates a variable called continueRunning to monitor if the while loop should break out or not
        continueRunning = True
        while continueRunning:
            # For every list in the itemList it will iterate over them forever until continueRunning is set to False
            for item in itemList:
                # Goes to current link
                self.driver.get(item["url"])

                try:
                    # Checks if the buy now button exists
                    wait.until(ec.presence_of_element_located((By.ID, "desktop_buybox")))
                    self.driver.find_element_by_id("buy-now-button")
                    buyNowExists = True
                except NoSuchElementException:
                    print("Buy now button not found, checking see all options")
                    buyNowExists = False
                    pass

                if buyNowExists:
                    self.driver.find_element_by_id("buy-now-button").click()
                    # If it asks us to choose an address, we choose our main address
                    try:
                        wait.until(ec.presence_of_element_located(
                            (By.XPATH, "/html/body/div[5]/div[2]/div[1]/form/div/div[1]/div[2]/span/a")))
                        deliverHref = str(self.driver.find_element_by_xpath(
                            "/html/body/div[5]/div[2]/div[1]/form/div/div[1]/div[2]/span/a").get_attribute("href"))
                        self.driver.get(deliverHref)
                    except TimeoutException:
                        print("No address check, passing")
                        pass

                    # Gets final total price for later
                    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                               "td[class='a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap']")))
                    lastMenuTotalPrice = float(self.driver.find_element_by_css_selector(
                        "td[class='a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap']").text[
                                               1:].replace(",", ""))

                    # If the final price is same to the price + shipping then there is no extra costs associated
                    wait.until(ec.presence_of_element_located(
                        (By.XPATH, "//*[@id='subtotals-marketplace-table']/tbody/tr[4]/td[2]")))
                    totalBeforeTax = float(self.driver.find_element_by_xpath(
                        "//*[@id='subtotals-marketplace-table']/tbody/tr[4]/td[2]").text[1:].replace(",", ""))
                    if lastMenuTotalPrice == totalBeforeTax:
                        buyNowImportFeeExists = False
                    else:
                        buyNowImportFeeExists = True

                    if buyNowImportFeeExists:
                        wait.until(ec.presence_of_element_located(
                            (By.XPATH, "//*[@id='subtotals-marketplace-table']/tbody/tr[6]/td[2]")))
                        self.driver.find_element_by_xpath(
                            "//*[@id='subtotals-marketplace-table']/tbody/tr[6]/td[2]")
                        # If it finds it, checks the total price (it has the import fee included)
                        if lastMenuTotalPrice < item["max_price"]:
                            # If the condition above is true, orders
                            continueRunning = False
                            wait.until(ec.presence_of_element_located((By.XPATH,
                                                                       "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input")))
                            self.driver.find_element_by_xpath(
                                "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input").click()
                            print("Placing order...")
                            sleep(15)
                            break
                        else:
                            # Otherwise, goes to cart, Clicks delete on first item in cart
                            self.removeFirstItemFromCart(item["url"])
                            continue

                    else:
                        # Otherwise, it calculates the import fee (18% Turkey)
                        print("No import fee found, checking order total")

                        # Calculates import fee (18%)
                        wait.until(ec.presence_of_element_located(
                            (By.XPATH, "//*[@id='subtotals-marketplace-table']/tbody/tr[1]/td[2]")))
                        lastMenuRawPrice = float(self.driver.find_element_by_xpath(
                            "//*[@id='subtotals-marketplace-table']/tbody/tr[1]/td[2]").text[1:].replace(",", ""))

                        priceWTax = lastMenuTotalPrice + (lastMenuRawPrice / 100 * 18)

                        # If the new calculated price is less than our maximum price, orders
                        if priceWTax < item["max_price"]:
                            continueRunning = False
                            wait.until(ec.presence_of_element_located((By.XPATH,
                                                                       "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input")))
                            self.driver.find_element_by_xpath(
                                "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input").click()
                            print("Price with tax is lower than maximum price, ordering")
                            sleep(15)
                            break
                        else:
                            # Otherwise, goes to cart, Clicks delete on first item in cart
                            self.removeFirstItemFromCart(item["url"])
                            continue

                try:
                    # Clicks on see all buying options, and gets the href
                    wait.until(ec.presence_of_element_located((By.ID, "desktop_buybox")))
                    href = str(self.driver.find_element_by_link_text("See All Buying Options").get_attribute('href'))
                    print(href)
                except NoSuchElementException:
                    print("No suitable offers found, going to next link")
                    continue

                # Goes to the link inside the href
                self.driver.get(href)

                # Very redundant way of tracking divId, I hope it doesn't fuck me over
                try:
                    impatientWait.until(ec.visibility_of_all_elements_located((By.ID, "aod-offer")))
                    lengthOfOffers = len(self.driver.find_elements_by_id("aod-offer"))
                    impatientWait.until(ec.visibility_of_all_elements_located((By.ID, "aod-offer-list")))
                except TimeoutException:
                    print("See all options content is empty, skipping to next link")
                    continue
                for divId in range(1, lengthOfOffers + 1):
                    rawPrice = float(self.driver.find_element_by_xpath(
                        f"//*[@id='aod-price-{divId}']/span/span[2]/span[2]").text.replace(",", ""))
                    try:
                        # Looks for item cannot be shipped error message
                        self.driver.find_element_by_xpath(
                            f"//*[@id='aod-fasttrack-{divId}']/span/div/div/div/span")
                        # If it encounters it, skips to next loop
                        print(f"Offer {divId} cannot be shipped to your location")
                        continue
                    except NoSuchElementException:
                        print("No shipping error")
                        pass

                    print(f"Raw Price: {rawPrice} Max Price: {item['max_price']}")

                    if rawPrice < item["max_price"]:
                        wait.until(ec.presence_of_element_located((By.XPATH,
                                                                   f"/html/body/div[2]/span/span/span/div/div/div[4]/div[{divId}]/div[2]/div/div/div[2]/div/div/div[2]/form/span/span/span/input")))
                        self.driver.find_element_by_xpath(
                            f"/html/body/div[2]/span/span/span/div/div/div[4]/div[{divId}]/div[2]/div/div/div[2]/div/div/div[2]/form/span/span/span/input").click()
                        print("Putting into cart.")

                        # Gets the href for going to proceed to checkout
                        wait.until(ec.presence_of_element_located((By.XPATH,
                                                                   "html/body/div[1]/div/div[3]/div[2]/div[1]/div/div/div[4]/div/div/div/span[2]/span/a")))
                        href = str(self.driver.find_element_by_xpath(
                            "html/body/div[1]/div/div[3]/div[2]/div[1]/div/div/div[4]/div/div/div/span[2]/span/a").get_attribute(
                            "href"))

                        # Goes to proceed to checkout
                        self.driver.get(href)

                        # Gets final total price for later
                        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                                   "td[class='a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap']")))
                        lastMenuTotalPrice = float(self.driver.find_element_by_css_selector(
                            "td[class='a-color-price a-size-medium a-text-right grand-total-price aok-nowrap a-text-bold a-nowrap']").text[
                                                   1:].replace(",", ""))

                        lastMenuBeforeTax = float(self.driver.find_element_by_xpath(
                            "//*[@id='subtotals-marketplace-table']/tbody/tr[4]/td[2]").text[1:].replace(",", ""))
                        # If the final price is same to the price + shipping then there is no extra costs associated

                        print(lastMenuTotalPrice, lastMenuBeforeTax)
                        if lastMenuTotalPrice == lastMenuBeforeTax:
                            importFeeExists = False
                        else:
                            importFeeExists = True

                        if importFeeExists:
                            wait.until(ec.presence_of_element_located(
                                (By.XPATH, "//*[@id='subtotals-marketplace-table']/tbody/tr[6]/td[2]")))
                            self.driver.find_element_by_xpath(
                                "//*[@id='subtotals-marketplace-table']/tbody/tr[6]/td[2]")
                            # If it finds it, checks the total price (it has the import fee included)
                            if lastMenuTotalPrice < item["max_price"]:
                                # If the condition above is true, orders
                                continueRunning = False
                                wait.until(ec.presence_of_element_located((By.XPATH,
                                                                           "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input")))
                                self.driver.find_element_by_xpath(
                                    "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input").click()
                                print("Placing order...")
                                sleep(15)
                                break
                            else:
                                # Otherwise, goes to cart, Clicks delete on first item in cart
                                self.removeFirstItemFromCart(item["url"])
                                break

                        else:
                            # Otherwise, it calculates the import fee (18% Turkey)
                            print("No import fee found, checking order total")

                            # Calculates import fee (18%)
                            wait.until(ec.presence_of_element_located(
                                (By.XPATH, "//*[@id='subtotals-marketplace-table']/tbody/tr[1]/td[2]")))
                            lastMenuRawPrice = float(self.driver.find_element_by_xpath(
                                "//*[@id='subtotals-marketplace-table']/tbody/tr[1]/td[2]").text[1:].replace(",", ""))

                            priceWTax = lastMenuTotalPrice + (lastMenuRawPrice / 100 * 18)

                            # If the new calculated price is less than our maximum price, orders
                            if priceWTax < item["max_price"]:
                                continueRunning = False
                                wait.until(ec.presence_of_element_located((By.XPATH,
                                                                           "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input")))
                                self.driver.find_element_by_xpath(
                                    "/html/body/div[5]/div/div[2]/form/div/div/div/div[2]/div/div[1]/div/div[1]/div/span/span/input").click()
                                print("Price with tax is lower than maximum price, ordering")
                                sleep(15)
                                break
                            else:
                                # Otherwise, goes to cart, Clicks delete on first item in cart
                                self.removeFirstItemFromCart(item["url"])
                                break

    def removeFirstItemFromCart(self, currentItemLink):
        # Initializes wait
        wait = WebDriverWait(self.driver, 10, poll_frequency=0.1)

        self.driver.get("https://www.amazon.com/gp/cart/view.html")

        # Gets last 10 characters of currentItemLink to plug into the data-asin
        linkEnd = currentItemLink[-10:]
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, f"div[data-asin='{linkEnd}']")))
        deleteId = self.driver.find_element_by_css_selector(f"div[data-asin='{linkEnd}']").get_attribute("data-itemid")
        wait.until(ec.presence_of_element_located(
            (By.XPATH, f"//*[@id='sc-item-{deleteId}']/div[4]/div/div[1]/div/div/div[2]/div[1]/span[2]/span/input")))
        self.driver.find_element_by_xpath(
            f"//*[@id='sc-item-{deleteId}']/div[4]/div/div[1]/div/div/div[2]/div[1]/span[2]/span/input").click()
        sleep(2)


bot = AmazonBot()
bot.login()
bot.purchase()
