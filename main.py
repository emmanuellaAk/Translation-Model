import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
import time
from contextlib import asynccontextmanager
from typing import Literal

import torch
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

BASE_MODEL = "facebook/nllb-200-distilled-600M"
FT_MODEL = "emmanuellaak/nllb-asante-twi-mt"

models = {}
device = "cuda" if torch.cuda.is_available() else "cpu"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Loading models on {device}... (first run downloads ~5 GB)")
    models["base_tok"] = AutoTokenizer.from_pretrained(BASE_MODEL)
    models["base_model"] = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL).to(device)
    models["base_model"].eval()
    models["ft_tok"] = AutoTokenizer.from_pretrained(FT_MODEL)
    models["ft_model"] = AutoModelForSeq2SeqLM.from_pretrained(FT_MODEL).to(device)
    models["ft_model"].eval()
    print("Models loaded. Server ready.")
    yield
    models.clear()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class TranslateRequest(BaseModel):
    text: str
    direction: Literal["en2tw", "tw2en"]


def _translate(model, tokenizer, text: str, src_lang: str, tgt_lang: str) -> str:
    tokenizer.src_lang = src_lang
    forced_bos = tokenizer.convert_tokens_to_ids(tgt_lang)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256).to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos,
            num_beams=4,
            max_new_tokens=256,
        )
    return tokenizer.batch_decode(out, skip_special_tokens=True)[0]


@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/translate")
def do_translate(req: TranslateRequest):
    text = req.text.strip()
    if not text:
        return {"error": "Empty text"}

    if req.direction == "en2tw":
        src_lang, tgt_lang = "eng_Latn", "twi_Latn"
    else:
        src_lang, tgt_lang = "twi_Latn", "eng_Latn"

    t0 = time.time()
    base_out = _translate(models["base_model"], models["base_tok"], text, src_lang, tgt_lang)
    t1 = time.time()
    ft_out = _translate(models["ft_model"], models["ft_tok"], text, src_lang, tgt_lang)
    t2 = time.time()

    return {
        "base": base_out,
        "fine_tuned": ft_out,
        "base_time_ms": int((t1 - t0) * 1000),
        "ft_time_ms": int((t2 - t1) * 1000),
    }

class BatchRequest(BaseModel):
    texts: list[str]
    direction: Literal["en2tw", "tw2en"] = "en2tw"

@app.post("/batch")
def do_batch(req: BatchRequest):
    if req.direction == "en2tw":
        src_lang, tgt_lang = "eng_Latn", "twi_Latn"
    else:
        src_lang, tgt_lang = "twi_Latn", "eng_Latn"

    results = []
    for text in req.texts:
        text = text.strip()
        if not text:
            continue
        base_out = _translate(models["base_model"], models["base_tok"], text, src_lang, tgt_lang)
        # respect phrasebook if you added it; otherwise just the model
        ft_out = _translate(models["ft_model"], models["ft_tok"], text, src_lang, tgt_lang)
        results.append({"src": text, "base": base_out, "ft": ft_out})
    return {"results": results}