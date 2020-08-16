import os
import time
import smtplib

def send_mail(server, recipient, user, passw, msg):
    server = smtplib.SMTP('smtp.%s:587' % server)
    server.starttls()
    server.login(user, passw)
    server.sendmail(user, recipient, msg)
    server.quit()
    
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT_TIMEOUT = 60

book_test_xpath = "//a[@title='Book a Road Test']"
continue_btn_xpath = "//button[.//span[text()='Continue']]"

month_header_xpath = "//h3[@class='ng-binding']"
next_month_btn_xpath = "//a[@title='next month']"
date_cell_xpath = "//a[contains(@class, 'date-link')]"
available_xpath = "//a[@class='date-link']"
return_to_selection_xpath = "//a[@title='Back to DriveTest Centre Locations Selection']"

close_popout_xpath = "//layer//input[@name='No']"
retry_xpath = "//a[@title='retry']"

class DriveTestBot():
    def __init__(self):
        self.wd = webdriver.Chrome("chromedriver.exe")

    def log_in(self, email, licence, expiry):
        self.wd.get("https://drivetest.ca/book-a-road-test/booking.html")
        self.close_popout()
        WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "regSubmitBtn")))

        email_field = self.wd.find_element_by_id("emailAddress")
        confirm_email_field = self.wd.find_element_by_id("confirmEmailAddress")
        licence_field = self.wd.find_element_by_id("licenceNumber")
        expiry_field = self.wd.find_element_by_id("licenceExpiryDate")

        email_field.send_keys(email)
        confirm_email_field.send_keys(email)
        licence_field.send_keys(licence)
        expiry_field.send_keys(expiry)

        submit_btn = self.wd.find_element_by_id("regSubmitBtn")
        submit_btn.click()

        WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "G2btn")))
        g2_btn = self.wd.find_element_by_id("G2btn")
        g2_btn.click()

        WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, continue_btn_xpath)))
        continue_btn = self.wd.find_element_by_xpath(continue_btn_xpath)
        continue_btn.click()

    def navigate_to_location(self, location):
        location_xpath = f"//a[.//*[text()='{location}']]"
        WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, location_xpath)))
        location_btn = self.wd.find_element_by_xpath(location_xpath)
        location_btn.click()

        WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, continue_btn_xpath)))
        continue_btn = self.wd.find_element_by_xpath(continue_btn_xpath)
        continue_btn.click()

    def check_available(self, num_months):
        dictionary = {}
        for i in range(num_months):
            time.sleep(2)

            self.click_retry()
            WebDriverWait(self.wd, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, date_cell_xpath)))
            
            month = self.wd.find_element_by_xpath(month_header_xpath).text
            available_dates = self.wd.find_elements_by_xpath(available_xpath)
            
            open_dates = []
            for date in available_dates:
                open_dates.append(date.text)
                
            dictionary[month] = open_dates
            next_month_btn = self.wd.find_element_by_xpath(next_month_btn_xpath)
            next_month_btn.click()
            
        return_to_selection_link = self.wd.find_element_by_xpath(return_to_selection_xpath)
        return_to_selection_link.click()
        return dictionary

    def check_locations(self, locations, months):
        dictionary = {}
        for location in locations:
            self.navigate_to_location(location)
            available_dates_here = self.check_available(months)
            dictionary[location] = available_dates_here
        return dictionary

    def click_retry(self):
        retry_links = self.wd.find_elements_by_xpath(retry_xpath)
        for link in retry_links:
            link.click()

    def close_popout(self):
        close_popout_buttons = self.wd.find_elements_by_xpath(close_popout_xpath)
        if len(close_popout_buttons) > 0:
            self.wd.refresh()
        
    def pretty_print(self, dictionary):
        for location, months in dictionary.items():
            print(location)
            print("==========")
            for month, dates in months.items():
                if dates:
                    print(f">>> {month} >>> {dates}")
            print("==========")
            print("")

    def notify(self, dictionary, recipient, user, passw):
        for location, months in dictionary.items():
            has_free_date = False
            for month, dates in months.items():
                if dates:
                    has_free_date = True    
                    break
            if has_free_date:
                message_to_send = f"\nThere is an available opening at {location}! It is {months}"
                send_mail('gmail.com', recipient, user, passw, message_to_send)
                
    def stop(self):
        self.wd.quit()

def job():
    DT_EMAIL = os.environ.get('DT_EMAIL')
    DT_EMAIL_PWD = os.environ.get('DT_EMAIL_PWD')
    DT_LICENCE = os.environ.get('DT_LICENCE')
    DT_EXPIRY = os.environ.get('DT_EXPIRY')
    
    bot = DriveTestBot()
    bot.log_in(DT_EMAIL, DT_LICENCE, DT_EXPIRY)
    available_dates_all = bot.check_locations(["Kitchener", "Guelph", "Brantford", "Stratford"], 3)
    bot.pretty_print(available_dates_all)
    bot.notify(available_dates_all, DT_EMAIL, DT_EMAIL, DT_EMAIL_PWD)
    bot.stop()

from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=30)
    scheduler.start()
    job()
