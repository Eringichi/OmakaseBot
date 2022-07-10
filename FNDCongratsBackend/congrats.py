from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import time, discord
from datetime import datetime
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
import boto3
import os

import json

d_client = discord.Client()
# DIR = '/home/jl/ProjectS/omakase/discordBots/FNDCongratsBackend/'
DIR = "saves"
os.makedirs(DIR,exist_ok=True)
LOCAL_FILE = f"{DIR}/congrats.json"
def get_current_unix():
    return int(time.time())
def eventStrings(evt,name,price = 0):
    if (evt == "Bid"):
        return [
            ":moneybag: **BID RECEIVED** :moneybag:",
            f"**{name}'s** below NFT has received a bid for **{price} ETH**"
        ]
    elif (evt == "BuyPriceAccepted"):
        return [
            ":moneybag: **BUY NOW PRICE ACCEPTED** :moneybag:",
            f"**{name}'s** below NFT's Buy Now Price was accepted for **{price} ETH**"
        ] 
    elif (evt == "Minted"):
        return [
            "🔨 **MINTING** 🔨",
            f"**{name}** has minted the below NFT"
        ]
    elif (evt == "Listed"):
        return [
            "🌟 **LISTING** 🌟",
            f"**{name}** has listed the below NFT for **{price} ETH**"
        ]
    elif (evt == "PriceChanged"):
        return [
            "📈 **PRICE CHANGE** 📉 ",
            f"**{name}** has changed the below NFT's price to **{price} ETH**"
        ]
    elif (evt == "Unlisted"):
        return [
            "❌ **DELISTING** ❌"
            f"**{name}** has delisted the below NFT"
        ]
    elif (evt == "BuyPriceSet"):
        return [
            "📈 **BUY NOW PRICE SET** 📉",
            f"**{name}** has set the below NFT's Buy Now price to **{price} ETH**"
        ]
    elif (evt == "SellAlr"):
        return [
            ":partying_face: **Yay!** :partying_face:",
            f"**{name}** has brought home the dough for **{price} ETH**"
        ]
#         return "🥈 LISTING ON SECONDARY 🥈",0x53...303d has listed HxxG's NFT below on secondary market for 10 ETH  
    return ""

#https://dynobase.dev/dynamodb-python-with-boto3/#:~:text=To%20get%20all%20items%20from,the%20results%20in%20a%20loop.
def scanFromDb():
    #print("scanFromDb")
    dynamodb = boto3.resource('dynamodb',
                        region_name="ap-northeast-2",
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                        )
    table = dynamodb.Table('FND_DETAILS')

    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    return data


def isLocalDataOutdated():
    print(LOCAL_FILE)
    return True
    if(not os.path.exists(LOCAL_FILE)):
        return True
    ct = int(os.path.getctime(LOCAL_FILE))#int(os.stat(LOCAL_FILE).st_birthtime)
    if (ct + 6 * 3600 < get_current_unix()):
        return True
    return False

def saveToLocal(toSave:dict):
    print("saveToLocal")
    convert_file =  open(LOCAL_FILE, 'w')
    convert_file.write(json.dumps(toSave))
    convert_file.close()
    print("success")

def loadFromLocal():
    with open(LOCAL_FILE) as fp:
        return json.load(fp)

def getWalletData():
    print("getWalletData")
    # Check local, if dont exist pull external
    isOutdated = isLocalDataOutdated()
    data = {}
    if(isOutdated):
        print("outdated")
        data = scanFromDb()
        temp = {}
        for d in data:
            temp[d['wallet'].lower()] = d
        data = temp
        saveToLocal(data)
    else:
        data = loadFromLocal()

    print(data)
    return data

