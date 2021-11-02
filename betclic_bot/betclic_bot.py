from typing import Match
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

#Variables de base
login=""
mdp=""
birthdate=""
mise = ""
trueMise = ""

gameHour = 0
gameMin = 0
startAgainHour = 0

tsmin = 2
tsmed = 5
tsmax = 10
curMoney = 0
afterBetMoney = 0
stateMoney=0
betStep = 1

def setParamsFunction():
    
    global login,mdp,birthdate,mise,trueMise

    f = open("bot_config.txt", "r")
    login = f.readline().split("=")[1].strip()
    mdp = f.readline().split("=")[1].strip()
    birthdate = f.readline().split("=")[1].strip()
    mise = f.readline().split("=")[1].strip()
    trueMise = float(mise)
    #print(login," ",mdp," ",birthdate, " ",mise)


def checkClass(theElement,classNeedle):
    classes = theElement.get_attribute("class").split(" ")
    for c in classes :
        if(c==classNeedle) :
            return True

    return False

def hasAttribute(theElement,theAttribute):
    val = theElement.get_attribute(theAttribute)
    if val!="": 
        return True
    else : return False

def connexion():

    driver.get("https://m.betclic.fr/connexion")
    time.sleep(tsmed)
    #Close pop up page
    EC.presence_of_element_located((By.ID, "popin_tc_privacy_button_3"))
    elem = driver.find_element(By.ID,"popin_tc_privacy_button_3")
    elem.click()
    #Username
    elem = driver.find_element(By.CLASS_NAME,"forms_inputText")
    elem.clear()
    elem.send_keys(login)
    #Password
    elem = driver.find_element(By.CLASS_NAME,"forms_inputPassword")
    elem.clear()
    elem.send_keys(mdp)
    elem = driver.find_elements(By.CLASS_NAME,"button")[0]
    elem.click()
    time.sleep(tsmin)
    #birthdate to confirm account
    elem = driver.find_element(By.ID,"date")
    elem.clear()
    elem.send_keys(birthdate)
    elem = driver.find_elements(By.CLASS_NAME,"button")[0]
    elem.click()
    time.sleep(tsmed)
    driver.get("https://m.betclic.fr/football-s1")
    time.sleep(tsmed)


def getAccountMoney():

    global curMoney
    #On récupère l'argent
    elem = driver.find_elements(By.TAG_NAME,"span")[2]
    curMoney = elem.text.split("€")[0].strip()
    curMoney = curMoney.replace(",",".")


def placeBet(theMatch):

    driver.get(theMatch)

    time.sleep(tsmin)

    elemArray = driver.find_elements(By.CLASS_NAME,"button")
    for e in elemArray :
        if(e.text=="J'ai compris") :
            e.click()
            break

    #On va sur la page de la première mi temps  
    elemArray = driver.find_elements(By.CLASS_NAME,"tabs_link")
    for e in elemArray :
        if(e.text=="1ère MT") :
            e.click()
            break
    
    #Scroll
    elem = driver.find_elements(By.CLASS_NAME,"oddButtonWrapper")[6]
    driver.execute_script("arguments[0].scrollIntoView();", elem)

    #On sélection le résultat de la première mi-temps
    elem = driver.find_elements(By.CLASS_NAME,"oddButtonWrapper")[12]
    elem.click()

    time.sleep(tsmin)

    elem =  driver.find_element(By.ID,"lqfmj")
    elem.click()

    time.sleep(tsmin)

    #On place la mise
    elem =  driver.find_element(By.NAME,"stakeField")
    elem.clear()
    elem.send_keys(mise)

    #On confirme le pari
    elem =  driver.find_element(By.ID,"betBtn")
    elem.click()

    time.sleep(tsmin)

    #On ferme la page de confirmation du pari
    elem =  driver.find_element(By.ID,"closeBetConfirmation")
    elem.click()

    time.sleep(tsmin)


