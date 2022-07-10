import "dotenv/config";
import express from "express";
import {
  InteractionType,
  InteractionResponseType,
  InteractionResponseFlags,
  MessageComponentTypes,
  ButtonStyleTypes,
} from "discord-interactions";
import {
  VerifyDiscordRequest,
  getRandomEmoji,
  DiscordRequest,
} from "./utils.js";
import {
  WALLET_COMMAND,
  TEST_OMA_COMMAND,
  HasGuildCommands,
} from "./commands.js";

import {FNDScrape} from "./FNDScrapeCaller.js"


import { PutFNDWallet } from "./dynamodb.js";

// console.log(`AWS API KEY: ${process.env.AWS_ACCESS_KEY_ID}`)
// Create an express app
const app = express();
// Get port, or default to 3000
const PORT = process.env.PORT || 3000;
// Parse request body and verifies incoming requests using discord-interactions package
app.use(express.json({ verify: VerifyDiscordRequest(process.env.PUBLIC_KEY) }));

app.post("/interactions", async function (req, res) {
  // Interaction type and data
  const { type, id, data } = req.body;
  //   console.log("/interactions");
  //   console.log(req.body);
  /**
   * Handle verification requests
   */
  if (type === InteractionType.PING) {
    console.log("Ping?");
    return res.send({ type: InteractionResponseType.PONG });
  }
  if (type === InteractionType.APPLICATION_COMMAND) {
    const { name } = data;
    if (name === "test_omakase") {
      // Send a message into the channel where command was triggered from
      return res.send({
        type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data: {
          // Fetches a random emoji to send from a helper function
          content: "hello world " + getRandomEmoji(),
        },
      });
    } else if (name === "wallet") {
      const userId = req.body.member.user.id;
      return res.send({
        type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data: {
          // Fetches a random emoji to send from a helper function
          content: `Hi <@${userId}>! Choose the NFT market:`,
          flags: InteractionResponseFlags.EPHEMERAL,
          components: [
            {
              type: MessageComponentTypes.ACTION_ROW,
              components: [
                {
                  type: MessageComponentTypes.BUTTON,
                  // Append the game ID to use later on
                  custom_id: `FND_${req.body.id}`,
                  label: "FND",
                  style: ButtonStyleTypes.PRIMARY,
                },
                {
                  type: MessageComponentTypes.BUTTON,
                  // Append the game ID to use later on
                  custom_id: `OPENSEA_${req.body.id}`,
                  label: "Opensea",
                  style: ButtonStyleTypes.PRIMARY,
                  disabled: true,
                },
              ],
            },
          ],
        },
      });
    }
  }
  if (type === InteractionType.APPLICATION_MODAL_SUBMIT) {
    console.log("InteractionType.APPLICATION_MODAL_SUBMIT");
    const componentId = data.custom_id;
    console.log(data);
    console.log(data.components[0].components[0]);
    const url = data.components[0].components[0].value;
    const wallet = data.components[1].components[0].value;
    // if (custom_id.startsWith("FND_INPUT_")) {
    const userId = req.body.member.user.id;
    console.log("FND_INPUT_");
    console.log(`userId: ${userId}`);
    console.log(data);
    try {
      // update db, get status. If bad then res.send error message like try again later
      const dbStat = await PutFNDWallet(userId, url, wallet);
      if (!dbStat) {
        return false;
      }
      FNDScrape(url, wallet)
      //success
      await res.send({
        type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data: {
          // Fetches a random emoji to send from a helper function
          content: `Congrats! Your FND will now be tracked for new art :D`,
          // Indicates it'll be an ephemeral message
          flags: InteractionResponseFlags.EPHEMERAL,
        },
      });
    } catch (err) {
      console.error("Error sending message:", err);
    }
    // }
  }
  if (type === InteractionType.MESSAGE_COMPONENT) {
    console.log("InteractionType.MESSAGE_COMPONENT");
    const componentId = data.custom_id;
    console.log(`componentId: ${componentId}`);
    if (componentId.startsWith("FND_")) {
      console.log("FND_");
      try {
        await res.send({
          type: InteractionResponseType.APPLICATION_MODAL,
          data: {
            title: "WALLET FORM",
            custom_id: "wallet_modal",
            // content: `Please input that market's wallet`,
            components: [
              {
                type: MessageComponentTypes.ACTION_ROW,
                components: [
                  {
                    type: MessageComponentTypes.INPUT_TEXT,
                    style: 1,
                    custom_id: `FND_ADDR_${req.body.id}`,
                    label: "FND Profile",
                    placeholder: "https://foundation.app/@rofortyseven",
                    required: true,
                  },
                ],
              },
              {
                type: MessageComponentTypes.ACTION_ROW,
                components: [
                  {
                    type: MessageComponentTypes.INPUT_TEXT,
                    style: 1,
                    custom_id: `FND_WALLET_${req.body.id}`,
                    label: "FND Wallet",
                    placeholder: "0x<40chars>",
                    required: true,
                    // min_length: 40,
                    max_length: 42,
                  },
                ],
              },
            ],
          },
        });
      } catch (err) {
        console.error("Error sending message:", err);
      }
    }
  }
});
app.listen(PORT, () => {
  console.log("Listening on port", PORT);

  // Check if guild commands from commands.json are installed (if not, install them)
  HasGuildCommands(process.env.APP_ID, process.env.GUILD_ID, [
    WALLET_COMMAND,
    TEST_OMA_COMMAND,
  ]);
});
