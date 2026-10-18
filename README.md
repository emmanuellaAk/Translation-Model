# English–Asante Twi Neural Machine Translation — Comparison App

A web application that translates between English and Asante Twi using two models
side by side: the unadapted base model (NLLB-200-distilled-600M) and a fine-tuned
model adapted to Asante Twi through staged domain-adaptive fine-tuning.

Built as part of a BSc Computer Science final-year project at the University of Ghana.

## What it does
Given a sentence and a direction (English→Twi or Twi→English), the app runs the
input through both the base and fine-tuned models and shows their translations
together, so the effect of the fine-tuning can be seen directly.

## Tech stack
- **Backend:** Python, FastAPI — loads both models at start-up and exposes a translation endpoint
- **Frontend:** HTML, CSS, JavaScript — single-page interface
- **Models:** Hugging Face Transformers (NLLB-200-distilled-600M base + fine-tuned checkpoint)

## Running locally
1. Install dependencies: