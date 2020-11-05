# drivetest-scraper  
Selenium scraper for [https://drivetest.ca/](https://drivetest.ca/).  
Inserts data into MongoDB Atlas database, to be used by [drivetest-openings](https://github.com/tacticaltofu/drivetest-openings)

## If you want to use dtbot directly
1. Clone the backup-master branch
2. Download the version of chromedriver that matches your Chrome version, and put chromedriver.exe in the dtbot folder (you may need to change the line `self.wd = webdriver.Chrome("chromedriver.exe")` in `drivetestbot.py` if you are not using Windows)
3. Set the environment variables as follows:
  - DT_EMAIL to be your email
  - DT_EMAIL_PWD to be the password to your email (if you use gmail and want to get email notifications for when an spot opens up)
  - DT_LICENCE to be your driver's license number
  - DT_EXPIRY to be your driver's license expiry (e.g 2020/01/31)
4. Run drivetestbot.py directly.

Hope that helps.
