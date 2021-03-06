#!/usr/bin/env python

import wx
# import wx
from lxml import html
import requests
import PIL.Image
import PIL.ImageTk
import tkinter
from io import BytesIO
import webbrowser
import csv
import json
import threading
import math
#
TRAY_TOOLTIP = 'System Tray Demo'
TRAY_ICON = 'icon.png'

api_key = '7C28D264D4A05EB3ED84423B00F0F392'
base_profile_URL = ('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
                    + '?key='+api_key+'&steamids=')
steamTax = 1.15
# baseURL string. DO NOT MODIFY
baseURL = 'http://steamcommunity.com/market/priceoverview/?currency=13&appid=730&market_hash_name='
items_sell = []  # market_store
items_buy = []   # market_buy
root = None
check_thread = None

# Settings file
settings_json = None


def main():
    print('Program Starting')
    Scan_For_Link_Errors('market_sell.txt')
    Scan_For_Link_Errors('market_buy.txt')
    Read_Settings()
    app = wx.App(False)
    grab_data_from_textfile()

    # if settings_json["notifications"] == 1:
    #     Check_Prices_Sell(settings_json["checktime"])

    SteamScraperApp(items_sell)
    app.MainLoop()


# arrays

#####################################################################

# Allows program to open up individual windows without creating a root item first.
def Check_For_Root_Ownership(root_param):
    global root
    if root_param == root and root != None:
        root = None
        print('root is freed by ' + str(root_param))


def Create_Menu_Item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item
# Function that will check prices every time_s seconds and display a notification when items are ready to sell


# def Check_Prices_Sell(time_s):
    # global check_thread
    # check_thread = threading.Timer(time_s, Check_Prices_Sell)
    # check_thread.start()

    # # possible_sell_itmes = []
    # for item in items_sell:
    #     fifteen_cent = str("%.2f" %
    #                        ((float(item.purchase_price) + 0.15) * steamTax))
    #     # Split the url using '/' as the delimiter
    #     hash_name = item.url.split('/')
    #     # Generate the json URL for the item/weapon. Something along the lines of
    #     # http://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=StatTrak%E2%84%A2%20P250%20%7C%20Steel%20Disruption%20%28Factory%20New%29
    #     request_url = baseURL + hash_name[-1]
    #     # Create json
    #     try:
    #         page = requests.get(request_url)
    #         # print("RequestURL:" + request_url)
    #         page.raise_for_status()
    #     except requests.HTTPError:
    #         print(
    #             ("CheckPrices_Sell -- Unable to make JSON request for item" + item.name))
    #         continue
    #     json_dict = page.json()
    #     try:
    #         if item.purchase_price != 0.0 and json_dict['lowest_price'] >= fifteen_cent:
    #             possible_sell_itmes.append(item.name)
    #     except KeyError:
    #         continue
    # if possible_sell_itmes:
    #     msg = wx.NotificationMessage()
    #     msg.SetTitle('Items to sell')
    #     msg.SetMessage(str(possible_sell_itmes))
    #     msg.Show()

# Makes sure that the links in file_name are valid
def Scan_For_Link_Errors(file_name):
    error_flag = False
    correct_lines = []
    print('Starting link error scan')
    infile = open(file_name, 'r')
    infile_readlines = infile.readlines()
    for row in infile_readlines:
        if 'http://steamcommunity.com/market' in row:
            correct_lines.append(row)
        else:
            error_flag = True
    infile.close()

    open(file_name, 'w').close()

    outfile = open(file_name, 'w')
    for item in correct_lines:
        outfile.write(item)
    outfile.close()

    print('Scan complete')
    if error_flag == True:
        print('Errors found and fixed')
# Load settings to prevent opening settings.txt over and over again


def Read_Settings():
    global settings_json
    with open('settings.txt') as settings:
        settings_json = json.load(settings)
        settings.close()


def Write_Settings():
    global settings_json
    with open('settings.txt', 'w') as settings:
        json.dump(settings_json, settings)


