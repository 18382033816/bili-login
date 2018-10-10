import random
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlretrieve
import PIL.Image as image

class Crawl:
    def __init__(self,name,password):
        self.name=name
        self.pwd=password
        self.url = 'https://passport.bilibili.com/login'
        self.BORDER = 6
        self.browser = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.browser,10)
    def open_url(self):
        self.browser.get(self.url)
        input_name=self.wait.until(
        EC.presence_of_element_located((By.ID, "login-username"))
        )
        input_name.send_keys(self.name)
        input_pwd= self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        input_pwd.send_keys(self.pwd)
        button=self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".gt_ajax_tip.gt_ready"))
        )
        button.click()
    def get_images(self,bg_filename='bg.jpg',full_filename='full.jpg'):
        soup=BeautifulSoup(self.browser.page_source,'html.parser')
        bg = soup.find_all('div',{'class':'gt_cut_bg_slice'})
        fullgb = soup.find_all('div',{'class':'gt_cut_fullbg_slice'})
        bg_url=re.findall('image: url(.*?); background-position',bg[0].get('style'))[0][1:-1]
        fullgb_url=re.findall('image: url(.*?); background-position',fullgb[0].get('style'))[0][1:-1]
        print(bg_url)
        print(fullgb_url)
        # bg_url = re.findall('url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
        # fullgb_url = re.findall('url\(\"(.*)\"\);', fullgb[0].get('style'))[0].replace('webp', 'jpg')
        bg_location_list = []
        fullbg_location_list = []
        # print(bg)
        for each_bg in bg:
            location={}
            location['x'] =int(re.findall('background-position: (.*?)px (.*?)px;', each_bg.get('style'))[0][0])
            location['y'] =int(re.findall('background-position: (.*?)px (.*?)px;', each_bg.get('style'))[0][1])
            bg_location_list.append(location)
        for each_fullgb in fullgb:
            location={}
            location['x'] =int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][1])
            fullbg_location_list.append(location)
        r=urlretrieve(url=bg_url, filename=bg_filename)
        print('缺口图片下载完成',r)
        urlretrieve(url=fullgb_url, filename=full_filename)
        print('背景图片下载完成')
        print(bg_location_list)
        print(fullbg_location_list)
        return bg_location_list, fullbg_location_list

    def get_merge_image(self, filename, location_list):
        im = image.open(filename)
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []
        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))
        new_im = image.new('RGB', (260, 116))
        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
            x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]
        new_im.save(filename)
        return new_im

    def is_pixel_equal(self, img1, img2, x, y):
         pix1 = img1.load()[x, y]
         pix2 = img2.load()[x, y]
         threshold = 60
         if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(pix1[2] - pix2[2] < threshold)):
             return True
         else:
             return False

    def get_gap(self, img1, img2):
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        track = []
        track.append(distance*0.3)
        track.append(distance*0.2)
        track.append(distance*0.4)
        track.append(distance*0.1)
        return track

    def get_slider(self):
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, track):
        ActionChains(self.browser).click_and_hold(slider).perform()
        while track:
            x = random.choice(track)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            track.remove(x)
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()


    def crack(self):
        self.open_url()
        bg_filename = 'bg.jpg'
        fullbg_filename = 'fullbg.jpg'
        bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)
        bg_img = self.get_merge_image(bg_filename, bg_location_list)
        fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)
        gap = self.get_gap(fullbg_img, bg_img)
        print('缺口位置', gap)
        track = self.get_track(gap - self.BORDER)
        print('滑动滑块')
        print(track)
        slider = self.get_slider()
        self.move_to_gap(slider, track)
        time.sleep(3)
        self.browser.save_screenshot('index.png')

if __name__=='__main__':
    crawl=Crawl('18281593914','18281593914')
    crawl.crack()
    print('验证成功')
