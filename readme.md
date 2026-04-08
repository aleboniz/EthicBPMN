# EthicBPMN

## Descrizione del Progetto
**EthicBPMN** è un motore di validazione (Rule Engine) scritto in Python per l'analisi basata sui principi etici dei business process. 

Il software prende in input file di processo standard (`.bpmn` in formato XML) arricchiti con la **Matrice EthicBPMN** e applica un'architettura di validazione a due livelli:

1. **Hard Compliance (Analisi Deterministica):** Un parser incrocia la topologia del diagramma (i costrutti BPMN) con i parametri etici della matrice EthicBPMN per rilevare violazioni strutturali delle 11 regole etiche.
2. **Soft Compliance (Analisi Semantica):** Un'integrazione con LLM (Intelligenza Artificiale) analizza il contesto semantico dei nodi per suggerire ulteriori ottimizzazioni.
Il progetto utilizza **Llama-3.1-8b-instant** ospitato sull'infrastruttura di [GroqCloud](https://console.groq.com/), un'architettura hardware che garantisce un'inferenza ad alta velocità e che offre l'utilizzo perfetto per un progetto accademico come questo.
Le API di Groq sono progettate per essere compatibili al 100% con lo standard di mercato.

L'output finale è un **Ethical Audit Report** formattato in Markdown, contenente i log degli errori classificati per priorità (ERROR, WARNING, INFO, SUGGESTION) e il feedback dell'Intelligenza Artificiale.

---

## Guida all'Installazione

Per eseguire questo progetto, è necessario utilizzare un **Ambiente Virtuale Python** per mantenere le librerie isolate, di seguito i passaggi:

### 1. Creare l'ambiente virtuale
Nella cartella del progetto lanciare il comando (valido su Windows, Mac o Linux): python -m venv venv

### 2. Attivare l'Ambiente Virtuale
- Su Windows: .\venv\Scripts\activate
- Su Mac/Linux: source venv/bin/activate

### 3. Installare le dipendenze
Per far funzionare sia il motore che la nuova interfaccia grafica, è necessario lanciare i seguenti comandi: 
## 3.1. Installare i requisiti base
pip install -r requirements.txt
## 3.2. Installare le librerie per la dashboard e i report
pip install streamlit fpdf2

### 4. Eseguire il software nell'ambiente virtuale
Si può scegliere tra due modalità di esecuzione
## 4.1. Via terminale (standard)
python main.py
## 4.2. Via dashboard (interativa)
streamlit run app.py