class SettingsWindow:
    def __init__(self):
        global root
        if (root == None):
            root = tkinter.Tk()
            self.root = root
            print('root is taken by' + str(self))
        else:
            self.root = tkinter.Toplevel()
        self.root.title('Settings')
        # # Notifications
        # self.notification_arg = tkinter.IntVar()
        # self.notification_arg.set(settings_json['notifications'])
        # self.notification_entry = tkinter.Entry(
        #     self.root, textvariable=self.notification_arg).grid(row=1, column=3)
        # self.notification_label = tkinter.Label(
        #     self.root, text='Notification').grid(row=1, column=2)
        # Results Per Page
        self.resultsPerPage_arg = tkinter.IntVar()
        self.resultsPerPage_arg.set(settings_json['maxresultsperpage'])
        self.resultsPerPage_entry = tkinter.Entry(
            self.root, textvariable=self.resultsPerPage_arg).grid(row=2, column=3)
        self.resultsPerPage_label = tkinter.Label(
            self.root, text='Results Per Page').grid(row=2, column=2)
        # # Interval Time
        # self.checkTime_arg = tkinter.IntVar()
        # self.checkTime_arg.set(settings_json['checktime'])
        # self.checkTime_entry = tkinter.Entry(
        #     self.root, textvariable=self.checkTime_arg).grid(row=3, column=3)
        # self.checkTime_label = tkinter.Label(
        #     self.root, text='Notification Intervale (s)').grid(row=3, column=2)

        # Save Button
        self.save_button = tkinter.Button(
            self.root, text="Save", command=self.SaveSettings).grid(row=4, column=4)
        #
        self.root.protocol('WM_DELETE_WINDOW', self.root_owner_caller)
        self.root.mainloop()

    def root_owner_caller(self):
        Check_For_Root_Ownership(self.root)
        self.root.destroy()

    def SaveSettings(self):
        global settings_json
        # settings_json['notifications'] = self.notification_arg.get()
        settings_json['maxresultsperpage'] = self.resultsPerPage_arg.get()
        # settings_json['checktime'] = self.checkTime_arg.get()
        Write_Settings()
        print('Settings Saved')


class ProfileSearch:
    def __init__(self):
        global root
        if (root == None):
            root = tkinter.Tk()
            self.root = root
            print('root is taken by' + str(self))
        else:
            self.root = tkinter.Toplevel()
        self.root.title('Profile Viewer')
        # self.search_param = Tkinter.StringVar()
        self.profile_arg = tkinter.IntVar()
        self.profile_button = tkinter.Button(
            self.root, text="Enter 64bit Steam ID", command=self.GotoProfile).grid(row=0, column=0)
        self.profile_entry = tkinter.Entry(
            self.root, textvariable=self.profile_arg).grid(row=0, column=2)
        self.root.protocol('WM_DELETE_WINDOW', self.root_owner_caller)
        self.root.mainloop()

    def GotoProfile(self):
        profile_id = str(self.profile_arg.get())
        if(len(profile_id) != 17):
            top = tkinter.Toplevel()
            top.title("Error")

            msg = tkinter.Message(top, text="Invalid Profile ID")
            msg.pack()

            button = tkinter.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            return
        profile_URL = base_profile_URL + profile_id
        # print(self.profile_URL)
        try:
            page = requests.get(profile_URL)
            page.raise_for_status()
            # print(self.page)
            y = ProfileDisplay(page)
        except requests.HTTPError:
            print('Profile URL Not Found')

    def root_owner_caller(self):
        Check_For_Root_Ownership(self.root)
        self.root.destroy()


