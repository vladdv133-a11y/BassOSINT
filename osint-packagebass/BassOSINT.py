import sys
import os
import re
import socket
import asyncio
import logging
import httpx
from urllib.parse import urlparse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import dns.resolver
from colorama import init, Fore, Style

init(autoreset=True)

logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Red Theme Palette
R = Fore.RED + Style.BRIGHT
DR = Fore.RED
W = Fore.WHITE + Style.BRIGHT
DIM = Fore.BLACK + Style.BRIGHT
RESET = Style.RESET_ALL

BANNER = f"""{R}
██████╗  █████╗ ███████╗███████╗ ██████╗ ███████╗██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
██████╔╝███████║███████╗███████╗██║   ██║███████╗██║██╔██╗ ██║   ██║   
██╔══██╗██╔══██║╚════██║╚════██║██║   ██║╚════██║██║██║╚██╗██║   ██║   
██████╔╝██║  ██║███████║███████║╚██████╔╝███████║██║██║ ╚████║   ██║   
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   
{DIM}[ BassOSINT Framework v2.6 – Red Edition ]{RESET}
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

TARGET_SITES = {
    "GitHub": "https://github.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Telegram": "https://t.me/{username}",
    "Steam": "https://steamcommunity.com/id/{username}",
    "Pinterest": "https://www.pinterest.com/{username}/",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Medium": "https://medium.com/@{username}",
    "DockerHub": "https://hub.docker.com/u/{username}",
    "SoundCloud": "https://soundcloud.com/{username}",
    "Vimeo": "https://vimeo.com/{username}",
    "Pornhub": "https://www.pornhub.com/users/{username}",
    "Chaturbate": "https://chaturbate.com/{username}/",
    "OnlyFans": "https://onlyfans.com/{username}",
    "XHamster": "https://xhamster.com/users/{username}",
}

def print_status(symbol, text, color=R):
    print(f"{DIM}[{color}{symbol}{RESET}{DIM}]{RESET} {text}")

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image_path):
    try:
        logging.info(f"Processing EXIF image: {image_path}")
        image = Image.open(image_path)
        exif = image._getexif()
        if not exif:
            print_status("!", "No EXIF data found in this image.", DR)
            logging.warning(f"No EXIF data present in file: {image_path}")
            return

        exif_data = {}
        gps_data = {}

        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id in value:
                    sub_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[sub_tag] = value[gps_tag_id]
            else:
                exif_data[tag] = value

        print(f"\n{R}--- Image Metadata ---{RESET}")
        if "Make" in exif_data or "Model" in exif_data:
            print(f"  {DIM}└─>{RESET} Device:    {W}{exif_data.get('Make', '')} {exif_data.get('Model', '')}{RESET}".strip())
        if "DateTimeOriginal" in exif_data:
            print(f"  {DIM}└─>{RESET} Date/Time: {W}{exif_data.get('DateTimeOriginal')}{RESET}")
        if "Software" in exif_data:
            print(f"  {DIM}└─>{RESET} Software:  {W}{exif_data.get('Software')}{RESET}")

        if gps_data:
            lat = convert_to_degrees(gps_data.get("GPSLatitude")) if "GPSLatitude" in gps_data else None
            if gps_data.get("GPSLatitudeRef") == "S" and lat:
                lat = -lat

            lon = convert_to_degrees(gps_data.get("GPSLongitude")) if "GPSLongitude" in gps_data else None
            if gps_data.get("GPSLongitudeRef") == "W" and lon:
                lon = -lon

            if lat and lon:
                print(f"  {DIM}└─>{RESET} GPS:       {W}{lat:.6f}, {lon:.6f}{RESET}")
                print(f"  {DIM}└─>{RESET} Maps Link: {R}https://maps.google.com/?q={lat:.6f},{lon:.6f}{RESET}")
                logging.info(f"GPS coordinates found: {lat:.6f}, {lon:.6f}")

    except Exception as e:
        print_status("!", f"Error processing image: {e}", DR)
        logging.error(f"Error processing image {image_path}: {e}")

def run_metatool():
    path = input(f"\n{R}Enter path to image file > {W}").strip()
    if path:
        get_exif_data(path)

def run_user_searcher():
    target = input(f"\n{R}Enter IP address or Domain > {W}").strip()
    if not target:
        return

    logging.info(f"Launching UserSearcher for target: {target}")
    print_status("*", f"Fetching info for target: {W}{target}{RESET}", R)
    try:
        response = httpx.get(f"http://ip-api.com/json/{target}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query", headers=HEADERS, timeout=5.0)
        data = response.json()
        if data.get("status") == "success":
            print(f"  {DIM}└─>{RESET} IP:           {W}{data.get('query')}{RESET}")
            print(f"  {DIM}└─>{RESET} Country:      {W}{data.get('country')}{RESET}")
            print(f"  {DIM}└─>{RESET} City:         {W}{data.get('city')} ({data.get('regionName')}){RESET}")
            print(f"  {DIM}└─>{RESET} Coordinates:  {W}{data.get('lat')}, {data.get('lon')}{RESET}")
            print(f"  {DIM}└─>{RESET} ISP:          {W}{data.get('isp')}{RESET}")
            print(f"  {DIM}└─>{RESET} Organization: {W}{data.get('org')}{RESET}")
            print(f"  {DIM}└─>{RESET} ASN:          {W}{data.get('as')}{RESET}")
            logging.info(f"Successfully retrieved network data for {target}")
        else:
            print_status("!", f"Failed to retrieve data: {data.get('message')}", DR)
            logging.warning(f"Failed to retrieve network data for {target}: {data.get('message')}")
    except Exception as e:
        print_status("!", f"Error querying IP API: {e}", DR)
        logging.error(f"UserSearcher error for {target}: {e}")

def run_bass_script():
    domain = input(f"\n{R}Enter target domain > {W}").strip()
    if not domain:
        return

    logging.info(f"Launching BassScript DNS Recon for domain: {domain}")
    print_status("*", f"Running DNS Recon for: {W}{domain}{RESET}", R)

    try:
        ip = socket.gethostbyname(domain)
        print(f"  {DIM}└─>{RESET} A Record (IP): {W}{ip}{RESET}")
    except Exception as e:
        print_status("!", "Could not resolve primary IP.", DR)
        logging.warning(f"Could not resolve IP for domain {domain}: {e}")

    record_types = ["MX", "NS", "TXT"]
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"\n{R}{rtype} Records:{RESET}")
            for rdata in answers:
                print(f"  {DIM}└─>{RESET} {W}{rdata.to_text()}{RESET}")
        except Exception:
            pass

    print_status("*", "Fetching Subdomains via Certificate Logs...", R)
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        res = httpx.get(url, headers=HEADERS, timeout=10.0)
        if res.status_code == 200:
            subdomains = set()
            for entry in res.json():
                name = entry.get("name_value")
                if name:
                    subdomains.update(name.split("\n"))
            print_status("+", f"Found {len(subdomains)} unique domain/subdomain records:", R)
            for sub in list(subdomains)[:15]:
                print(f"  {DIM}└─>{RESET} {W}{sub}{RESET}")
            if len(subdomains) > 15:
                print(f"  {DIM}... and {len(subdomains) - 15} more.{RESET}")
            logging.info(f"Found {len(subdomains)} subdomains for {domain}")
    except Exception as e:
        print_status("!", f"Error fetching subdomains: {e}", DR)
        logging.error(f"Error fetching subdomains for {domain}: {e}")

def run_url_status():
    target_url = input(f"\n{R}Enter URL or Domain > {W}").strip()
    if not target_url:
        return
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    print_status("*", f"URLStatus Analyzing: {W}{target_url}{RESET}", R)
    try:
        res = httpx.get(target_url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        html = res.text
        
        scripts = re.findall(r'<script [^>]*src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.IGNORECASE)
        
        external_domains = set()
        base_domain = urlparse(target_url).netloc
        for link in links:
            domain = urlparse(link).netloc
            if domain and domain != base_domain:
                external_domains.add(domain)

        print(f"  {DIM}└─>{RESET} Status Code:       {W}{res.status_code}{RESET}")
        print(f"  {DIM}└─>{RESET} External Scripts:  {W}{len(scripts)}{RESET}")
        print(f"  {DIM}└─>{RESET} Linked Domains:    {W}{len(external_domains)}{RESET}")
        
        if external_domains:
            print(f"  {DIM}└─>{RESET} Connected Domains: {W}{', '.join(list(external_domains)[:5])}{RESET}")

    except Exception as e:
        print_status("!", f"URLStatus Error: {e}", DR)

def run_bass_script_2():
    target_url = input(f"\n{R}Enter Target URL or Domain > {W}").strip()
    if not target_url:
        return
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    print_status("*", f"BassScript2 Tech Detection for: {W}{target_url}{RESET}", R)
    try:
        res = httpx.get(target_url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        html = res.text
        headers_str = str(res.headers).lower()
        techs = []

        server = res.headers.get("server")
        if server:
            techs.append(f"Server: {server}")

        cms_patterns = {
            "WordPress": r"wp-content|wp-includes",
            "Joomla": r"joomla",
            "Drupal": r"Drupal",
            "Shopify": r"cdn.shopify.com",
            "Tilda": r"tildacdn"
        }
        for cms, pattern in cms_patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                techs.append(f"CMS: {cms}")

        analytics_patterns = {
            "Google Analytics": r"googletagmanager|google-analytics",
            "Yandex Metrika": r"mc.yandex.ru",
            "Cloudflare": r"cloudflare",
            "Facebook Pixel": r"connect.facebook.net"
        }
        for service, pattern in analytics_patterns.items():
            if re.search(pattern, html, re.IGNORECASE) or re.search(pattern, headers_str, re.IGNORECASE):
                techs.append(f"Service/CDN: {service}")

        js_patterns = {
            "React": r"react|react-dom",
            "Vue.js": r"vue",
            "jQuery": r"jquery"
        }
        for js, pattern in js_patterns.items():
            if re.search(pattern, html, re.IGNORECASE):
                techs.append(f"JS Framework: {js}")

        if techs:
            for tech in techs:
                print(f"  {DIM}└─>{RESET} Detected Tech: {W}{tech}{RESET}")
        else:
            print(f"  {DIM}└─>{RESET} No specific technology patterns detected.", DIM)

    except Exception as e:
        print_status("!", f"BassScript2 Error: {e}", DR)

async def check_site(client: httpx.AsyncClient, site_name: str, url_template: str, username: str):
    url = url_template.format(username=username)
    try:
        response = await client.get(url, headers=HEADERS, timeout=5.0, follow_redirects=True)
        if response.status_code == 200:
            print_status("+", f"{site_name:<15} : {W}{url}{RESET}", R)
            return site_name, url
        else:
            print_status("-", f"{site_name:<15} : Not Found", DIM)
            return None
    except Exception:
        print_status("!", f"{site_name:<15} : Timeout/Error", DR)
        return None

async def run_all_searcher_async(username: str):
    logging.info(f"Launching AllSearcher for username: {username}")
    print_status("*", f"Starting AllSearcher for target: '{W}{username}{RESET}'", R)
    print_status("*", f"Scanning {len(TARGET_SITES)} platforms...", R)
    print(DIM + "-" * 60 + RESET)

    async with httpx.AsyncClient(http2=True) as client:
        tasks = [
            check_site(client, site, url, username) 
            for site, url in TARGET_SITES.items()
        ]
        results = await asyncio.gather(*tasks)

    found = [res for res in results if res is not None]
    print(DIM + "-" * 60 + RESET)
    print_status("OK", f"Scan finished! Matches found: {W}{len(found)}{R}/{len(TARGET_SITES)}{RESET}", R)
    logging.info(f"AllSearcher completed for {username}. Matches found: {len(found)}")

def run_all_searcher():
    username = input(f"\n{R}Enter username to search > {W}").strip()
    if username:
        asyncio.run(run_all_searcher_async(username))

def run_shodan_public():
    target_ip = input(f"\n{R}Enter Target IP > {W}").strip()
    if not target_ip:
        return

    print_status("*", f"Querying Public Shodan InternetDB API for: {W}{target_ip}{RESET}", R)
    url = f"https://internetdb.shodan.io/{target_ip}"
    
    try:
        res = httpx.get(url, headers=HEADERS, timeout=8.0)
        if res.status_code == 200:
            data = res.json()
            print(f"\n{R}--- Public Shodan Intelligence ---{RESET}")
            print(f"  {DIM}└─>{RESET} IP:          {W}{data.get('ip')}{RESET}")
            
            hostnames = data.get('hostnames', [])
            print(f"  {DIM}└─>{RESET} Hostnames:   {W}{', '.join(hostnames) if hostnames else 'None'}{RESET}")
            
            ports = data.get('ports', [])
            print(f"  {DIM}└─>{RESET} Open Ports:  {W}{', '.join(map(str, ports)) if ports else 'None'}{RESET}")
            
            cves = data.get('cves', [])
            if cves:
                print(f"  {DIM}└─>{RESET} Vulnerabilities (CVEs): {R}{', '.join(cves[:10])}{RESET}")
                if len(cves) > 10:
                    print(f"      {DIM}...and {len(cves) - 10} more CVEs{RESET}")
            else:
                print(f"  {DIM}└─>{RESET} Vulnerabilities: {W}No known CVEs{RESET}")
                
            tags = data.get('tags', [])
            if tags:
                print(f"  {DIM}└─>{RESET} Tags:         {W}{', '.join(tags)}{RESET}")

            logging.info(f"Shodan Public API query successful for {target_ip}")
        elif res.status_code == 404:
            print_status("!", "No records found in Shodan InternetDB for this IP.", DR)
        else:
            print_status("!", f"Server returned status code: {res.status_code}", DR)

    except Exception as e:
        print_status("!", f"Error querying Public API: {e}", DR)
        logging.error(f"Shodan Public API error for {target_ip}: {e}")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        print(BANNER)
        print(f" {R}1{RESET} - {W}MeTatool{RESET}       (EXIF & GPS photo analysis)")
        print(f" {R}2{RESET} - {W}UserSearcher{RESET}   (IP & Network details)")
        print(f" {R}3{RESET} - {W}BassScript{RESET}     (Domain, Subdomains & DNS Recon)")
        print(f" {R}4{RESET} - {W}URLStatus{RESET}      (External scripts & Linked domains)")
        print(f" {R}5{RESET} - {W}BassScript2{RESET}    (CMS, Frameworks & Tech Analyzer)")
        print(f" {R}6{RESET} - {W}AllSearcher{RESET}    (Cross-platform username enum)")
        print(f" {R}7{RESET} - {W}ShodanPublic{RESET}   (Free Anonymous Ports & Vulnerability Recon)")
        print(f" {R}0{RESET} - {DR}Exit{RESET}\n")

        choice = input(f"{R}BassOSINT > {W}").strip()

        if choice == "1":
            run_metatool()
        elif choice == "2":
            run_user_searcher()
        elif choice == "3":
            run_bass_script()
        elif choice == "4":
            run_url_status()
        elif choice == "5":
            run_bass_script_2()
        elif choice == "6":
            run_all_searcher()
        elif choice == "7":
            run_shodan_public()
        elif choice == "0":
            print(f"\n{DR}Exiting BassOSINT.{RESET}")
            logging.info("BassOSINT process terminated.")
            sys.exit(0)
        else:
            print(f"\n{DR}Invalid option, try again.{RESET}")
        
        input(f"\n{DIM}Press Enter to return to main menu...{RESET}")

if __name__ == "__main__":
    main()