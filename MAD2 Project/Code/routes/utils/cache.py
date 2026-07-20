from Code.app import redis_client

def cache_campaign(campaign_id, campaign_data):
    redis_client.set(f'campaign:{campaign_id}', campaign_data)

def get_cached_campaign(campaign_id):
    return redis_client.get(f'campaign:{campaign_id}')