class ProfileDisplay:
    def __init__(self, page):
        self.root = tkinter.Toplevel()
        self.page = page
        self.page_dict = self.page.json()
        # Check to see if player profile exists based on the 64 bit ID number
        if len(self.page_dict['response']['players']) == 0:
            top = tkinter.Toplevel()
            top.title("Error")

            msg = tkinter.Message(top, text="Player not found")
            msg.pack()

            button = tkinter.Button(top, text="Dismiss", command=top.destroy)
            button.pack()
            self.root.destroy()
            return
        # at this point the player profile DOES exist.
        self.page_dict_list = self.page_dict['response']['players'][0]
        if self.page_dict_list['personastate'] == 1:
            self.online_status = 'Online'
        else:
            self.online_status = 'Offline'
        # Display profile image ----------------------------------------------
        self.r = requests.get(self.page_dict_list['avatarfull'])
        self.img = PIL.Image.open(BytesIO(self.r.content))
        self.img = self.img.resize((150, 150), PIL.Image.ANTIALIAS)
        self.photo = PIL.ImageTk.PhotoImage(self.img)
        self.img_label = tkinter.Label(self.root, image=self.photo)
        self.img_label.pack()
        self.text = (
            'Name: ' + self.page_dict_list['personaname'] + '\n' +
            'Profile URL: ' + self.page_dict_list['profileurl'] + '\n' +
            'Online Status: ' + self.online_status
        )
        self.text_label = tkinter.Label(self.root, text=self.text).pack()
        self.root.mainloop()


class Weapon:
    def __init__(self, link_p, *args):
        self.url = link_p
        if(args[0] != None):
            self.name = args[0]
        else:
            self.name = 'No name provided'
        if(args[1] != None):
            self.purchase_price = args[1]
        else:
            self.purchase_price = '0'


class AddItem:
    def __init__(self):
        global root
        if (root == None):
            root = tkinter.Tk()
            self.root = root
            print('root is taken by' + str(self))
        else:
            self.root = tkinter.Toplevel()

        self.root.title('Add Item to List')
        # Need 3 StringVar/IntVar
        self.link_arg = tkinter.StringVar()
        self.name_arg = tkinter.StringVar()
        self.price_arg = tkinter.DoubleVar()
        # Need 3 Entry Fields
        self.link_entry = tkinter.Entry(
            self.root, textvariable=self.link_arg).grid(row=2, column=3)
        self.name_entry = tkinter.Entry(
            self.root, textvariable=self.name_arg).grid(row=1, column=3)
        self.price_entry = tkinter.Entry(
            self.root, textvariable=self.price_arg).grid(row=3, column=3)
        # Need 3 Labels for Text for Entry
        self.name_label = tkinter.Label(
            self.root, text="Name: ").grid(row=1, column=2)
        self.link_label = tkinter.Label(
            self.root, text="Link: ").grid(row=2, column=2)
        self.price_label = tkinter.Label(
            self.root, text="Price: ").grid(row=3, column=2)

        # Button to add entries to market_store.txt
        self.add_sell_button = tkinter.Button(
            self.root, text="Add to Sell List", command=self.AddToSellList).grid(row=4, column=4)
        self.add_buy_button = tkinter.Button(
            self.root, text="Add to Buy List", command=self.AddToBuyList).grid(row=4, column=3)
        self.root.protocol('WM_DELETE_WINDOW', self.root_owner_caller)
        self.root.mainloop()

    def CreateErrorBox(self, errorMsg):
        print(("Error - " + errorMsg))
        error_popup = tkinter.Toplevel()
        error_popup.title('Error')
        error__label = tkinter.Label(error_popup, text=errorMsg).pack()
        error_popup.after(3000, error_popup.destroy)
        error_popup.mainloop()

    def AddToSellList(self):
        temp1 = self.link_arg.get()
        if('http://steamcommunity.com/market' not in temp1):
            self.CreateErrorBox('Not a Steam market link. Please try again.')
            return
        # test if link entered is a valid connection
        try:
            r = requests.get(temp1)
            r.raise_for_status()        # raise signal if not a valid link
        except requests.HTTPError:
            self.CreateErrorBox(
                'Cannot Access Link. Please  make sure Link is valid or if Steam is down')

        temp2 = self.name_arg.get()
        temp3 = str(self.price_arg.get())
        # Check for duplicate links
        with open('market_sell.txt', 'r') as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            line_counter = 0
            for row in read_csv:
                if row[0] == temp1:
                    print(('Duplicate found at line ' + str(line_counter) + '.\n'))
                    duplicate_popup = tkinter.Toplevel()
                    duplicate_label = tkinter.Label(
                        duplicate_popup, text="Duplicate found at line " + str(line_counter + 1))
                    duplicate_label.pack()
                    duplicate_popup.title("Error - Duplicate Link Found")
                    duplicate_popup.mainloop()
                    return
                line_counter += 1
        # Did not find any duplicate links
        with open('market_sell.txt', 'a') as f:
            f.write(temp1 + ',' + temp2 + ',' + temp3 + '\n')
        self.root.destroy()

    def AddToBuyList(self):
        temp1 = self.link_arg.get()
        if ('http://steamcommunity.com/market' not in temp1):
            self.CreateErrorBox('Not a Steam market link. Please try again.')
            return
        # test if link entered is a valid connection
        try:
            r = requests.get(temp1)
            r.raise_for_status()        # raise signal if not a valid link
        except requests.HTTPError:
            self.CreateErrorBox(
                'Cannot Access Link. Please  make sure Link is valid or if Steam is down')

        temp2 = self.name_arg.get()
        temp3 = str(self.price_arg.get())

        # Check for duplicate links
        with open('market_buy.txt', 'r') as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            line_counter = 0
            for row in read_csv:
                if row[0] == temp1:
                    print(('Duplicate found at line ' + str(line_counter) + '.\n'))
                    duplicate_popup = tkinter.Toplevel()
                    duplicate_label = tkinter.Label(
                        duplicate_popup, text="Duplicate found at line " + str(line_counter + 1))
                    duplicate_label.pack()
                    duplicate_popup.title("Error - Duplicate Link Found")
                    duplicate_popup.mainloop()
                    return
                line_counter += 1
        # Did not find any duplicate links
        with open('market_sell.txt', 'a') as f:
            f.write(temp1 + ',' + temp2 + ',' + temp3 + '\n')
        self.root.destroy()

    def root_owner_caller(self):
        Check_For_Root_Ownership(self.root)
        self.root.destroy()


