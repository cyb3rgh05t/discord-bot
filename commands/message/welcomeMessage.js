const { Client, Message } = require("discord.js");

module.exports = {
  name: "welcome",
  description: "welcome channel message",
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
      message.channel.send({
        content: `=======================================\n\n**Willkommen bei <:sclub:1310635856318562334> StreamNet Club's Discord Server**\n\n=======================================\n\n➡️  Wie bekomme ich Zutritt zum **StreamNet Club Service** ?\n\n**1. **Bestätige die** REGELN **in <#694495838013095967> !\n\n**2.** Suche dir ein Projekt aus  <#1246852243680919592> oder <#1246852387570978818> !\n\n**3.** Folge den Anweisungen um Zutritt zu bekommen !\n\n**4.** Viel Spass beim streamen.. <:sclub:1310635856318562334>`
      });
    } catch (error) {
      message.channel.send("Some Error Occured");
      client.logger.log(error, "error")
    }
  }
}