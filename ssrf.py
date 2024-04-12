import requests # type: ignore
from colorama import Fore, Style, init # type: ignore
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup # type: ignore

init(autoreset=True)

# Webhook linkini global olarak tanımla
webhook_linki = None

def extract_links(html_content, base_url):
    links = set()
    soup = BeautifulSoup(html_content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        links.add(full_url)
    return links

def subdomain_tarama(domain, subdomain_listesi):
    try:
        with open(subdomain_listesi, "r") as dosya:
            subdomains = dosya.readlines()
    except FileNotFoundError:
        print(Fore.RED + f"{subdomain_listesi} bulunamadı.")
        return

    base_url = f"http://{domain}"
    for subdomain in subdomains:
        url = f"http://{subdomain.strip()}.{domain}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(Fore.BLUE + Style.BRIGHT + f"[Subdomain] Bulundu: {url}")
                ssrf_tarama(url)
        except requests.ConnectionError:
            pass

def directory_tarama(domain, directory_listesi):
    try:
        with open(directory_listesi, "r") as dosya:
            directories = dosya.readlines()
    except FileNotFoundError:
        print(Fore.RED + f"{directory_listesi} bulunamadı.")
        return

    base_url = f"http://{domain}"
    for directory in directories:
        url = urljoin(base_url, directory.strip())
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(Fore.BLUE + Style.BRIGHT + f"[Directory] Bulundu: {url}")
                ssrf_tarama(url)
        except requests.ConnectionError:
            pass

def ssrf_tarama(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[-] Hata: {response.status_code} - İstek başarısız oldu.")
            return
        
        print(f"[+] URL taraması başlatıldı: {url}")

        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
        discovered_links = extract_links(response.text, base_url)

        for link in discovered_links:
            if urlparse(link).scheme in ['http', 'https']:  # Sadece HTTP ve HTTPS bağlantılarını tarar
                try:
                    response = requests.get(link)
                    if response.status_code == 200:
                        webhook_istegi(link)
                except requests.RequestException as e:
                    print(f"[-] Hata: {e}")
    except requests.RequestException as e:
        print(f"[-] Hata: {e}")

def webhook_istegi(link):
    global webhook_linki  # Global değişkeni kullan

    if webhook_linki is not None:
        try:
            response = requests.get(webhook_linki)
            if response.status_code == 200:
                print(Fore.RED + Style.BRIGHT + f"[+] Potansiyel SSF Zafiyeti Bulundu: {link}")
            else:
                print(f"[-] Webhook İsteği Başarısız: {link}")
        except requests.RequestException as e:
            print(f"[-] Hata: {e}")
    else:
        print(Fore.RED + "Webhook linki belirtilmedi.")

if __name__ == "__main__":
    domain = input(Fore.YELLOW + "Ana domaini girin (örn: example.com): ")
    subdomain_listesi = input(Fore.YELLOW + "Subdomain listesi dosyasının adını girin: ")
    directory_listesi = input(Fore.YELLOW + "Directory listesi dosyasının adını girin: ")
    
    webhook_linki = input(Fore.YELLOW + "Webhook linkini girin: ")

    print(Fore.YELLOW + "\nSubdomain Taraması Başlatılıyor...")
    subdomain_tarama(domain, subdomain_listesi)
    
    print(Fore.YELLOW + "\nDirectory Taraması Başlatılıyor...")
    directory_tarama(domain, directory_listesi)