class Calculator:
    def __init__(self):
        global root
        if (root == None):
            root = tkinter.Tk()
            self.root = root
            print('root is taken by' + str(self))
        else:
            self.root = tkinter.Toplevel()
        self.root.title("Calculator")

        # Display entry box-----------------
        self.price_arg = tkinter.DoubleVar()
        self.price_0result = tkinter.DoubleVar()
        self.price_15result = tkinter.DoubleVar()

        self.price_input_label = tkinter.Label(self.root, text='Enter price')
        self.price_input_label.pack()
        self.price_input_entry = tkinter.Entry(
            self.root, textvariable=self.price_arg)
        self.price_input_entry.pack()

        self.price_button = tkinter.Button(
            self.root, text="Calculate!", command=self.LaunchCalculation).pack()

        self.price_output0_label = tkinter.Label(
            self.root, text='Break Even').pack()
        self.price_output0_entry = tkinter.Entry(
            self.root, textvariable=self.price_0result, state='readonly').pack()

        self.price_output15_label = tkinter.Label(
            self.root, text='15c Profit').pack()
        self.price_output15_entry = tkinter.Entry(
            self.root, textvariable=self.price_15result, state='readonly').pack()

        self.root.protocol('WM_DELETE_WINDOW', self.root_owner_caller)
        self.root.mainloop()

    def LaunchCalculation(self):
        value = self.price_arg.get()
        break_even_value = value * steamTax
        fifteen_cent_profit = (value + 0.15) * steamTax
        self.price_0result.set(break_even_value)
        self.price_15result.set(fifteen_cent_profit)

    def root_owner_caller(self):
        Check_For_Root_Ownership(self.root)
        self.root.destroy()

    # Takes in a list of Weapon objects.


