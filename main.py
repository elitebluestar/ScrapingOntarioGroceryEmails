import re
import os
import time
import xlsxwriter

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd

class GetOntarioGroceryEmail(object):
	def __init__(self):
		self.base_url = 'https://www.contactcanada.com/database/freesearch.php?portal=0a10'

		self.setup_driver('/home/elite/work/ScrapingOntarioGroceryEmails/chromedriver')
	
	def setup_driver(self, chrome_path, headless=False):
		"""
		Chreates chrome web driver.
		:chrome_path: the location of chromedriver.exe
		"""
		options = webdriver.ChromeOptions()
		self.driver = webdriver.Chrome(chrome_path, chrome_options = options)

	def is_visible_element(self, by_type, locator, timeout=10):
		"""
		Return true if locator is found up to timeout.
		Return false if it's not found until timeout is over.
		"""
		try:
			if by_type == 'name':
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.NAME, locator)))
			elif by_type == 'id':
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator)))
			else:
				WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
			return True
		except Exception as error:
			return False

	def start_process(self):
		"""
		Start scraping process.
		"""
		print('Started scraping')
		self.driver.get(self.base_url)
		time.sleep(2)

		select_box = self.driver.find_element_by_id('fld-locations')
		option = select_box.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/form[2]/ul/li[2]/select/optgroup[1]/option[8]')
		option.click()

		elem = self.driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/form[2]/p[2]/input[1]')
		elem.click()
		time.sleep(1)

		results = []
		page_num = 0

		while True:
			if len(results) > 200:
				break
			view_profiles = self.driver.find_elements_by_css_selector("#containerContent .listResults .openNewWindow.iconNewWindow .noPrint")

			for index in range(0, len(view_profiles)):
				view_profiles = self.driver.find_elements_by_css_selector("#containerContent .listResults .openNewWindow.iconNewWindow .noPrint")
				view_profiles[index].click()
				self.driver.switch_to.window(self.driver.window_handles[-1])
				try:
					results.append(
						(
							self.driver.find_elements_by_class_name('linkEmail')[0].get_attribute('href').split('?')[0].split(':')[-1].strip(),
							self.driver.find_elements_by_class_name('linkExternal')[0].get_attribute('href')
						)
					)
				except:
					results.append('')
				time.sleep(2)
				self.driver.close()
				time.sleep(2)
				self.driver.switch_to.window(self.driver.window_handles[0])

				print(results)
				df = pd.DataFrame(results, columns = ['email', 'website'])
				writer = pd.ExcelWriter('results.xlsx', engine='xlsxwriter')
				df.to_excel(writer,sheet_name='emails',index=False)
				writer.save()
		
			self.driver.get('https://www.contactcanada.com/database/freesearch.php?portal=0a10&action=next_results&s={}&l=20'.format(page_num * 20 + len(view_profiles)))
			page_num += 1
			

if __name__ == '__main__':
	getontariogroceryemails = GetOntarioGroceryEmail()
	getontariogroceryemails.start_process()