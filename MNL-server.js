var express = require("express");

var app = express();

var PORT = process.env.PORT || 10000;

app.use(express.json());

app.get("/", function(req, res) {

  res.send("MNL News Bot is running.");

});

app.get("/MNL-run-news", async function(req, res) {

  try {

    console.log("MNL news endpoint called");

    res.json({

      ok: true,

      message: "MNL news endpoint works"

    });

  } catch (error) {

    console.error("MNL news error:", error);

    res.status(500).json({

      ok: false,

      error: error.message

    });

  }

});

app.listen(PORT, function() {

  console.log("MNL News Bot running on port " + PORT);

});