class SteamScraperApp:
    def __init__(self, list_of_items_p):
        global settings_json
        global root

        if (root == None):
            root = tkinter.Tk()
            self.root = root
            print('root is taken by' + str(self))
        else:
            self.root = tkinter.Toplevel()
        self.list_of_items = list_of_items_p
        # Arrays used for reference
        self.photo_arr = []
        self.img_label_arr = []
        self.price_label_arr = []

        # # Reset
        self.row_counter = 0
        self.column_counter = 0

        # New display mechanics
        self.results_per_page = settings_json['maxresultsperpage']
        print('resultsperpage = ' + str(self.results_per_page))
        self.current_page__img_arr = []
        self.current_page__lbl_arr = []
        self.current_page_number = 0

        print('Current_page_number = ' + str(self.current_page_number))
        self.max_page_number = 0

        # Frames
        self.buttons_frame = tkinter.Frame(
            self.root, height=2, bd=1, relief='sunken')
        self.buttons_frame.pack()
        self.items_frame = tkinter.Frame(
            self.root, height=2, bd=1, relief='sunken')
        self.items_frame.pack()
        # Re-list items
        self.first_time_open()

    def refresh(self):
        global items_sell
        print('refresh called')
        print('beginning destruction of widgets')
        # Destroy the widgets
        print(('Deleting' + str(len(self.img_label_arr)) + 'items from img_label_arr'))

        for item in self.img_label_arr:
            print(('Destorying item' + str(item) + 'from img_label_arr'))
            item.destroy()
        print('Done destorying items in img_label_arr')
        for item in self.price_label_arr:
            print(('Destroying item' + str(item) + 'from price_label_arr'))
            item.destroy()
        print('Done destorying items in price_label_arr')

        # Arrays
        self.img_label_arr = []
        self.price_label_arr = []
        # Getting data

        print('Emptying items_sell')
        for item in items_sell:
            del item
        items_sell = []
        grab_data_from_textfile()
        self.list_of_items = items_sell
        self.get_data()
        # Display
        self.current_page_number = 0
        self.display_page()

    def open_settings(self):
        SettingsWindow()

    # @staticmethod
    def open_profile(self):
        ProfileSearch()

    # @staticmethod
    def open_item_adder(self):
        AddItem()

    # @staticmethod
    def open_calculator(self):
        Calculator()

    def open_steam_status(self):
        webbrowser.open('https://steamstat.us/', new=2)

    def root_owner_caller(self):
        Check_For_Root_Ownership(self.root)
        self.root.destroy()

    def ScanForLinkErrorCaller(self):
        Scan_For_Link_Errors('market_sell.txt')
        Scan_For_Link_Errors('market_buy.txt')

    def display_page(self):
        print('display_page called')
        arr_s = self.current_page_number * self.results_per_page
        max_index = self.current_page_number * \
            self.results_per_page + (self.results_per_page-1)
        while arr_s <= max_index:
            try:
                self.img_label_arr[arr_s].grid(
                    row=self.row_counter, column=self.column_counter)
                self.price_label_arr[arr_s].grid(
                    row=self.row_counter, column=self.column_counter + 1)
            except IndexError as xxx_todo_changeme:
                tkinter.TclError = xxx_todo_changeme
                break
            arr_s += 1
            self.row_counter += 1
        self.row_counter = 0

    def forget_page(self):
        print('forget_page called')
        arr_s = self.current_page_number * self.results_per_page
        max_index = self.current_page_number * \
            self.results_per_page + (self.results_per_page - 1)
        while arr_s <= max_index:
            try:
                self.img_label_arr[arr_s].grid_forget()
                self.price_label_arr[arr_s].grid_forget()
            except IndexError:
                break
            arr_s += 1
        self.row_counter = 0

    def next_page(self):
        print('next_page called')
        # Forget the grid in the current page
        self.forget_page()
        # Move over to the new page
        if self.current_page_number < self.max_page_number:
            self.current_page_number += 1     # Increment
        print('Current_page_number = ' + str(self.current_page_number))
        # Re-list new pages
        self.display_page()

        # Enable and Disable Buttons
        if self.current_page_number == self.max_page_number:
            self.next_page_button['state'] = 'disabled'
            self.prev_page_button['state'] = 'normal'
        else:
            self.next_page_button['state'] = 'normal'
            self.prev_page_button['state'] = 'normal'

    def prev_page(self):
        print('prev_page called')
        # Forget the grid in the current page
        self.forget_page()
        # Move over to the new page
        if self.current_page_number > 0:
            self.current_page_number -= 1     # Decrement
        print('Current_page_number = ' + str(self.current_page_number))
        # Re-list new pages
        self.display_page()
        # Enable and Disable Buttons
        if self.current_page_number == 0:
            self.prev_page_button['state'] = 'disabled'
            self.next_page_button['state'] = 'normal'
        else:
            self.prev_page_button['state'] = 'normal'
            self.next_page_button['state'] = 'normal'

    def first_time_open(self):
        print('first_time_open called')
        self.get_data()
        self.DrawMainWindow()
    # Fetches data, creates Tkinter Labels, then stores it into img_label_arr and price_label_arr

    def get_data(self):
        print('get_data')
        for item in self.list_of_items:
            # Print the text Information ------------------------------------------------------------
            # Prices for profit
            break_even_price = str(
                "%.2f" % (float(item.purchase_price) * steamTax))
            fifteen_cent = str(
                "%.2f" % ((float(item.purchase_price) + 0.15) * steamTax))
            twenty_cent = str("%.2f" %
                              ((float(item.purchase_price) + 0.20) * steamTax))
            twenty_five_cent = str(
                "%.2f" % ((float(item.purchase_price) + 0.25) * steamTax))
            thrity_cent = str("%.2f" %
                              ((float(item.purchase_price) + 0.30) * steamTax))
            # Split the url using '/' as the delimiter
            hash_name = item.url.split('/')

            # Generate the json URL for the item/weapon. Something along the lines of
            # http://steamcommunity.com/market/priceoverview/?currency=3&appid=730&market_hash_name=StatTrak%E2%84%A2%20P250%20%7C%20Steel%20Disruption%20%28Factory%20New%29
            request_url = baseURL + hash_name[-1]
            # Create json
            try:
                print('Requesting JSON from: ' + request_url)
                page = requests.get(request_url)
                # print("RequestURL:" + request_url)
                page.raise_for_status()
            except requests.HTTPError:
                print(("Unable to make JSON request for item" + item.name))
                continue

            json_dict = page.json()
            try:
                text_to_display = (
                    "Name: " + item.name + '\n' +
                    "Purchase Price: " + item.purchase_price + '\n' +
                    "Median Price: " + json_dict['median_price'] + '\n' +
                    "Lowest Price: " + json_dict['lowest_price'] + '\n' +
                    "Break Even: " + break_even_price + '\n' +
                    "15c Profit: " + fifteen_cent + '\n' +
                    "20c Profit: " + twenty_cent + '\n' +
                    "25c Profit: " + twenty_five_cent + '\n' +
                    "30c Profit: " + thrity_cent + '\n' +
                    "--------------------------------------------------\n"
                )
            except KeyError:
                text_to_display = 'Key error. Please refresh in a few minutes.'
                continue

            price_label = tkinter.Label(self.items_frame, text=text_to_display)
            # Display the image -------------------------------------------------------------------------
            # Get img_url
            page = requests.get(item.url)
            tree = html.fromstring(page.content)

            # Grab image URL using Xpath
            img_url = tree.xpath(
                '//*[@id="mainContents"]/div[2]/div/div[1]/img/@src')
            try:
                self.temp = img_url[0]
                # Convert and Resize image
                r = requests.get(img_url[0])
                img = PIL.Image.open(BytesIO(r.content))
                img = img.resize((150, 150), PIL.Image.ANTIALIAS)
                photo = PIL.ImageTk.PhotoImage(img)
                # Reference the image and photo
                img_label = tkinter.Label(self.items_frame, image=photo)
                # append to arrays. Append all 3 only when they are all valid
                self.photo_arr.append(photo)
                self.img_label_arr.append(img_label)
                self.price_label_arr.append(price_label)
            except IndexError:
                print("img_url[0] == None:")
                print((item.url))
                continue

        # Debug info
        print('img_label_arr length = ' + str(float(len(self.img_label_arr))))
        self.max_page_number = math.ceil(
            float(len(self.img_label_arr))/self.results_per_page) - 1.0
        print('maxPagenumber = ' + str(self.max_page_number))

    def DrawMainWindow(self):
        print('DrawWindow called')

        refresh_button = tkinter.Button(
            self.buttons_frame, text="Refresh", command=self.refresh)
        refresh_button.grid(row=0, column=0, stick='nw')
        error_checking_button = tkinter.Button(
            self.buttons_frame, text='Error Check', command=self.ScanForLinkErrorCaller)
        error_checking_button.grid(row=0, column=1, stick='nw')
        # Other features of application
        profile_button = tkinter.Button(
            self.buttons_frame, text="Profile", command=self.open_profile)
        profile_button.grid(row=0, column=2, stick='nw')
        add__to_button = tkinter.Button(
            self.buttons_frame, text="Add Item to List", command=self.open_item_adder)
        add__to_button.grid(row=0, column=3, stick='nw')
        calc_button = tkinter.Button(
            self.buttons_frame, text="Calculator", command=self.open_calculator)
        calc_button.grid(row=0, column=4, stick='nw')
        service_stat_button = tkinter.Button(
            self.buttons_frame, text="Steam Service Stat", command=self.open_steam_status)
        service_stat_button.grid(row=0, column=5, stick='nw')
        settings_button = tkinter.Button(
            self.buttons_frame, text="Settings", command=self.open_settings)
        settings_button.grid(row=0, column=6, stick='nw')
        #
        self.next_page_button = tkinter.Button(
            self.buttons_frame, text="Next Page", state='normal', command=self.next_page)
        self.next_page_button.grid(row=1, column=1, stick='nw')
        self.prev_page_button = tkinter.Button(
            self.buttons_frame, text="Prev Page", state='disabled', command=self.prev_page)
        self.prev_page_button.grid(row=1, column=0, stick='nw')
        # Draw window -------------------------
        self.display_page()
        print('Done fetching data')
        # root checker
        print('listItems() img_label_array length = ' +
              str(len(self.img_label_arr)))
        self.root.protocol('WM_DELETE_WINDOW', self.root_owner_caller)
        self.root.mainloop()
    # modify self.list_of_items using items_sell

