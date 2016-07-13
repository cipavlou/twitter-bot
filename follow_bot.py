from twitter import Twitter, OAuth, TwitterHTTPError
import os
import sys
import time
import random
import datetime
from random import randint

# initialise twitter bot
# sync followers
# check ratios
# decide to follow or unfollow
# auto follow new followers
# find followers to follow
# follow followers
# exit
#a

class TwitterBot:
    def __init__(self):
        self.oauth_token = 0
        self.oauth_secret = 0
        self.consumer_key = 0
        self.consumer_secret = 0
        self.twitter_handle = self
        self.twitter_connection = Twitter(auth=OAuth(self.oauth_token, self.oauth_secret, self.consumer_key, self.consumer_secret))

    def sync_follows(self):
        followers_status = self.twitter_connection.followers.list(screen_name=self.twitter_handle)
        followers = set(followers_status["ids"])
        next_cursor = followers_status["next_cursor"]




        
        with open(self.BOT_CONFIG["FOLLOWERS_FILE"], "w") as out_file:
            for follower in followers:
                out_file.write("%s\n" % (follower))

        while next_cursor != 0:
            followers_status = self.TWITTER_CONNECTION.followers.ids(screen_name=self.BOT_CONFIG["TWITTER_HANDLE"],
                                                                     cursor=next_cursor)
            followers = set(followers_status["ids"])
            next_cursor = followers_status["next_cursor"]

            with open(self.BOT_CONFIG["FOLLOWERS_FILE"], "a") as out_file:
                for follower in followers:
                    out_file.write("%s\n" % (follower))

        # sync the user's follows (accounts the user is following)
        following_status = self.TWITTER_CONNECTION.friends.ids(screen_name=self.BOT_CONFIG["TWITTER_HANDLE"])
        following = set(following_status["ids"])
        next_cursor = following_status["next_cursor"]

        with open(self.BOT_CONFIG["FOLLOWS_FILE"], "w") as out_file:
            for follow in following:
                out_file.write("%s\n" % (follow))

        while next_cursor != 0:
            following_status = self.TWITTER_CONNECTION.friends.ids(screen_name=self.BOT_CONFIG["TWITTER_HANDLE"],
                                                                   cursor=next_cursor)
            following = set(following_status["ids"])
            next_cursor = following_status["next_cursor"]

            with open(self.BOT_CONFIG["FOLLOWS_FILE"], "a") as out_file:
                for follow in following:
                    out_file.write("%s\n" % (follow))

test = TwitterBot()
print(test.twitter_handle)

time.sleep(360)

