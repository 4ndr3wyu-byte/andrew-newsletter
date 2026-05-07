var express = require("express");

var app = express();

var PORT = process.env.PORT || 10000;

var runMNLNews = require("./MNL-news");

app.use(express.json());

app.get("/", function(req, res) {

  res.send("MNL News Bot is running.");

});

app.get("/MNL-run-news", async function(req, res) {

  res.json({

    ok: true,

    message: "MNL news started"

  });

  runMNLNews();

});

app.listen(PORT, function() {

  console.log("MNL News Bot running on port " + PORT);

});