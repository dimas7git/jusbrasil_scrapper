import csv
import time
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

options = ChromeOptions()
options.add_argument("--no-sandbox")

with Chrome(options=options) as driver:
    empresas = [
        "Nike do Brasil Comércio e Participações Ltda.",
        "Adidas do Brasil Ltda.",
        "Puma do Brasil Ltda.",
        "Reebok Produtos Esportivos Ltda.",
        "Asics Brasil, Distribuição e Comércio de Artigos Esportivos Ltda.",
        "Under Armour Brasil Comércio e Distribuição de Artigos Esportivos Ltda"
    ]

    # Iterando sobre cada empresa na lista
    for empresa in empresas:
        with open(f"{empresa}.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Número do Processo", "Tribunal", "Localidade", "Partes Envolvidas", "Procedimentos"])

            pesquisa_url = f"https://www.jusbrasil.com.br/consulta-processual/busca?q={'+'.join(empresa.split())}"
            driver.get(pesquisa_url)

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.EntitySnippet-header-img a")))

            # Acessando o primeiro resultado da pesquisa (URL de um processo específico)
            primeiro_resultado = driver.find_element(By.CSS_SELECTOR, "div.EntitySnippet-header-img a")
            link_processo = primeiro_resultado.get_attribute("href")
            driver.get(link_processo)

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.LawsuitCardPersonPage-card")))

            def scroll_to_bottom():
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(7)

            scroll_to_bottom()

            # Localizando todos os elementos que representam os processos na página
            processos = driver.find_elements(By.CSS_SELECTOR, "div.LawsuitCardPersonPage-card")
            numeros_processos = []

            max_processos = 50

            # Loop para extrair os números dos processos
            for processo in processos:
                numero_processo = processo.find_element(By.CSS_SELECTOR, "span.LawsuitCardPersonPage-header-processNumber").text.strip()
                numeros_processos.append(numero_processo)

                # Parar a extração se atingir o limite de 50 processos
                if len(numeros_processos) >= max_processos:
                    break

            # Loop para extrair os detalhes de cada processo através dos numeros extraidos dos processos
            for numero_processo in numeros_processos:
                processo_element = driver.find_element(By.XPATH, f"//span[text()='{numero_processo}']/ancestor::div[contains(@class, 'LawsuitCardPersonPage-card')]")
            
                tribunal_element = processo_element.find_element(By.CSS_SELECTOR, "p.LawsuitCardPersonPage-body-row-item-text[role='body-court']")
                tribunal_text = tribunal_element.text.strip()
                tribunal = ""
                localidade = ""
                if "·" in tribunal_text:
                    tribunal = tribunal_text.split("·")[0].strip()
                    localidade = tribunal_text.split("·")[1].strip()

                partes_envolvidas_element = processo_element.find_element(By.CSS_SELECTOR, "strong.LawsuitCardPersonPage-header-processInvolved")
                partes_envolvidas = partes_envolvidas_element.text.strip()

                procedimentos = ""
                try:
                    procedimentos_element = processo_element.find_element(By.CSS_SELECTOR, "p.LawsuitCardPersonPage-body-row-item-text[role='body-kind']")
                    procedimentos = procedimentos_element.text.strip()
                except NoSuchElementException:
                    procedimentos = ""

                writer.writerow([numero_processo, tribunal, localidade, partes_envolvidas, procedimentos])