class TwitteraBot:

    def auto_follow_followers(self,count=None):
        """
            Follows back everyone who's followed you.
        """

        following = self.get_follows_list()
        followers = self.get_followers_list()

        not_following_back = followers - following
        not_following_back = list(not_following_back)[:count]
        for user_id in not_following_back:
            try:
                self.wait_on_action()

                self.TWITTER_CONNECTION.friendships.create(user_id=user_id, follow=False)
            except TwitterHTTPError as api_error:
                # quit on rate limit errors
                if "unable to follow more people at this time" in str(api_error).lower():
                    print("You are unable to follow more people at this time. "
                          "Wait a while before running the bot again or gain "
                          "more followers.", file=sys.stderr)
                    return

                # don't print "already requested to follow" errors - they're frequent
                if "already requested to follow" not in str(api_error).lower():
                    print("Error: %s" % (str(api_error)), file=sys.stderr)

    def auto_follow_followers_of_user(self, user_twitter_handle, count=100):

        following = self.get_follows_list() # following.txt
        followers_of_user = set(self.TWITTER_CONNECTION.followers.ids(screen_name=user_twitter_handle)["ids"][:count]) # followers of target account
        do_not_follow = self.get_do_not_follow_list() # already-followed.txt

        for user_id in followers_of_user:
            try:
                if (user_id not in following and user_id not in do_not_follow):

                    self.wait_on_action()

                    self.TWITTER_CONNECTION.friendships.create(user_id=user_id, follow=False)
                    print("Followed %s" % user_id, file=sys.stdout)

            except TwitterHTTPError as api_error:
                # quit on rate limit errors
                if "unable to follow more people at this time" in str(api_error).lower():
                    print("You are unable to follow more people at this time. "
                          "Wait a while before running the bot again or gain "
                          "more followers.", file=sys.stderr)
                    return

                # don't print "already requested to follow" errors - they're
                # frequent
                if "already requested to follow" not in str(api_error).lower():
                    print("Error: %s" % (str(api_error)), file=sys.stderr)

    def auto_follow_followers_of_user_2(self, user_twitter_handle, count=5000):
        """
            Follows the followers of a specified user.
        """

        following = self.get_follows_list() # following.txt

        # users_to_follow IS A LIST WITH THE NEXT xxxx USERS TO BE FOLLOWED BY THE ACCOUNT
        users_to_follow = list(self.get_users_to_follow_list())
        do_not_follow = self.get_do_not_follow_list() # already-followed.txt

        # IF THIS LIST IS EMPTY, REPOPULATE WITH FOLLOWERS FROM ANOTHER ACCOUNT
        if len(users_to_follow) == 0:
            users_to_follow = list(self.TWITTER_CONNECTION.followers.ids(screen_name=user_twitter_handle)["ids"][:5000]) # followers of target account
            print ("Pulling", user_twitter_handle, "user list")
            with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "a") as out_file:
                for user_id in users_to_follow:
                    out_file.write(str(user_id) + "\n")

        user_id = str(users_to_follow[0])
        # print (user_id)

        try:
            # REMOVE USER_ID FROM LIST IF WE ARE FOLLOWING THEM ALREADY
            if (user_id in following or user_id in do_not_follow):
                with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "r+") as out_file:
                    d = out_file.readlines()
                    out_file.seek(0)
                    for i in d:
                        if i != user_id:
                            out_file.write(i)
                    out_file.truncate()

            # IF NOT FOLLOWING, LET'S FOLLOW THEM
            elif (user_id not in following and user_id not in do_not_follow):
                self.TWITTER_CONNECTION.friendships.create(user_id=user_id, follow=False)
                print("Followed %s" % user_id.rstrip(), file=sys.stdout)
                # ADD USER TO FOLLOWING FILE
                with open(self.BOT_CONFIG["FOLLOWS_FILE"], "a") as out_file:
                    out_file.write(user_id)
                # REMOVE USER FROM "TO FOLLOW" FILE
                with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "r+") as out_file:
                    d = out_file.readlines()
                    out_file.seek(0)
                    for i in d:
                        if i != user_id:
                            out_file.write(i)
                    out_file.truncate()

        except TwitterHTTPError as api_error:
            # quit on rate limit errors
            if "unable to follow more people at this time" in str(api_error).lower():
                print("You are unable to follow more people at this time. "
                      "Wait a while before running the bot again or gain "
                      "more followers.", file=sys.stderr)
                time.sleep(3600)
            if "cannot find" in str(api_error).lower():
                print("Cannot find user, removing user")
                with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "r+") as out_file:
                    d = out_file.readlines()
                    out_file.seek(0)
                    for i in d:
                        if i != user_id:
                            out_file.write(i)
                    out_file.truncate()
            if "blocked" in str(api_error).lower():
                print("Blocked from following user, removing")
                with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "r+") as out_file:
                    d = out_file.readlines()
                    out_file.seek(0)
                    for i in d:
                        if i != user_id:
                            out_file.write(i)
                    out_file.truncate()
            if "age" in str(api_error).lower():
                print("Age verification required, removing user")
                with open(self.BOT_CONFIG["USERS_TO_FOLLOW_FILE"], "r+") as out_file:
                    d = out_file.readlines()
                    out_file.seek(0)
                    for i in d:
                        if i != user_id:
                            out_file.write(i)
                    out_file.truncate()


            # don't print "already requested to follow" errors - they're
            # frequent
            if "already requested to follow" not in str(api_error).lower():
                print("Error: %s" % (str(api_error)), file=sys.stderr)


    def auto_unfollow_nonfollowers(self,count=None):
        """
            Unfollows everyone who hasn't followed you back.
        """

        following = self.get_follows_list()
        followers = self.get_followers_list()

        not_following_back = following - followers
        not_following_back = list(not_following_back)[:count]
        # update the "already followed" file with users who didn't follow back
        already_followed = set(not_following_back)
        already_followed_list = []
        with open(self.BOT_CONFIG["ALREADY_FOLLOWED_FILE"], "r") as in_file:
            for line in in_file:
                already_followed_list.append(int(line))

        already_followed.update(set(already_followed_list))

        with open(self.BOT_CONFIG["ALREADY_FOLLOWED_FILE"], "w") as out_file:
            for val in already_followed:
                out_file.write(str(val) + "\n")

        for user_id in not_following_back:
            if user_id not in self.BOT_CONFIG["USERS_KEEP_FOLLOWING"]:

                self.wait_on_action()

                self.TWITTER_CONNECTION.friendships.destroy(user_id=user_id)
                print("Unfollowed %d" % (user_id), file=sys.stdout)

    def auto_unfollow_nonfollowers_2(self):
        """
            Unfollows everyone who hasn't followed you back.
        """

        following = self.get_follows_list()
        followers = self.get_followers_list()

        not_following_back = following - followers

        # CHOOSE USER TO UNFOLLOW
        user_to_unfollow = int(list(not_following_back)[0])

        # UPDATE THE ALREADY FOLLOWED FILE WITH USER THAT WE ARE UNFOLLOWING
        already_followed_list = []
        with open(self.BOT_CONFIG["ALREADY_FOLLOWED_FILE"], "r") as in_file:
            for line in in_file:
                already_followed_list.append(int(line))

        if user_to_unfollow not in already_followed_list:
            already_followed_list.append(user_to_unfollow)

        with open(self.BOT_CONFIG["ALREADY_FOLLOWED_FILE"], "w") as out_file:
            for val in already_followed_list:
                out_file.write(str(val) + "\n")

        # EXECUTE UNFOLLOW COMMAND

        if user_to_unfollow not in self.BOT_CONFIG["USERS_KEEP_FOLLOWING"]:
            try:
                # self.wait_on_action()

                self.TWITTER_CONNECTION.friendships.destroy(user_id=user_to_unfollow)
                print("Unfollowed %d" % (user_to_unfollow), file=sys.stdout)
            except TwitterHTTPError as api_error:
                print(api_error)


            # UPDATE FOLLOWING LIST
            user_id = (str(user_to_unfollow) + "\n")
            # print(user_id)
            with open(self.BOT_CONFIG["FOLLOWS_FILE"], "r+") as out_file:
                d = out_file.readlines()
                out_file.seek(0)
                for i in d:
                    if i != user_id:
                        out_file.write(i)
                out_file.truncate()


   

    def send_tweet(self, message):
        """
            Posts a tweet.
        """

        return self.TWITTER_CONNECTION.statuses.update(status=message)

    def auto_add_to_list(self, phrase, list_slug, count=100, result_type="recent"):
        """
            Add users to list slug that are tweeting phrase.
        """

        result = self.search_tweets(phrase, count, result_type)

        for tweet in result["statuses"]:
            try:
                if tweet["user"]["screen_name"] == self.BOT_CONFIG["TWITTER_HANDLE"]:
                    continue

                result = self.TWITTER_CONNECTION.lists.members.create(owner_screen_name=self.BOT_CONFIG["TWITTER_HANDLE"],
                                                                      slug=list_slug,
                                                                      screen_name=tweet["user"]["screen_name"])
                print("User %s added to the list %s" % (tweet["user"]["screen_name"], list_slug), file=sys.stdout)
            except TwitterHTTPError as api_error:
                print(api_error)

def memoirsofanentrepreneur(lonelyplanet):

    memoirsofanentrepreneur = TwitterBot("lovingwhisky_config.txt")
    print("Initialising lovingwhisky")

    #########################Sync Twitter followers and followings if file is more than a day old
    if (time.time() - os.path.getmtime(lovingwhisky.BOT_CONFIG["FOLLOWS_FILE"]) > 3600 or time.time() - os.path.getmtime(lovingwhisky.BOT_CONFIG["FOLLOWERS_FILE"]) > 3600):
        lovingwhisky.sync_follows()
        print("Syncing lovingwhisky followers")

    # FOLLOW FOLLOWERS
    # lovingwhisky.auto_follow_followers(count=5)

    ####Automatically retweet any tweets that have a specific phrase
    lovingwhisky.auto_rt("@hipflask1", count=10)

    ########################Follow people based on who they follow
    print("Following followers of", account_to_follow)
    count = randint(50,70)
    lovingwhisky.auto_follow_followers_of_user(account_to_follow, count)

    print("End main_lovingwhisky")

