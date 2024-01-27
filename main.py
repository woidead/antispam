import shutil

from telethon import TelegramClient, sync, events
import threading
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, CreateNewSession, UseCurrentSession
import asyncio
import socks
from datetime import datetime
import configparser

from random import randint

from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.errors import FloodWaitError

from threading import Thread

import time
import requests
import os
import sys

import dearpygui.dearpygui as dpg

big_let_start = 0x00C0  # Capital "A" in cyrillic alphabet
big_let_end = 0x00DF  # Capital "Я" in cyrillic alphabet
small_let_end = 0x00FF  # small "я" in cyrillic alphabet
remap_big_let = 0x0410  # Starting number for remapped cyrillic alphabet
alph_len = big_let_end - big_let_start + 1  # adds the shift from big letters to small
alph_shift = remap_big_let - big_let_start

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def to_cyr(instr):
    out = []
    for i in range(0, len(instr)):  # 5 значенний и +1 после круга
        if ord(instr[i]) in range(big_let_start, small_let_end + 1):
            out.append(chr(ord(instr[i]) + alph_shift))
        else:
            out.append(instr[i])
    return ''.join(out)


class Proxy():

    def __init__(self, proxy_type):
        self.proxy_type = int(proxy_type)

    def get_proxy_am(self, link, i):
        proxies = requests.get(link)
        print("Using proxy:", proxies.text.split("\n")[i])
        addr = proxies.text.split("\n")[i].split(":")[0]
        port = proxies.text.split("\n")[i].split(":")[1]
        return addr, port

    def get_proxy(self, i):
        if self.proxy_type == 0:
            link = open("proxy.txt", "r").read()
            if link == "":
                print("[!] No link for proxy.am in proxy.txt [!]")
                sys.exit(1)
            return self.get_proxy_am(link, i)
        if self.proxy_type == 1:
            proxies = open("proxy.txt", "r").read().split("\n")
            proxy = proxies[i].split(":")
            return proxy[0], proxy[1]
        if self.proxy_type == 2:
            return "", ""


async def authorize(proxy, tname):
    config = configparser.ConfigParser()

    config.read("config.txt")

    proxy_type = config.get("myvars", "proxy_type")

    tdesk = TDesktop(f"tdatas/{tname}")


    api = API.TelegramIOS.Generate()
    prox = Proxy(proxy_type)
    addr, port = prox.get_proxy(proxy)
    if addr == "" or port == "":
        try:
            client = await tdesk.ToTelethon(f"sessions/{tname}.session",
                                            UseCurrentSession,
                                            api,
                                            )
            await client.connect()
        except:
            pprint("Нерабочий аккаунт!")
            return
    else:
        try:
            client = await tdesk.ToTelethon(f"sessions/{tname}.session", UseCurrentSession, api,
                                            proxy=(socks.SOCKS5, addr, int(port), True, "i17t3011117", "ee8mnJDjOK"),
                                            connection_retries=0,
                                            retry_delay=1,
                                            auto_reconnect=True,
                                            request_retries=0)
            await client.connect()
        except Exception as e:
            if "ConnectionError" in str(e):
                pprint(f"{tname} | Нерабочие прокси: {addr}:{port}")
                pprint(f"{tname} | Заменяем прокси")
                return authorize(proxy + 1, tname)
            else:
                print(e)
                pprint("Нерабочий аккаунт!")
                return

    return client


def clear_tdata(name):
    try:
        for file in os.listdir(f"./tdatas/{name}"):
            if str(file) in ["dumps", "emoji", "user_data"]:
                shutil.rmtree(f"./tdatas/{name}/{file}")
    except Exception as e:
        pass


def startarc():

    global message_threads
    message_threads = []

    try:
        os.remove("./tdatas/.gitkeep")
    except:
        pass
    while True:
        for proxy, tdataname in enumerate(os.listdir(f"./tdatas")):
            clear_tdata(tdataname)
            try:
                t = Thread(target=startall, args=(proxy, tdataname,)).start()
            except:
                pass
            time.sleep(1)
        return