async def queryFND(addresses):
    fnd_url = 'https://api.thegraph.com/subgraphs/name/f8n/fnd'

    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=fnd_url)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    end_time = get_current_unix()
    start_time = end_time - 3600

    query = gql(
        """
        query test($start:BigInt, $end:BigInt, $id_in: [ID!]){
            creators(where: {id_in: $id_in }) {
                id
                nfts (orderBy: dateMinted) {
                nftContract {
                    id
                    name
                    symbol
                }
                tokenId
                tokenIPFSPath
                dateMinted
                isFirstSale
                nftHistory (orderBy: date, where: {
                    event_in: [Bid, BuyPriceAccepted], date_gt: $start, date_lte: $end
                }) {
                    actorAccount {
                    id
                    }
                    event
                    date
                    amountInETH
                }
                lastSalePriceInETH
                }
            }
        }
    """
    )
    # addresses = ["0xa3ffe0852407580a043e704d1767adfc6d7acc41", "0xa6616f91d6a6d554213ca3f11f87dc525ea82803", "0xa5ed4cb9f460e89303ff1bf8b11b20987a4a2f72", "0x18cafd72a2b1efa67c9dafa77aa874618b27e38e", "0x2da88c8a45f32f2f84d7c675512ab045b3673cf9", "0x60b6f16f8b52c2966420fb4a7f9d1b7fdb999518", "0xae6523e811edc6d16b806875fbf2082e01fb3117", "0x65a7e0554eba32df644805bf6bd463f6e7a37a77", "0xc9bb2cd8c473f012bc839fcab644ec9d9f8f4557", "0x28aa1bda95bd43e502bf96fa8fd560edc9bc3ac2", "0x612b194218cedbe38a418b79106e12dedd75e0cc", "0x752f004b6e8cb9ed62be55c964257d1955478ea1", "0x71feea315e5026c09db3e260cdaec14c3d990b75", "0x9fef6f79977d2fbc78227d914222e78bfa95c30c", "0xd3a846303e52d6b7f7e2605103cc1af1f503a949", "0x4b416807473bd926ef0f3ee77d383e908e39dc3a", "0x3f6e2f3380ad5b3187c513832d14b9517d87639e", "0x52fcde35b1bd070eecb2c60a730af8816e420b53", "0xfb7d7c678c6bfc03952d9c9c7427d3fb8d3142f9", "0xe23d6582b37818f0fdeb4dcdbb8e63e6b7dacb84", "0xa6c2bbc6d9b2039965efce4d4fcafb47c4069e6a", "0x4c5c59b023e8b1b3c5633bfb4c9e7cc2f796579d", "0x471100bd609ac6bdb33a7e5d636d07057b77111a", "0xafe82d46210ec8d2b580fde4ed088a4b73083d7e", "0xf88a9e0d5bd66984628aee7944858ed992dda586", "0xd2f223de67d69e0c576a3a5f8a300cb02e79941d", "0x64e44f61615e6662cd70f1e57ca57b08c6660591", "0xfde8604980e8db7d965c86028bbbf136b7836606", "0xd4849bec09de2ab271ef92df0b6e7faaabf07adf", "0x14a02abba072c026dfef8f7f5582fc3ff18bcad7"]
    # addresses = addresses[:-20]
    # addresses.append("0xF46E179D808eBdFAED29Cd511326aEe00049BCFa".lower())
    params = {
        "start": start_time,
        "end": end_time,
        "id_in": addresses
    }
    result = await client.execute_async(query, variable_values=params)
    return result


def constructLink(link, tokenId):
    return f"{link}/{tokenId}"

def getUsernameByWallet(addr):
    #TODO: access local json
    return "@Okanyan"

def getNameByWallet(addr):
    return "Oka"

def messageCreator(data,addr, nftObj):
    sym = nftObj['nftContract']['symbol']
    collectName = nftObj['nftContract']['name']
    tokenId = nftObj['tokenId']
    # username = getUsernameByWallet(addr)
    collectionLink  = ""
    for c in data['collections']:
        token = c['token'].lower()
        print(f"{token} vs {collectName} vs {sym}")
        if token == collectName.lower() or token == sym.lower():
            collectionLink = c['link']
            break
    if len(collectionLink) == 0:
        collectionLink = f"https://foundation.app/{data['username']}/foundation"
    
    name = data['name']
    link = constructLink(collectionLink,tokenId)
    msgs = []
    print(f"art link: {link}")
    for hist in nftObj['nftHistory']:
        temp = []
        temp.append("=" * 50)
        event = hist['event']
        if (nftObj['lastSalePriceInETH'] != None):
            event = "SellAlr"
        eventStrs = eventStrings(event, name, hist['amountInETH'] if 'amountInETH' in hist else 0)
        temp.append(eventStrs[0])
        temp.append(eventStrs[1])
        temp.append(f"**Event Date:** {datetime.utcfromtimestamp(int(hist['date'])).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        temp.append(f"**FND Link:** {link}")
        msgs.append('\n'.join(temp))
    return msgs

def create_batches(wallets: dict):
    SIZE=30
    toRet = []
    idx = 0
    addrs = list(wallets.keys())
    while(idx < len(addrs) - SIZE):
        toRet.append(addrs[idx:idx+SIZE])
        idx += SIZE

    toRet.append(addrs[idx:])
    return toRet

@tasks.loop(minutes = 60)
async def main():
    wallets = getWalletData()
    batches = create_batches(wallets)
    for batch in batches:
        addresses = batch
        print("queryFND")
        result = await queryFND(addresses)
        msgs = []
        for c in result['creators']:
            print(f"id: {c['id']}")
            addr = c['id']
            for nft in c['nfts']:
                if(len(nft['nftHistory']) > 0):
                    print(nft)
                    msgs.extend(messageCreator(wallets[addr],addr,nft))

        # SPAM CONGRATS CHANNEL
        # print("msgs")
        # print(msgs)
        # await d_client.wait_until_ready()
        channel_id = 994651198948909094
        channel = d_client.get_channel(channel_id)
        for msg in msgs:
            await channel.send(msg)
        
@d_client.event
async def on_ready():
    # await main()
    await main.start()
    print("Bot ready.")



d_client.run(os.environ["DISCORD_TOKEN"])
#https://stackoverflow.com/questions/69778259/how-do-i-make-a-bot-to-message-every-hour-on-discord-without-using-a-discord-bot
