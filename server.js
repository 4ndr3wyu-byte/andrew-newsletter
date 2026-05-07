app.get("/", function(req, res) {

  res.send("Andrew schedule bot is running. MNL endpoint added.");

});

/* ━━━━━━━━━━━━━━━━━━━━

   MNL NEWS BOT

━━━━━━━━━━━━━━━━━━━━ */

app.get("/MNL-run-news", async function(req, res) {

  try {

    console.log("━━━━━━━━━━━━━━━━━━━━");

    console.log("MNL news bot started");

    console.log("━━━━━━━━━━━━━━━━━━━━");

    res.json({

      ok: true,

      message: "MNL news endpoint works"

    });

  } catch (error) {

    console.error("━━━━━━━━━━━━━━━━━━━━");

    console.error("MNL news error");

    console.error(error);

    console.error("━━━━━━━━━━━━━━━━━━━━");

    res.status(500).json({

      ok: false,

      error: error.message

    });

  }

});