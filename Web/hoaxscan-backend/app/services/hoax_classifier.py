"""HoaxScan ML-05: membungkus model IndoBERT hasil ML-03 menjadi interface classify(text).

Pemakaian di backend FastAPI:

    from hoax_classifier import HoaxClassifier

    clf = HoaxClassifier("models/indobert-hoax-v1")   # load sekali saat server menyala
    hasil = clf.classify(teks_artikel)
    # {"label": "hoax", "prob_hoax": 0.93, "confident": True, "status": "ok", ...}

Aturan keputusan:
- label      : "hoax" bila prob_hoax >= 0.5, selain itu "fakta".
- confident  : True bila prob_hoax >= threshold atau prob_hoax <= 1 - threshold.
               False berarti skor belum meyakinkan dan artikel diteruskan ke Gemini.
- threshold  : hasil kalibrasi ML-06, dibaca dari inference_config.json di folder model.
               Bila file itu tidak ada, dipakai 0.85. Bisa juga diisi langsung saat membuat objek.

Artikel panjang dipecah menjadi beberapa potongan sepanjang max_length token (sama dengan
saat training, dibaca dari training_config.json) yang saling tumpang tindih sebanyak stride
token. Skor tiap potongan lalu digabung (rata-rata atau maksimum, pilihan ML-06).
"""

import json
import os
import re

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Pembersihan sama dengan ML-01 (ML_preprocessing.ipynb, bagian 3), supaya teks dari
# scraping mirip dengan teks yang dilihat model saat training. Langkah khusus dataset
# Turnbackhoax (memotong "Penjelasan:", pemisah "= = =") sengaja tidak dipakai di sini.
URL_RE = re.compile(r"https?://\S+|www\.\S+|pic\.twitter\.com/\S+", re.I)
MEDIA_RE = re.compile(
    r"^\s*(?:[A-Z][A-Za-z .]{0,30},\s*)?(?:CNN Indonesia|KOMPAS\.com|TEMPO\.CO)"
    r"(?:,\s*[A-Za-z ]{0,30})?\s*[-–—]+\s*"
)


def clean_text(text):
    t = str(text)
    t = re.sub(r"Baca [Jj]uga\s*:?[^\n.]*", " ", t)
    t = MEDIA_RE.sub(" ", t)
    t = URL_RE.sub(" ", t)
    t = re.sub(r"\[(?:SALAH|HOAKS?|HOAX|DISINFORMASI|NARASI|SUMBER)[^\]]*\]", " ", t, flags=re.I)
    t = re.sub(r"\b(?:Sumber|Kategori)\s*:[^\n]*", " ", t, flags=re.I)
    t = re.sub(r"@\w+", " ", t)
    t = t.replace("#", " ")
    t = re.sub(r"[“”\"]", " ", t)
    t = t.replace("&amp;", "&").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def _read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


class HoaxClassifier:
    def __init__(self, model_dir, threshold=None, stride=64, max_chunks=16,
                 aggregate=None, min_words=5, batch_size=8, device=None):
        calibration = _read_json(os.path.join(model_dir, "inference_config.json"))
        if threshold is None:
            threshold = calibration.get("threshold", 0.85)
        if aggregate is None:
            aggregate = calibration.get("aggregate", "mean")
        if not 0.5 <= threshold < 1:
            raise ValueError("threshold harus di antara 0.5 dan 1")
        if aggregate not in ("mean", "max"):
            raise ValueError('aggregate harus "mean" atau "max"')

        self.threshold = threshold
        self.max_chunks = max_chunks
        self.aggregate = aggregate
        self.min_words = min_words
        self.batch_size = batch_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device).eval()
        self.hoax_id = self.model.config.label2id.get("hoax", 1)

        config = _read_json(os.path.join(model_dir, "training_config.json"))
        self.max_length = config.get("max_length", 256)
        if not 0 <= stride < self.max_length - 2:
            raise ValueError(f"stride harus di antara 0 dan {self.max_length - 3}")
        self.stride = stride

    def _chunks(self, text):
        # Potongan dibuat manual: return_overflowing_tokens di transformers 5 tidak
        # mengembalikan semua potongan untuk teks yang sangat panjang.
        ids = self.tokenizer(text, add_special_tokens=False, verbose=False)["input_ids"]
        size = self.max_length - 2  # sisakan tempat untuk [CLS] dan [SEP]
        step = size - self.stride
        starts = range(0, max(len(ids) - self.stride, 1), step)
        cls, sep = self.tokenizer.cls_token_id, self.tokenizer.sep_token_id
        return [[cls] + ids[s:s + size] + [sep] for s in starts]

    @torch.inference_mode()
    def _chunk_probs(self, chunk_ids):
        probs = []
        for i in range(0, len(chunk_ids), self.batch_size):
            batch = self.tokenizer.pad({"input_ids": chunk_ids[i:i + self.batch_size]},
                                       return_tensors="pt").to(self.device)
            logits = self.model(**batch).logits
            probs += torch.softmax(logits.float(), dim=-1)[:, self.hoax_id].tolist()
        return probs

    def classify(self, text):
        cleaned = clean_text(text or "")
        n_words = len(cleaned.split())
        result = {
            "label": None, "prob_hoax": None, "confident": False, "status": "ok",
            "threshold": self.threshold, "n_words": n_words, "n_tokens": 0,
            "n_chunks": 0, "chunks_used": 0, "chunk_probs": [],
        }
        if n_words < self.min_words:
            result["status"] = "teks_terlalu_pendek"
            return result

        chunk_ids = self._chunks(cleaned)
        used = chunk_ids[:self.max_chunks]
        chunk_probs = self._chunk_probs(used)
        prob = max(chunk_probs) if self.aggregate == "max" else sum(chunk_probs) / len(chunk_probs)

        # jumlah token isi: potongan pertama utuh, potongan berikutnya dikurangi tumpang tindih
        content = [len(ids) - 2 for ids in chunk_ids]
        n_tokens = content[0] + sum(c - self.stride for c in content[1:])

        result.update({
            "label": "hoax" if prob >= 0.5 else "fakta",
            "prob_hoax": round(prob, 4),
            "confident": prob >= self.threshold or prob <= 1 - self.threshold,
            "status": "terpotong" if len(chunk_ids) > self.max_chunks else "ok",
            "n_tokens": n_tokens,
            "n_chunks": len(chunk_ids),
            "chunks_used": len(used),
            "chunk_probs": [round(p, 4) for p in chunk_probs],
        })
        return result

    def classify_batch(self, texts):
        return [self.classify(t) for t in texts]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print('Pemakaian: python hoax_classifier.py <folder_model> "teks artikel"')
        sys.exit(1)
    clf = HoaxClassifier(sys.argv[1])
    print(json.dumps(clf.classify(sys.argv[2]), indent=2, ensure_ascii=False))
