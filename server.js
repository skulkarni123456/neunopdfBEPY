const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Storage
const upload = multer({ dest: "uploads/" });

// ⭐ API ROUTES
app.post("/api/word2pdf", upload.single("file"), async (req, res) => {
  return res.json({ status: "ok", message: "word2pdf working on Render" });
});

app.post("/api/split", upload.single("file"), async (req, res) => {
  return res.json({ status: "ok", message: "split working" });
});

// You can add more routes here exactly as your old backend

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// ⭐ Render PORT
const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log("Backend running on Render:", PORT);
});
