from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

#https://gql.readthedocs.io/en/stable/usage/variables.html

fnd_url = 'https://api.thegraph.com/subgraphs/name/f8n/fnd'

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url=fnd_url)

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
    query {
        creators(where: {id_in: ["0xa3ffe0852407580a043e704d1767adfc6d7acc41", "0xa6616f91d6a6d554213ca3f11f87dc525ea82803", "0xa5ed4cb9f460e89303ff1bf8b11b20987a4a2f72", "0x18cafd72a2b1efa67c9dafa77aa874618b27e38e", "0x2da88c8a45f32f2f84d7c675512ab045b3673cf9", "0x60b6f16f8b52c2966420fb4a7f9d1b7fdb999518", "0xae6523e811edc6d16b806875fbf2082e01fb3117", "0x65a7e0554eba32df644805bf6bd463f6e7a37a77", "0xc9bb2cd8c473f012bc839fcab644ec9d9f8f4557", "0x28aa1bda95bd43e502bf96fa8fd560edc9bc3ac2", "0x612b194218cedbe38a418b79106e12dedd75e0cc", "0x752f004b6e8cb9ed62be55c964257d1955478ea1", "0x71feea315e5026c09db3e260cdaec14c3d990b75", "0x9fef6f79977d2fbc78227d914222e78bfa95c30c", "0xd3a846303e52d6b7f7e2605103cc1af1f503a949", "0x4b416807473bd926ef0f3ee77d383e908e39dc3a", "0x3f6e2f3380ad5b3187c513832d14b9517d87639e", "0x52fcde35b1bd070eecb2c60a730af8816e420b53", "0xfb7d7c678c6bfc03952d9c9c7427d3fb8d3142f9", "0xe23d6582b37818f0fdeb4dcdbb8e63e6b7dacb84", "0xa6c2bbc6d9b2039965efce4d4fcafb47c4069e6a", "0x4c5c59b023e8b1b3c5633bfb4c9e7cc2f796579d", "0x471100bd609ac6bdb33a7e5d636d07057b77111a", "0xafe82d46210ec8d2b580fde4ed088a4b73083d7e", "0xf88a9e0d5bd66984628aee7944858ed992dda586", "0xd2f223de67d69e0c576a3a5f8a300cb02e79941d", "0x64e44f61615e6662cd70f1e57ca57b08c6660591", "0xfde8604980e8db7d965c86028bbbf136b7836606", "0xd4849bec09de2ab271ef92df0b6e7faaabf07adf", "0x14a02abba072c026dfef8f7f5582fc3ff18bcad7"] }) {
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
            nftHistory (orderBy: date, where: {event_in: [Bid, BuyPriceAccepted], date_gt: 1656992520, date_lte: 1656992700}) {
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

# Execute the query on the transport
result = client.execute(query)
print(result)
if __name__ == "__main__":
    main()