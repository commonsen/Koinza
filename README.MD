# 🛍️ KOINZA: AI-Powered E-Commerce Search Engine

**KOINZA** is a dynamic web application built with Python Flask that uses Large Language Models (LLaMA-3.3 provided by Groq) and external shopping APIs (RapidAPI, Serper.dev) to provide ranked, real-time product search results.

It's designed to offer users a smarter way to find products across various online stores by prioritizing current pricing, ratings, and buying links.

## ✨ Features

* **Intelligent Search:** Uses Groq's LLaMA-3.3 model for intelligent ranking and fallback web search.
* **Real-Time Data:** Integrates with **RapidAPI** and **Serper.dev (Google Shopping)** to fetch up-to-date product information, pricing, and purchase links.
* **API Fallback:** If external shopping API calls fail or run out of free tier limits, the application automatically falls back to the **Groq AI web search** feature.
* **Filtering:** Allows users to filter products by price range and brand.
* **Modern Backend:** Powered by **Python** and **Flask**, deployed using **Gunicorn**.

## 🚀 Deployment Status

This application is currently deployed and hosted on **Render (Free Tier)**.

* **Live URL:** (`https://koinza.onrender.com/`)
