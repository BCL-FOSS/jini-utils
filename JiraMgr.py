import json
import httpx
import logging
import argparse
import asyncio

class JiraSM():
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('passlib').setLevel(logging.ERROR)
        logger = logging.getLogger(__name__)
        self.logger = logger
        
    async def make_http_request(self, headers: dict, url: str, data: dict, timeout: int = 10, user:  str = None, passwd: str = None):
            auth = httpx.BasicAuth(username=user, password=passwd)
            async with httpx.AsyncClient() as client:                
                exec_resp = await client.post(url, json=data, headers=headers, timeout=timeout, auth=auth)
                if exec_resp.status_code != 200:
                    self.logger.error(f"HTTP request failed with status code {exec_resp.status_code}: {exec_resp.text}")
                    return exec_resp.status_code, None
                exec_resp_data = exec_resp.json()
                return exec_resp.status_code, exec_resp_data

    def set_jira_connection_info(self, cloud_id: str, auth_email: str, auth_token: str):
        self.cloud_id = cloud_id
        self.auth_token = auth_token
        self.auth_email = auth_email

    async def send_alert(self, message: str, desc: str, note: str, source: str, entity: str, alias: str, priority: str, actions: list, extra_properties: dict):
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/alerts"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload= json.dumps({
                            "message": message,
                            "responders": [
                                {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "type": "team"},
                                {"id": "bb4d9938-c3c2-455d-aaab-727aa701c0d8", "type": "user"},
                                {"id": "aee8a0de-c80f-4515-a232-501c0bc9d715", "type": "escalation"},
                                {"id": "80564037-1984-4f38-b98e-8a1f662df552", "type": "schedule"}
                            ],
                            "visibleTo": [
                                {"id": "4513b7ea-3b91-438f-b7e4-e3e54af9147c", "type": "team"},
                                {"id": "bb4d9938-c3c2-455d-aaab-727aa701c0d8", "type": "user"}
                            ],
                            "note": note,
                            "alias": alias,
                            "entity": entity,
                            "source": source,
                            "tags": ["OverwriteQuietHours", "Critical"],
                            "actions": actions,
                            "description": desc,
                            "priority": priority,
                            "extraProperties": extra_properties
                        })

        result_code, result = await self.make_http_request(url=url, headers=headers, data=payload, user= self.auth_email, passwd=self.auth_token)
        self.logger.info(f'status code: {result_code}\nresult json: {json.dumps(result)}')
        return
    
    async def get_teams(self):
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/teams"

        auth = (self.auth_email, self.auth_token)

        headers = {
            "Accept": "application/json"
        }

        result = await self.make_http_request(cmd='g', url=url, auth=auth, headers=headers)

        return result
    
    async def get_schedules(self):
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/schedules"

        auth = (self.auth_email, self.auth_token)

        headers = {
            "Accept": "application/json"
        }

        result = await self.make_http_request(cmd='g', url=url, auth=auth, headers=headers)

        return result
    
    async def get_escalations(self, team_id: str):
        url = f"https://api.atlassian.com/jsm/ops/api/{self.cloud_id}/v1/teams/{team_id}/escalations"

        auth = (self.auth_email, self.auth_token)

        headers = {
            "Accept": "application/json"
        }

        result = await self.make_http_request(cmd='g', url=url, auth=auth, headers=headers)

        return result

    async def task_manager(self, task: str, params: dict, id: str, email: str, token: str):
        self.set_jira_connection_info(cloud_id=id, auth_email=email, auth_token=token)
        match task:
            case 'alert':
                await self.send_alert(**params)

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
    jira_opts.add_argument(
        '-id', '--cloud_id',
        type=str,
        help="jira cloud id",
        default=None
    )
    jira_opts.add_argument(
        '-e', '--email',
        type=str,
        help="jira email attached to token",
        default=None
    )
    jira_opts.add_argument(
        '-k', '--auth_token',
        type=str,
        help="jira auth token",
        default=None
    )
    jira = JiraSM()
    args = jira_opts.parse_args()
    asyncio.run(jira.task_manager(task=args.task, params=args.params, id=args.cloud_id, email=args.email, token=args.auth_token))
    
