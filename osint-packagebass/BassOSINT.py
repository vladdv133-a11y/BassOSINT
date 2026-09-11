import sys
import asyncio
import socket
import logging
import httpx
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import dns.resolver
from colorama import init, Fore, Style

logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

logging.info("BassOSINT successfully started.")

init(autoreset=True)

G = Fore.GREEN
R = Fore.RED
C = Fore.CYAN
Y = Fore.YELLOW
W = Fore.WHITE
DIM = Style.DIM

BANNER = f"""{C}
  ____                  ____  ____ _____ T 
 | __ )  __ _ ___ ___  / __ \/ ___|_   _|
 |  _ \ / _` / __/ __|/ / _` \___ \ | |  
 | |_) | (_| \__ \__ \ / /_/ |___) || |  
 |____/ \__,_|___/___/\____/|____/ |_|  
            {Y}[ OSINT Framework v1.0 ]
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

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
            print(f"{R}No EXIF data found in this image.")
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

        print(f"\n{Y}--- Image Metadata ---")
        if "Make" in exif_data or "Model" in exif_data:
            print(f"{G}Device:{W} {exif_data.get('Make', '')} {exif_data.get('Model', '')}".strip())
        if "DateTimeOriginal" in exif_data:
            print(f"{G}Date/Time:{W} {exif_data.get('DateTimeOriginal')}")
        if "Software" in exif_data:
            print(f"{G}Software:{W} {exif_data.get('Software')}")

        if gps_data:
            lat = convert_to_degrees(gps_data.get("GPSLatitude")) if "GPSLatitude" in gps_data else None
            if gps_data.get("GPSLatitudeRef") == "S" and lat:
                lat = -lat

            lon = convert_to_degrees(gps_data.get("GPSLongitude")) if "GPSLongitude" in gps_data else None
            if gps_data.get("GPSLongitudeRef") == "W" and lon:
                lon = -lon

            if lat and lon:
                print(f"{G}GPS Coordinates:{W} {lat:.6f}, {lon:.6f}")
                print(f"{C}Google Maps Link:{W} https://maps.google.com/?q={lat:.6f},{lon:.6f}")
                logging.info(f"GPS coordinates found: {lat:.6f}, {lon:.6f}")

    except Exception as e:
        print(f"{R}Error processing image: {e}")
        logging.error(f"Error processing image {image_path}: {e}")

def run_metatool():
    path = input(f"\n{Y}Enter path to image file:{W} ").strip()
    if path:
        get_exif_data(path)

def run_user_searcher():
    target = input(f"\n{Y}Enter IP address or Domain for network lookup:{W} ").strip()
    if not target:
        return

    logging.info(f"Launching UserSearcher for target: {target}")
    print(f"\n{C}Fetching info for target: {W}{target}...")
    try:
        response = httpx.get(f"http://ip-api.com/json/{target}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query", headers=HEADERS, timeout=5.0)
        data = response.json()
        if data.get("status") == "success":
            print(f"{G}IP:{W} {data.get('query')}")
            print(f"{G}Country:{W} {data.get('country')}")
            print(f"{G}City:{W} {data.get('city')} ({data.get('regionName')})")
            print(f"{G}Coordinates:{W} {data.get('lat')}, {data.get('lon')}")
            print(f"{G}ISP:{W} {data.get('isp')}")
            print(f"{G}Organization:{W} {data.get('org')}")
            print(f"{G}ASN:{W} {data.get('as')}")
            logging.info(f"Successfully retrieved network data for {target}")
        else:
            print(f"{R}Failed to retrieve data: {data.get('message')}")
            logging.warning(f"Failed to retrieve network data for {target}: {data.get('message')}")
    except Exception as e:
        print(f"{R}Error querying IP API: {e}")
        logging.error(f"UserSearcher error for {target}: {e}")

def run_bass_script():
    domain = input(f"\n{Y}Enter target domain (e.g., example.com):{W} ").strip()
    if not domain:
        return

    logging.info(f"Launching BassScript DNS Recon for domain: {domain}")
    print(f"\n{C}Running DNS Recon for:{W} {domain}\n")

    try:
        ip = socket.gethostbyname(domain)
        print(f"{G}A Record (IP):{W} {ip}")
    except Exception as e:
        print(f"{R}Could not resolve primary IP.")
        logging.warning(f"Could not resolve IP for domain {domain}: {e}")

    record_types = ["MX", "NS", "TXT"]
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            print(f"\n{Y}{rtype} Records:")
            for rdata in answers:
                print(f"  {G}{rdata.to_text()}")
        except Exception:
            pass

    print(f"\n{C}Fetching Subdomains via Certificate Logs...")
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        res = httpx.get(url, headers=HEADERS, timeout=10.0)
        if res.status_code == 200:
            subdomains = set()
            for entry in res.json():
                name = entry.get("name_value")
                if name:
                    subdomains.update(name.split("\n"))
            print(f"{G}Found {len(subdomains)} unique domain/subdomain records:")
            for sub in list(subdomains)[:15]:
                print(f"  {W}{sub}")
            if len(subdomains) > 15:
                print(f"  {DIM}... and {len(subdomains) - 15} more.")
            logging.info(f"Found {len(subdomains)} subdomains for {domain}")
    except Exception as e:
        print(f"{R}Error fetching subdomains: {e}")
        logging.error(f"Error fetching subdomains for {domain}: {e}")

TARGET_SITES = {
    "GitHub": "https://github.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Telegram": "https://t.me/{username}",
    "Steam": "https://steamcommunity.com/id/{username}",
    "Pinterest": "https://www.pinterest.com/{username}/",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Medium": "https://medium.com/@{username}",
    "Pornhub": "https://www.pornhub.com/users/{username}",
    "Chaturbate": "https://chaturbate.com/{username}/",
    "OnlyFans": "https://onlyfans.com/{username}",
    "XHamster": "https://xhamster.com/users/{username}",
}

async def check_site(client: httpx.AsyncClient, site_name: str, url_template: str, username: str):
    url = url_template.format(username=username)
    try:
        response = await client.get(url, headers=HEADERS, timeout=5.0, follow_redirects=True)
        if response.status_code == 200:
            print(f"{G}Found on {site_name}:{W} {url}")
            return site_name, url
        return None
    except httpx.RequestError:
        return None

async def run_all_searcher_async(username: str):
    logging.info(f"Launching AllSearcher for username: {username}")
    print(f"\n{C}Starting AllSearcher for target:{W} '{username}'")
    print(f"{C}Scanning {len(TARGET_SITES)} platforms...\n")

    async with httpx.AsyncClient(http2=True) as client:
        tasks = [
            check_site(client, site, url, username) 
            for site, url in TARGET_SITES.items()
        ]
        results = await asyncio.gather(*tasks)

    found = [res for res in results if res is not None]
    print(f"\n{Y}Scan finished! Matches found: {G}{len(found)}{Y}/{len(TARGET_SITES)}")
    logging.info(f"AllSearcher completed for {username}. Matches found: {len(found)}")

def run_all_searcher():
    username = input(f"\n{Y}Enter username to search:{W} ").strip()
    if username:
        asyncio.run(run_all_searcher_async(username))

def main():
    while True:
        print(BANNER)
        print(f" {Y}1{W} - {G}MeTatool    {W} (EXIF & GPS photo analysis)")
        print(f" {Y}2{W} - {G}UserSearcher{W} (IP & Network details)")
        print(f" {Y}3{W} - {G}BassScript  {W} (Domain, Subdomains & DNS Recon)")
        print(f" {Y}4{W} - {G}AllSearcher {W} (Cross-platform username enum)")
        print(f" {Y}0{W} - {R}Exit\n")

        choice = input(f"{C}BassOSINT >{W} ").strip()

        if choice == "1":
            run_metatool()
        elif choice == "2":
            run_user_searcher()
        elif choice == "3":
            run_bass_script()
        elif choice == "4":
            run_all_searcher()
        elif choice == "0":
            print(f"\n{R}Exiting BassOSINT.")
            logging.info("BassOSINT process terminated.")
            sys.exit(0)
        else:
            print(f"\n{R}Invalid option, try again.")
        
        input(f"\n{DIM}Press Enter to return to main menu...")

if __name__ == "__main__":
    main()