def botFunction():

    #Variables + tableaux
    global gameHour,gameMin,startAgainHour,mise
    matchIndexes=[]
    allMatches=[]

    #On récupère la première heure de trouver (si heure, alors match pas commencé)
    cardEvent = driver.find_elements(By.CLASS_NAME,"cardEvent")
    count = 0
    for c in cardEvent:
        if(checkClass(c,"is-live")) : count+=1

    hourElem = driver.find_elements(By.CLASS_NAME,"scoreboard_hour")
    dateElem = driver.find_elements(By.CLASS_NAME,"scoreboard_date")
    baseH,baseM="",""

    for he in hourElem:
        #Si on a pas d'heure de base, on set et on se base la dessus pour le reste
        if(baseH=="" and baseM==""):
            baseH = int(he.text.split(":")[0])
            baseM = int(he.text.split(":")[1])
            gameHour=baseH
            gameMin=baseM
            startAgainHour = 0 if (gameHour+1 > 24) else gameHour+1  

        h=int(he.text.split(":")[0])
        m=int(he.text.split(":")[1])
        # and dateElem[hourElem.index(he)].text==""
        if(h==baseH and m==baseM):
            matchIndexes.append(hourElem.index(he)+count)

    #Si on a trouvé des matchs
    if(len(matchIndexes)>0):

        betMade=0
        #On récupère les liens de matchs
        for m in matchIndexes:
            theElem = driver.find_elements(By.CLASS_NAME,"cardEvent")[m]
            allMatches.append(theElem.get_attribute("href"))

        #Pour chacun des matchs
        for match in allMatches:

            #On récupère l'argent
            getAccountMoney()

            #Si on a assez d'argent
            if(float(curMoney)>=float(mise)):
                if(betStep>1 and betMade>0):mise=trueMise
                placeBet(match)
                betMade+=1
                time.sleep(tsmin)
            else : #Sinon
                print("Il n'y a pas assez d'argent pour miser !")
                break
        
        if(betMade>0):
            #On met à jour le fichier d'état après pari
            elem = driver.find_elements(By.TAG_NAME,"span")[2]
            afterBetMoney = elem.text.split("€")[0].strip()
            file = open("state.txt", "w")
            file.write("AfterBetMoney="+str(afterBetMoney))
            file.write("\nBetStep="+str(betStep))
            file.close()

            print("***** ",betMade," Match(s) parié(s) ! Début : ",gameHour," H ",gameMin, " | Reprise du programme à : ",startAgainHour," H ",gameMin," *****")

    #Pour éviter de fermer la page trop vite : à retirer
    time.sleep(tsmed)

    #elem.send_keys(Keys.RETURN)
    #assert "No results found." not in driver.page_source
    driver.quit() 


setParamsFunction()

while True:
    try:
        driver = webdriver.Firefox()
        connexion()
        botFunction()
        break
    except: 
        print("error")
        driver.quit() 

starttime = time.time()

def getState():

    global stateMoney,betStep,trueMise

    f = open("state.txt", "r")
    stateMoney = f.readline().split("=")[1].strip()
    stateMoney = stateMoney.replace(",",".")
    betStep = int(f.readline().split("=")[1].strip())


def displayState():
    print("***** État ***** \n"
    "Argent actuel : "+curMoney+"\n"
    "Cycle(s) perdu(s) : ",betStep-1)


while True:

    now = datetime.datetime.now()
    
    if(now.hour == startAgainHour and now.minute >= gameMin):
        print(now.hour," : ",now.minute," : Activation. ")
        getState()
        driver = webdriver.Firefox()
        try:
            connexion()
            getAccountMoney()
            if(float(curMoney)<=float(stateMoney)):
                betStep *= 2
            else: betStep=1

            displayState()
            mise = float(mise)*betStep
            botFunction()
            mise = trueMise
        except:
            print("error")
            driver.quit() 


    time.sleep(300.0 - ((time.time() - starttime) % 300.0)) #toutes les 5 mins


#assert "Betclic" in driver.title
