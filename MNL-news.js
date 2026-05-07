var Parser = require("rss-parser");

var axios = require("axios");

var OpenAI = require("openai");

var parser = new Parser();

var openai = new OpenAI({

  apiKey: process.env.OPENAI_API_KEY

});

var TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

var TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

var SOURCES = [

  { name: "The Verge", url: "https://www.theverge.com/rss/index.xml" },

  { name: "TechCrunch", url: "https://techcrunch.com/feed/" },

  { name: "Ars Technica", url: "https://feeds.arstechnica.com/arstechnica/index" },

  { name: "Electrek", url: "https://electrek.co/feed/" },

  { name: "MacRumors", url: "https://www.macrumors.com/macrumors.xml" }

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

async function summarizeArticle(title) {

  try {

    var response = await openai.chat.completions.create({

      model: "gpt-4.1-mini",

      messages: [

        {

          role: "system",

          content:

            "너는 세계 최고의 IT 뉴스 에디터다. 기사 제목을 보고 한국어 제목과 핵심 요약 3줄을 만들어라."

        },

        {

          role: "user",

          content:

            "기사 제목:\n" +

            title +

            "\n\n출력 형식:\n제목:\n요약1:\n요약2:\n요약3:"

        }

      ],

      temperature: 0.7

    });

    return response.choices[0].message.content;

  } catch (error) {

    console.log("SUMMARY ERROR");

    console.log(error.message);

    return (

      "제목:\n" +

      title +

      "\n" +

      "요약1:\nAI 요약을 생성하지 못했습니다.\n" +

      "요약2:\nOpenAI API quota 또는 billing 상태를 확인해야 합니다.\n" +

      "요약3:\n원문 링크를 통해 기사를 확인할 수 있습니다."

    );

  }

}

async function collectNews() {

  var articles = [];

  for (var i = 0; i < SOURCES.length; i++) {

    try {

      console.log("Loading:", SOURCES[i].name);

      var feed = await parser.parseURL(SOURCES[i].url);

      for (var j = 0; j < Math.min(feed.items.length, 2); j++) {

        var item = feed.items[j];

        articles.push({

          source: SOURCES[i].name,

          title: item.title,

          link: item.link

        });

      }

    } catch (error) {

      console.log("RSS ERROR:", SOURCES[i].name);

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

    message += "📰 오늘의 테크 뉴스\n";

    message += "━━━━━━━━━━━━━━━━━━\n\n";

    for (var i = 0; i < articles.length; i++) {

      var summary = await summarizeArticle(articles[i].title);

      message += "🌐 [" + articles[i].source + "]\n\n";

      message += summary + "\n\n";

      message += "원문:\n" + articles[i].link + "\n\n";

      message += "━━━━━━━━━━━━━━━━━━\n\n";

    }

    await sendTelegram(message);

    console.log("Telegram sent");

  } catch (error) {

    console.log("MNL ERROR");

    console.log(error);

  }

}

module.exports = runMNLNews;