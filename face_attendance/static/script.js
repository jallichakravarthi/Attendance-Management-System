import dotenv from "dotenv";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { MongoClient } from "mongodb";
import fetch from "node-fetch";

dotenv.config({ path: "../.env" });

const secretKey = process.env.SECRET_KEY;
const MONGO_URI = process.env.MONGO_URI;
const DB_NAME = process.env.DB_NAME;

async function registerUser(email, password) {
  try {
    const client = await MongoClient.connect(MONGO_URI, { useUnifiedTopology: true });
    const db = client.db(DB_NAME);
    const users = db.collection("users");

    // Check if user exists and already has a password
    const existingUser = await users.findOne({ email });
    if (existingUser && existingUser.password) {
      console.log("User already exists");
      client.close();
      return;
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const result = await users.updateOne(
      { email },
      { $set: { password: hashedPassword } },
      { upsert: true }
    );

    const token = jwt.sign({ email }, secretKey, { expiresIn: "10h" });

    console.log("User registered successfully:", result.upsertedId || "existing user updated");

    const res = await fetch("http://localhost:5050/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, token })
    });

    const text = await res.text();
    console.log("token", token);

    client.close();
  } catch (err) {
    console.error("Error:", err.message);
  }
}

console.log(secretKey)
registerUser("tokentestuser1@test", "testuser");
