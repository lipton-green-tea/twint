import twint
import nest_asyncio

def main():
    proxy_host ="185.30.232.34"
    proxy_port = 80
    proxy_type = "http"
    proxy_username = "ypiwcjjj-rotate"
    proxy_password = "lhk3g9414mjp"

    t = twint.Config()
    t.Pandas = True
    t.Limit = 100
    t.Hide_output = True
    t.Store_object = True
    t.Search = "$ZM"
    t.Token_proxy_host = proxy_host
    t.Token_proxy_port = proxy_port
    t.Token_proxy_type = proxy_type
    t.Token_proxy_username = proxy_username
    t.Token_proxy_password = proxy_password
    twint.run.Search(t)
    nest_asyncio.apply()
    tweets_df = twint.storage.panda.Tweets_df
    tweets = []
    for x in range(0, len(tweets_df)):
        tweets.append({
            "id": tweets_df["id"][x],
            "timestamp": tweets_df["created_at"][x] / 1000,
            "content": tweets_df["tweet"][x]
        })
    print(tweets[0])

    print("[+] Testing complete!")


if __name__ == '__main__':
    main()