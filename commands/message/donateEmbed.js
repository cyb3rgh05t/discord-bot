const { Client, Message, Formatters, MessageEmbed } = require("discord.js");

module.exports = {
  name: "paylink",
  description: "donate channel payment links embed",
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
      const msg = new MessageEmbed()
      .setColor("DARK_BUT_NOT_BLACK")
      //.setTitle("Spenden Optionen")
      .addFields([{
               
                name: "💗 Ko-Fi",
                value: `
                <:icon_reply:993231553083736135>[Support StreamNet Club](https://ko-fi.com/streamnetclub)
                `

            }
            
    ])
      message.channel.send({
             embeds: [msg]
        });
    } catch (error) {
      message.channel.send("Some Error Occured");
      client.logger.log(error, "error")
    }
  }
}