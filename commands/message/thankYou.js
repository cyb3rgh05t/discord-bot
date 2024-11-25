const { Client, Message, Formatters } = require("discord.js");

module.exports = {
  name: "thankyou",
  description: "doante channel thankyou message",
  category: "message",
  syntax: "command",
  permission: "ADMINISTRATOR",
  /**
   * @param {Client} client
   * @param {Message} message
   * @param {String[]} args
   */
  run: async (client, message, args) => {
    try {
      const msg = Formatters.hyperlink("PayPal", "https://paypal.me/IveFlammang");
      message.channel.send({
        content: `\n\nIch bedanke mich für den Support <:sclub:1310635856318562334>`
      });
    } catch (error) {
      message.channel.send("Some Error Occured");
      client.logger.log(error, "error")
    }
  }
}