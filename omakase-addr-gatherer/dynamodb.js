import { DynamoDBClient, PutItemCommand, UpdateItemCommand } from "@aws-sdk/client-dynamodb";


const client = new DynamoDBClient({ region: "ap-northeast-2" });
//https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/dynamodb-example-document-client.html

const TableName = "DiscordUsers"
export async function PutFNDWallet(uid, url, addr) {
    console.log(`PutFNDWallet ${uid}, ${addr}`)
    try{
        const cmd = new PutItemCommand({
            TableName: TableName,
            Item:{
                uid : { S: uid },
                FND_PROFILE: {S:url},
                FND_WALLET: {S: addr}
            },
            ConditionExpression:"attribute_not_exists(uid)"
        })
        const data = await client.send(cmd)
        console.log("db status")
        console.log(data)
        return data
    } catch (err){
        console.log("ERROR")
        console.error(err);
        if (err.__type == "com.amazonaws.dynamodb.v20120810#ConditionalCheckFailedException"){
            console.log("KEY EXISTS")
            const updateParams = {
              TableName: TableName,
              Key: {
                uid: {S: uid} ,
              },
              UpdateExpression: "set FND_PROFILE = :p, FND_WALLET = :a",
              ExpressionAttributeValues: {
                ":a": {S: addr}, 
                ":p": {S:url}
              },
              ReturnValues: "ALL_NEW"
            }
            console.log("updateParams")
            try {
              const data = await client.send(new UpdateItemCommand(updateParams));
              console.log("CHECK")
              console.log("Success - item added or updated", data);
              return data;
            } catch (err) {
              console.log("Error", err);
              return false
            }
          }
        return true
    }   
}
