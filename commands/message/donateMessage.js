const { Client, Message, Formatters } = require("discord.js");

module.exports = {
  name: "donate",
  description: "donate channel message",
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
        content: `=======================================\n\n🚨 **HELP2STAYONLINE** 🚨\n\n**StreamNet Plex** ist mein **Hobby**, doch habe ich und werde noch viel **Arbeit** reinstecken, deshalb bitte ich euch User mir manschmal zu helfen in dem ihr spendet damit die **Server** und **Premium Accounts** der Indexer bezahlt werden koennen, um euch das **beste Erlebnis** zu präsentieren <:streamnet:1033460420587049021>\n\n➡️  Die Server Wartungen und Accounts kommen auf ungefähr 120-130 € im Monat, diese möchte ich gerne so gut wie möglich durch Spenden abgedeckt haben.\n\n➡️  Ist es die erste Spende für die Server Einladung <#825352124547989544> wird euch die **StreamNet..er** Rolle vergeben.\n\n➡️  Nach einigen weiteren Spenden werde ich euch eine **Supporter** Rolle vergeben. *(kann bis zu 24h dauern)*\n\nDurch diese Rolle sehe ich dass euch StreamNet gefällt und richtig bei Gelegenheit unterstützt.\n\n➡️  Um eine Spende zu betätigen bitte ich euch über folgende Optionen zu spenden:`
      });
    } catch (error) {
      message.channel.send("Some Error Occured");
      client.logger.log(error, "error")
    }
  }
}