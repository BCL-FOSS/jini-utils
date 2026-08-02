from slack_sdk.web.async_client import AsyncWebClient
import os
import argparse
import asyncio

class SlackAlert():
    def __init__(self):
        pass

    def set_slack_connection_info(self, slack_bot_token: str, slack_channel_id: str):
        self.token = slack_bot_token
        self.channel_id = slack_channel_id
        self.client = AsyncWebClient(token=self.token)
        
    async def get_conversation(self):
        channels_data = {}
 
        convo_list = await self.client.conversations_list()
     
        for key, value in convo_list.data.items():
            if key == "channels":
                channels_data[value['name']] = value['id']

        return channels_data
    
    async def send_alert_message(self, message: str):
        response = await self.client.chat_postMessage(channel=self.channel_id, text=message)
        return response

    async def task_manager(self, task: str, params: dict):
        self.set_slack_connection_info(slack_bot_token=os.getenv('SLACK_TOKEN'))
        match task:
            case 'alert':
                await self.send_alert_message(**params)

if __name__ == "__main__":
    jira_opts = argparse.ArgumentParser(description="")
    jira_opts.add_argument(
        '-t', '--task', 
        type=str, 
        help="selects appropiate email mgr task",
        default=None
    )
    jira_opts.add_argument(
        '-p', '--params',
        type=dict,
        help="parameters for email mgr task",
        default=None
    )
    slack = SlackAlert()
    args = jira_opts.parse_args()
    asyncio.run(slack.task_manager(task=args.task, params=args.params))

    