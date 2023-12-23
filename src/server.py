import argparse
import socket
import sys
from _thread import *
import requests
from bs4 import BeautifulSoup as bs
import bs4
from bs4.element import Tag

#from decouple import config

try:
    listening_port = 8080 #config('PORT', cast=int)
except KeyboardInterrupt:
    print("\n[*] User has requested an interrupt")
    print("[*] Application Exiting.....")
    sys.exit()

parser = argparse.ArgumentParser()

parser.add_argument('--max_conn', help="Maximum allowed connections", default=5, type=int)
parser.add_argument('--buffer_size', help="Number of samples to be used", default=8192, type=int)

args = parser.parse_args()
max_connection = args.max_conn
buffer_size = args.buffer_size


def link_replacinator(html_blob:str, website_adress:str ) -> str:
    soup = bs(html_blob, 'html.parser')
    for anchor in soup.find_all('a'):
        anchor["href"] = replace_link_path(anchor.get('href'), website_adress)
    for link in soup.find_all("link"):
        link["href"] = replace_link_path(link.get('href'), website_adress)
    for script in soup.find_all("script"):
        script["src"] = replace_link_path(script.get('src'), website_adress)
    for base_header in soup.find_all("base"):
        base_checker = True
        base_header["href"] = replace_link_path(base_header.get('href'), website_adress)
    if not base_checker:
        base_tag = bs4.element.Tag(name="base", attrs=dict({"href": "https://accounts.google.com/v3/signin/"}))
        for hed in soup.find_all("head"):
            soup.append(base_tag)
    return str(soup)


def replace_link_path(link_path_original, website_adress):
    if link_path_original.startswith('http'):
        link_path_our = 'http://seanmac.org/' + link_path_original
    else:
        link_path_our = 'http://seanmac.org/' + (website_adress + link_path_original)
    return link_path_our


def start():    #Main Program
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', listening_port))
        sock.listen(max_connection)
        print("[*] Server started successfully [ %d ]" %(listening_port))
    except Exception:
        print("[*] Unable to Initialize Socket")
        print(Exception)
        sys.exit(2)

    while True:
        try:
            conn, addr = sock.accept() #Accept connection from client browser
            data = conn.recv(buffer_size) #Recieve client data
            start_new_thread(conn_string, (conn,data, addr)) #Starting a thread
        except KeyboardInterrupt:
            sock.close()
            print("\n[*] Graceful Shutdown")
            sys.exit(0)

def conn_string(conn, data, addr):
    #try:
        print(data)
        print("-"*80)
        # GET /http://google.com HTTP/1.1\r
        first_line = data.split(b'\n')[0]

        # GET /http://google.com HTTP/1.1\r
        #     ^----------------^
        #           url
        url = first_line.split()[1]

        webserver = url[1:]
        #print(data)
        print("-"*80)
        print(f"Webserver: {webserver}") #Port: {port}")
        proxy_server(webserver, conn, addr)


def proxy_server(webserver, conn, addr):
    try:
        url = webserver.decode("UTF-8")

        response = requests.get(url)
        our_html = link_replacinator(response.text, url)
        if response.status_code == 200:
            status_line = "HTTP/1.1 200 OK"
            response_header = "Content-Type: text/html"
            http_response = f"{status_line}\n{response_header}\n\n{our_html}"
            conn.send(bytes(http_response, "UTF-8"))

        conn.close()
    except socket.error:
        conn.close()
        sys.exit(1)


if __name__== "__main__":
    start()