####################################################################
# class TaskBarIcon(wx.TaskBarIcon):
    # def __init__(self, frame):
    #     self.frame = frame
    #     super(TaskBarIcon, self).__init__()
    #     self.set_icon(TRAY_ICON)
    #     self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        Create_Menu_Item(menu, 'Open', self.OpenApp)
        Create_Menu_Item(menu, 'Calculator', self.OpenCalculator)
        Create_Menu_Item(menu, 'Add Item to List', self.OpenAddItem)
        Create_Menu_Item(menu, 'Profile Viewer', self.OpenProfileViewer)
        menu.AppendSeparator()
        Create_Menu_Item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        # Stop all threads here
        global check_thread
        check_thread.cancel()
        self.frame.Close()

    def OpenApp(self, event):
        SteamScraperApp(items_sell)

    def OpenCalculator(self, event):
        Calculator()

    def OpenAddItem(self, event):
        AddItem()

    def OpenProfileViewer(self, event):
        ProfileSearch()


# class App(wx.App):
#     def OnInit(self):
#         frame = wx.Frame(None)
#         self.SetTopWindow(frame)
#         TaskBarIcon(frame)
#         return True

def grab_data_from_textfile():
    print('Grab data called')
    # Grab items from text file
    with open('market_sell.txt') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            items_sell.append(Weapon(row[0], row[1], row[2]))

    with open('market_buy.txt') as csv_file:
        read_csv = csv.reader(csv_file, delimiter=',')
        for row in read_csv:
            items_buy.append(Weapon(row[0], row[1], row[2]))


######################################################################
if __name__ == '__main__':
    main()
