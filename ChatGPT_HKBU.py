import configparser
import requests
import openai
import os
import logging
import psycopg2

class HKBU_ChatGPT():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.db_conct = self._connect_database()

        keys = ['TELEGRAM', 'CHATGPT', 'OpenAI', 'POSTGRESQL']
        values = ['ACCESS_TOKEN', 'ACCESS_ID', 'BASICURL', 'MODELNAME', 'APIVERSION', 'ACCESS_TOKEN', 'OPENAI_API_KEY']

        current_key = []
        current_value = []

        for key, value in self.config:
            current_key.append(key)
            current_value.append(self.config(key))

        missing1 = [item for item in keys if item not in current_key]
        missing2 = [item for item in values if item not in current_value]

        if (missing1):
            exit()
        elif (missing2):
            exit()


    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (self.config['CHATGPT']['BASICURL']) + "/deployments/" + (self.config['CHATGPT']['MODELNAME']) + "/chat/completions/?api-version=" + (self.config['CHATGPT']['APIVERSION'])
        headers = {
            'Content-Type': 'application/json',
            'api-key': (self.config['CHATGPT']['ACCESS_TOKEN'])
        }
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f'Error: {response.status_code}, {response.text}'

    def _connect_database(self):
        conct = psycopg2.connect(
            host=self.config['POSTGRESQL']['HOST'],
            port=self.config['POSTGRESQL']['PORT'],
            database=self.config['POSTGRESQL']['DATABASE'],
            user=self.config['POSTGRESQL']['USER'],
            password=self.config['POSTGRESQL']['PASSWORD']
        )
        return conct

    def _add_log(self, log):
        connection = self._connect_database()
        if (connection):
            try:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO chatlog (log) VALUES (%s)"
                    cursor.execute(sql, (log))
                    connection.commit()
                    return True
            except Exception.Error as e:
                return False


    def send_to_telegram(self, message):
        access_token = self.config['TELEGRAM']['ACCESS_TOKEN']
        access_id = self.config['TELEGRAM']['CHAT_ID']
        url = f"https://api.telegram.org/bot{access_token}/sendMessage"
        config = {
            'chat_id': access_id,
            'access_token': access_token,
            'text': message
        }
        response = requests.post(url, json=config)
        return True

if __name__ == '__main__':
    test = HKBU_ChatGPT()
    while True:
        print("Hello, I'm HKBU_ChatGPT_BOT! My name is narak.")
        print("")
        print("My main mission is to assist you in your work, but of course, if you want to chat with me online, I have no objection.")
        question = input("Do you need anything help? :\t")
        test.add_log(question)
        response = test.submit(question)
        test.add_log(response)
        test.send_to_telegram(response)
        print("ChatGPT speak: " + response)