app.get("/MNL-run-news", async function(req, res) {

  try {

    console.log("MNL news bot started");

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