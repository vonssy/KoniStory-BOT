import requests
import json
import os
from urllib.parse import parse_qs, unquote
from colorama import *
from datetime import datetime
import time
import pytz

wib = pytz.timezone('Asia/Jakarta')

class KoniStory:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Host': 'sp-odyssey-api.playnation.app',
            'Origin': 'https://story-protocol-odyssey-tele.playnation.app',
            'Pragma': 'no-cache',
            'Referer': 'https://story-protocol-odyssey-tele.playnation.app/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Koni Story - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def extract_user_data(self, query: str) -> str:
        parsed_query = parse_qs(query)
        user_data = parsed_query.get('user', [None])[0]

        if user_data:
            user_json = json.loads(unquote(user_data))
            return str(user_json.get('first_name', 'Unknown'))
        return 'Unknown'

    def load_tokens(self):
        try:
            if not os.path.exists('tokens.json'):
                return {"accounts": []}

            with open('tokens.json', 'r') as file:
                data = json.load(file)
                if "accounts" not in data:
                    return {"accounts": []}
                return data
        except json.JSONDecodeError:
            return {"accounts": []}

    def save_tokens(self, tokens):
        with open('tokens.json', 'w') as file:
            json.dump(tokens, file, indent=4)

    def generate_tokens(self, accounts_data: list):
        tokens_data = self.load_tokens()
        accounts = tokens_data["accounts"]

        for account in accounts_data:
            query = account.get("query")
            address = account.get("address")

            if not query or not address:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Skipped{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reason{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Incomplete Data in accounts.json {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                continue

            account_name = self.extract_user_data(query)
            existing_account = next((acc for acc in accounts if acc.get("first_name") == account_name), None)

            if not existing_account:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Token Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Generating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                time.sleep(1)

                account_data = self.account_login(query, address)
                token = account_data.get('token') if account_data else None

                if token:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                     "
                    )
                    accounts.append({"first_name": account_name, "token": token})
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Query ID Is May Expired {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )

                time.sleep(1)
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)

        self.save_tokens({"accounts": accounts})

    def renew_token(self, account_name):
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])
        
        account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        
        if account and "token" in account:
            token = account["token"]
            if not self.task_history(token):
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Token Isn't Valid{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Regenerating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                time.sleep(1)
                
                accounts = [acc for acc in accounts if acc["first_name"] != account_name]
                
                accounts_data = self.load_accounts()
                account_data = next((acc for acc in accounts_data if self.extract_user_data(acc.get("query")) == account_name), None)
                if account_data:
                    query = account_data.get("query")
                    address = account_data.get("address")
                    
                    if query and address:
                        new_token = self.account_login(query, address).get('token')
                        if new_token:
                            accounts.append({"first_name": account_name, "token": new_token})
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                      "
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Reason{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} Query ID Is May Expired {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                    else:
                        print(
                            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}Skipped{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reason{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} Incomplete Data in accounts.json {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                            end="\r", flush=True
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Query Is None. Skipping {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                       "
                    )
                time.sleep(1)
        
        self.save_tokens({"accounts": accounts})

    def load_accounts(self):
        with open('accounts.json', 'r') as file:
            accounts_data = json.load(file)
            return accounts_data.get("accounts", [])
    
    def account_login(self, query: str, address: str):
        url = 'https://sp-odyssey-api.playnation.app/api/account/login'
        data = json.dumps({'address':address, 'initData': query, 'referralCode':'TXpN3k91O'})
        self.headers.update({
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers, data=data)
        result = response.json()
        if response.status_code == 200:
            return result
        else:
            return None
        
    def task_history(self, token: str):
        url = 'https://sp-odyssey-api.playnation.app/api/task/history'
        self.headers.update({
            'authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.get(url, headers=self.headers)
        result = response.json()
        if response.status_code == 200:
            return result
        else:
            return None
        
    def submit_task(self, token: str, task_id: int):
        url = 'https://sp-odyssey-api.playnation.app/api/task/submit'
        data = json.dumps({'extrinsicHash':'', 'network':'', 'taskId':task_id})
        self.headers.update({
            'authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        response = self.session.post(url, headers=self.headers, data=data)
        result = response.json()
        if response.status_code == 200:
            return result
        else:
            return None
        
    def process_query(self, query: str):
        account_name = self.extract_user_data(query)
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])

        exist_account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        if not exist_account:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Token Not Found in tokens.json{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return
        
        if exist_account and "token" in exist_account:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            time.sleep(1)

            token = exist_account["token"]

            tasks = self.task_history(token)
            if not tasks:
                self.renew_token(account_name)
                tokens_data = self.load_tokens()
                new_account = next((acc for acc in tokens_data["accounts"] if acc["first_name"] == account_name), None)
                
                if new_account and "token" in new_account:
                    new_token = new_account["token"] 
                    tasks = self.task_history(new_token)

            if tasks:
                is_complteted = False
                for task in tasks:
                    task_id = task['id']
                    completed = task['status']

                    if task and completed is None:
                        if task['endTime'] is not None:
                            continue

                        submit = self.submit_task(new_token if 'new_token' in locals() else token, task_id)
                        if submit and submit['success']:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['pointReward']} SP {Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                f"{Fore.WHITE+Style.BRIGHT} {task['name']} {Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT}Isn't Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA+Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                        time.sleep(1)

                    else:
                        is_complteted = True

                if is_complteted:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}[ Task{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Data Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}]{Style.RESET_ALL}"
                )
            
        
    def main(self):
        self.clear_terminal()
        try:
            accounts_data = self.load_accounts()
            self.generate_tokens(accounts_data)

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts_data)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)

                for account in accounts_data:
                    query = account.get("query")

                    if query:
                        self.process_query(query)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)
                        time.sleep(3)

                seconds = 1800
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Koni Story - BOT{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = KoniStory()
    bot.main()