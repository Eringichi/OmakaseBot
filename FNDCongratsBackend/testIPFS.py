# https://github.com/ipfs-shipyard/py-ipfs-http-client
# https://ipfs.io/ipns/12D3KooWEqnTdgqHnkkwarSrJjeMP2ZJiADWLYADaNvUb6SQNyPF/docs/http_client_ref.html
import ipfshttpclient
client = ipfshttpclient.connect() 
# res = client.add('test.txt')
res = client.cat("QmUuunAv5wz33KEMJuRowcnpcibJ7AME11qPxdDTw46G3K/metadata.json")
print(res)
mp4 = client.cat("Qmc3KiG3KQh1iNmah1nRoDjurvJ2nTUb1BjwFH2ujmWm55/nft.mp4")
