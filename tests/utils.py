"""Utility methods for unit testing.
"""

import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select


SLATE_URL = 'http://localhost:8080/slate'
MOCK_USER = 'test'
MOCK_PW = 'test'
DEFAULT_CATEGORIES = ['alcohol',
                      'bills',
                      'clothing',
                      'entertainment',
                      'food (in)',
                      'food (out)',
                      'household',
                      'medical',
                      'miscellaneous',
                      'rent/mortgage',
                      'transportation',
                      'travel/vacation']


def exists_by_xpath(browser, xpath):
    """Returns True if element exists, False otherwise.
    """
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def link_href_is_correct(browser, xpath, href):
    """Returns True if link href is the value passed in, False otherwise.
    """
    try:
        link = browser.find_element_by_xpath(xpath)
        actual_href = link.get_attribute('href')

        # The browser generates a complete URL from a relative path. Remove it
        # so we can just check relative paths.
        actual_href = actual_href.replace(SLATE_URL, '')

        return actual_href == '/%s' % href
    except NoSuchElementException:
        return False


def register_user(browser, username=MOCK_USER, password1=MOCK_PW,
                  password2=MOCK_PW, should_fail=False):
    """Creates a new user.
    """
    browser.get('%s/register' % SLATE_URL)
    username_input = browser\
        .find_element_by_xpath('//input[@name="username"]')
    password_input_1 = browser\
        .find_element_by_xpath('//input[@name="password2"]')
    password_input_2 = browser\
        .find_element_by_xpath('//input[@name="password1"]')
    username_input.send_keys(username)
    password_input_1.send_keys(password1)
    password_input_2.send_keys(password2)
    browser.find_element_by_xpath('//button[@type="submit"]').click()
    if should_fail:
        # We do not want to check for successful login, i.e. the landing page,
        # since sometimes registration should fail in our tests.
        time.sleep(10)
    else:
        wait_until(browser, '//a[text()="View expenses"]')


def update_password(browser, old_password, new_password1, new_password2):
    browser.get('%s/account' % SLATE_URL)
    old_password_input = browser\
        .find_element_by_xpath('//input[@name="oldpassword"]')
    new_password_input_1 = browser\
        .find_element_by_xpath('//input[@name="newpassword1"]')
    new_password_input_2 = browser\
        .find_element_by_xpath('//input[@name="newpassword2"]')
    old_password_input.send_keys(old_password)
    new_password_input_1.send_keys(new_password1)
    new_password_input_2.send_keys(new_password2)
    browser.find_element_by_xpath('//div[@id="update-password-section"]'
                                  '//button[@type="submit"]').click()


def login_user(browser, username=MOCK_USER, password=MOCK_PW):
    """Logs in user.
    """
    browser.get('%s/login' % SLATE_URL)
    username_input = browser\
        .find_element_by_xpath('//input[@name="username"]')
    password_input = browser\
        .find_element_by_xpath('//input[@name="password"]')
    username_input.send_keys(username)
    password_input.send_keys(password)
    browser.find_element_by_xpath('//button[@type="submit"]').click()
    wait_until(browser, '//a[text()="View expenses"]')


def logout_user(browser):
    """Logs out user.
    """
    browser.find_element_by_xpath('//div[@id="footer"]//button[@type="submit"]').click()


def delete_user(browser):
    """Delete test user.
    """
    browser.get('%s/account' % SLATE_URL)
    elem = wait_until(browser, '//div[@id="delete-account-section"]//button[@type="submit"]')
    elem.click()
    browser.switch_to.alert.accept()
    # Give the backend time to delete the user.
    time.sleep(3)


def add_expense(browser, cost, category, comment):
    """Adds expense.
    """
    cost_input = browser.find_element_by_xpath('//input[@name="cost"]')
    cost_input.send_keys(cost)
    category_select = Select(
        browser.find_element_by_xpath('//select[@name="category_id"]')
    )
    category_select.select_by_visible_text(category)
    comment_input = browser\
        .find_element_by_xpath('//input[@name="comment"]')
    comment_input.send_keys(comment)
    browser.find_element_by_xpath('//button[text()="Add"]').click()


def get_flashed_message(browser):
    """Returns the message that has been flashed on the user's screen.
    """
    message = wait_until(browser, '//div[@class="flashes"]//p')
    return message.text


def wait_until(browser, xpath, timeout=60):
    """Wait until element becomes available.
    """
    wait = WebDriverWait(browser, timeout)
    return wait.until(lambda b: b.find_element_by_xpath(xpath))


def click(browser, xpath, wait_for_xpath=None):
    """Click on an element by XPath. Wait to ensure page loads.
    """
    browser.find_element_by_xpath(xpath).click()
    if wait_for_xpath:
        wait_until(browser, wait_for_xpath)
    else:
        time.sleep(30)
