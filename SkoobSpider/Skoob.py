from selenium import webdriver
from Hush import usuarioEmail, usuarioSenha

browser = webdriver.Firefox()
browser.get("https://www.skoob.com.br/login/")
email = browser.find_element_by_name("data[Usuario][email]")
email.send_keys(usuarioEmail)
pwd = browser.find_element_by_name("data[Usuario][senha]")
pwd.send_keys(usuarioSenha)
entrar = browser.find_element_by_xpath('//*[@id="login-box-col02"]/form/div/div/input')
entrar.click()
link_indice_Skoob = browser.find_element_by_xpath('//*[@id="topoInterno"]/a/img')
link_indice_Skoob.click()
link_cortesia = browser.find_element_by_xpath('//*[@id="home-conteudo"]/div[1]/div[1]/div[2]/a')
link_cortesia.click()

#//*[@id="card3475"]/div[2]/div[4]
for elem in browser.find_elements_by_css_selector('[class *= "participe"]'): #Cada link para participar
   idLivro = elem.get_attribute("rel")
   print (elem.get_attribute("rel") )
   linkParticipe = browser.find_element_by_xpath('//*[@id="card'+idLivro+'"]/div[2]/div[4]/a[1]')
   if( linkParticipe.is_displayed() ): #Clica se der
      from random import randint
      from time import sleep
      sleep(randint(10,100))
      linkParticipe.click()
browser.quit()