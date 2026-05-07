var Parser = require("rss-parser");

var axios = require("axios");

var parser = new Parser();

var TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

var TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

var SOURCES = [

  {

    name: "The Verge",

    url: "https://www.theverge.com/rss/index.xml"

  },

  {

    name: "TechCrunch",

    url: "https://techcrunch.com/feed/"

  },

  {

    name: "Ars Technica",

    url: "https://feeds.arstechnica.com/arstechnica/index"

  },

  {

    name: "Electrek",

    url: "https://electrek.co/feed/"

  },

  {

    name: "MacRumors",

    url: "https://www.macrumors.com/macrumors.xml"

  }

];

async function sendTelegram(text) {

  var url =

    "https://api.telegram.org/bot" +

    TELEGRAM_BOT_TOKEN +

    "/sendMessage";

  await axios.post(url, {

    chat_id: TELEGRAM_CHAT_ID,

    text: text

  });

}

async function collectNews() {

  var articles = [];

  for (var i = 0; i < SOURCES.length; i++) {

    try {

      console.log("Loading:", SOURCES[i].name);

      var feed = await parser.parseURL(SOURCES[i].url);

      for (var j = 0; j < Math.min(feed.items.length, 3); j++) {

        var item = feed.items[j];

        articles.push({

          source: SOURCES[i].name,

          title: item.title,

          link: item.link

        });

      }

    } catch (error) {

      console.log("RSS Error:", SOURCES[i].name);

      console.log(error.message);

    }

  }

  return articles;

}

async function runMNLNews() {

  try {

    console.log("━━━━━━━━━━━━━━━━━━━━");

    console.log("MNL NEWS START");

    console.log("━━━━━━━━━━━━━━━━━━━━");

    var articles = await collectNews();

    var message = "";

    message += "📰 MNL Morning News\n";

    message += "━━━━━━━━━━━━━━━━━━\n\n";

    for (var i = 0; i < articles.length; i++) {

      message +=

        "• [" +

        articles[i].source +

        "]\n";

      message +=

        articles[i].title +

        "\n";

      message +=

        articles[i].link +

        "\n\n";

    }

    await sendTelegram(message);

    console.log("Telegram sent");

  } catch (error) {

    console.log("MNL ERROR");

    console.log(error);

  }

}

module.exports = runMNLNews;