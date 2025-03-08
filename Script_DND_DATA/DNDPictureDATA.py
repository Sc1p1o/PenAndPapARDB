import fitz  # PyMuPDF
from PIL import Image
import easyocr
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import LSTM, Dense, Embedding, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OCR-Funktion mit EasyOCR (Bild zu Text)
def extract_text_easyocr(image_path):
    try:
        reader = easyocr.Reader(["en"])  # Englisch als Sprache
        result = reader.readtext(image_path, detail=0)  # Nur erkannter Text zurückgeben
        return " ".join(result)  # Als String zurückgeben
    except Exception as e:
        logger.error(f"Fehler bei der Textextraktion: {e}")
        return ""

# PDF zu Bild konvertieren mit PyMuPDF (fitz)
def pdf_to_images(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        image_paths = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            image_path = f"temp_page_{i}.png"
            pix.save(image_path)
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        logger.error(f"Fehler bei der PDF-Konvertierung: {e}")
        return []

# Text aus PDF extrahieren
def extract_text_from_pdf(pdf_path):
    image_paths = pdf_to_images(pdf_path)
    full_text = ""
    for img_path in image_paths:
        full_text += extract_text_easyocr(img_path) + "\n"
        os.remove(img_path)  # Temporäre Bilder löschen
    return full_text.strip()

# Beispiel-Daten (D&D-Charakterbogen-Kategorien)
texts = [
    "Strength: 18 Dexterity: 14 Constitution: 16 Intelligence: 12 Wisdom: 10 Charisma: 8",
    "AC: 15 HP: 30 Speed: 30ft Proficiency: +2 Spell Slots: 2"
]
labels = [0, 1]  # 0 = Attribute, 1 = Kampfwerte

# Tokenizer für die Textverarbeitung
tokenizer = Tokenizer(num_words=1000)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
padded_sequences = pad_sequences(sequences, maxlen=10)

# Neuronales Netzwerk definieren
def create_model():
    model = keras.Sequential([
        Embedding(input_dim=1000, output_dim=64, input_length=10),
        Bidirectional(LSTM(64, return_sequences=True)),
        Bidirectional(LSTM(32)),
        Dense(32, activation="relu"),
        Dense(2, activation="softmax")  # Zwei Kategorien: Attribute oder Kampfwerte
    ])
    model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model

# Modell speichern
def save_model(model, path):
    model.save(path)

# Modell laden
def load_model(path):
    return keras.models.load_model(path)

# Training
def train_model(model, padded_sequences, labels):
    labels = np.array(labels)
    model.fit(padded_sequences, labels, epochs=10, verbose=1)
    return model

# Vorhersage-Funktion für neue Texte
def predict_text_category(model, tokenizer, text):
    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, maxlen=10)
    prediction = model.predict(padded)
    category = np.argmax(prediction)
    return "Attribute" if category == 0 else "Kampfwerte"

# Anwendung: Datei einlesen, Text extrahieren, kategorisieren
def process_file(file_path, model, tokenizer):
    if not os.path.exists(file_path):
        logger.error("Datei existiert nicht. Bitte gib einen gültigen Pfad an.")
        return
    
    try:
        if file_path.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_easyocr(file_path)
        
        logger.info("\nGelesener Text:\n%s", extracted_text)
        logger.info("\nKategorie: %s", predict_text_category(model, tokenizer, extracted_text))
    except Exception as e:
        logger.error(f"Fehler bei der Dateiverarbeitung: {e}")

# Hauptfunktion
def main():
    model_path = "dnd_model.h5"
    
    if os.path.exists(model_path):
        logger.info("Lade vorhandenes Modell...")
        model = load_model(model_path)
    else:
        logger.info("Erstelle und trainiere neues Modell...")
        model = create_model()
        model = train_model(model, padded_sequences, labels)
        save_model(model, model_path)
    
    # Nutzer gibt Datei-Pfad ein
    file_path = input("Gib den vollständigen Pfad zur Datei ein (PDF oder Bild): ").strip()
    process_file(file_path, model, tokenizer)

if __name__ == "__main__":
    main()