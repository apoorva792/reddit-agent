import praw
import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()
print("Token:", os.getenv('SLACK_BOT_TOKEN'))
print("Channel:", os.getenv('SLACK_CHANNEL'))

class RedditMonitor:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent="SimpleRedditMonitor"
        )
    
        self.slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
        self.slack_channel = os.getenv('SLACK_CHANNEL')
        
        try:
            response = self.slack_client.auth_test()
            print("Slack Connection Test:", response)
        except SlackApiError as e:
            print("Slack Connection Error:", e.response['error'])
        
        self.subreddits = ['salesforce', 'crm','salesforcedeveloper','sales','techsales']
        self.keywords = ['pipeline','report','analysis','flow','templates','agentforce','automate']
        self.check_interval = 300

    def send_to_slack(self, post):
        try:
            message = (
                f"*New Reddit Post*\n"
                f"*Subreddit:* r/{post.subreddit}\n"
                f"*Title:* {post.title}\n"
                f"*Link:* {post.url}\n"
                f"*Score:* {post.score} | *Comments:* {post.num_comments}"
            )
            
            print(f"send message to channel: {self.slack_channel}")
            
            response = self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=message
            )
            print("Slack API Response:", response)
            
        except SlackApiError as e:
            print(f"Error sending to Slack: {e.response['error']}")
            print(f"Full error : {e.response}")

    def monitor(self):
        """Main monitoring loop"""
        print(f"Monitoring subreddits: {', '.join(self.subreddits)}")
        print(f"Looking for keywords: {', '.join(self.keywords)}")
        
        while True:
            try:
                for subreddit in self.subreddits:
                    try:
                        for post in self.reddit.subreddit(subreddit).new(limit=10):
                            if any(keyword.lower() in post.title.lower() or 
                                  keyword.lower() in post.selftext.lower() 
                                  for keyword in self.keywords):
                                print(f"Found matching post: {post.title}")
                                self.send_to_slack(post)
                    except Exception as e:
                        print(f"Error r/{subreddit}: {e}")
                
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
               
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = RedditMonitor()
    monitor.monitor()