def startall(proxy, tdataname):
    asyncio.run(startik(proxy, tdataname))


async def startik(proxy, tdataname):
    try:
        client = await authorize(proxy, tdataname)

    except (IOError, OSError) as e:
        pass
        await client.disconnect()
        try:
            os.remove(f"./sessions/{tdataname}.session")
            os.remove(f"./sessions/{tdataname}.session-journal")
        except Exception as e:
            pass
        return
    except Exception as e:
        pass
        if str(e) == "The phone number is invalid (caused by SendCodeRequest)":
            os.rename("tdata", "Banned tdata")
        await client.disconnect()
        try:
            os.remove(f"./sessions/{tdataname}.session")
            os.remove(f"./sessions/{tdataname}.session-journal")
        except Exception as e:
            pass
        return

    pprint(f"{tdataname} working...")
    try:
        config = configparser.ConfigParser()

        config.read("config.txt")

        message = to_cyr(dpg.get_value("mess"))
        await mainn(message, tdataname, client, proxy)
    except Exception as e:
        print(e)

        print("some error, trying again...")


async def send_message_with_timeout(tdataname, dialog, mess, proxy):

    try:
        client = await authorize(proxy, tdataname)

    except (IOError, OSError) as e:
        pass
        await client.disconnect()
        try:
            os.remove(f"./sessions/{tdataname}.session")
            os.remove(f"./sessions/{tdataname}.session-journal")
        except Exception as e:
            pass
        return
    except Exception as e:
        pass
        if str(e) == "The phone number is invalid (caused by SendCodeRequest)":
            os.rename("tdata", "Banned tdata")
        await client.disconnect()
        try:
            os.remove(f"./sessions/{tdataname}.session")
            os.remove(f"./sessions/{tdataname}.session-journal")
        except Exception as e:
            pass
        return
    await client.send_message(dialog, mess)


def create_send_message_thread(tdataname, dialog, mess, proxy):
    asyncio.run(send_message_with_timeout(tdataname, dialog, mess, proxy))


async def mainn(mess, tdataname, client, proxy):
    config = configparser.ConfigParser()

    config.read("config.txt")

    proxy_type = config.get("myvars", "proxy_type")


    try:
        await client.send_message("@SpamBot", f"/start")
        await client.disconnect()
    except: pass


def get_current_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    return f"Дата и время: {dt_string} | "


def pprint(mess):
    print(get_current_time() + str(mess))


def launcher():
    big_let_start = 0x00C0  # Capital "A" in cyrillic alphabet
    big_let_end = 0x00DF  # Capital "Я" in cyrillic alphabet
    small_let_end = 0x00FF  # small "я" in cyrillic alphabet
    remap_big_let = 0x0410  # Starting number for remapped cyrillic alphabet
    alph_len = big_let_end - big_let_start + 1  # adds the shift from big letters to small
    alph_shift = remap_big_let - big_let_start  # adds the shift from remapped to non-remapped

    with dpg.font_registry():
        with dpg.font("C:/Windows/Fonts/arial.ttf", 16) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            biglet = remap_big_let  # Starting number for remapped cyrillic alphabet
            for i1 in range(big_let_start, big_let_end + 1):  # Cycle through big letters in cyrillic alphabet
                dpg.add_char_remap(i1, biglet)  # Remap the big cyrillic letter
                dpg.add_char_remap(i1 + alph_len, biglet + alph_len)  # Remap the small cyrillic letter
                biglet += 1  # choose next letter

    dpg.bind_font(default_font)

    with dpg.window(label="TGSpamCore", width=1000, height=600) as win1:
        dpg.add_input_text(tag="mess", label="Message", width=400, default_value="Hello!")
        dpg.add_button(tag="start", label="Start", callback=startarc)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

dpg.create_context()
dpg.create_viewport(title='TGSpamCore', width=1000, height=600)

launcher()
