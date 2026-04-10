# EthicBPMN

## Descrizione del Progetto
**EthicBPMN** è un motore di validazione (Rule Engine) scritto in Python per l'analisi basata sui principi etici dei business process. 

Il software prende in input file di processo standard (`.bpmn` in formato XML), se non rispettano EthicBPMN grazie all'Intelligenza Artificiale vengono arricchiti compilando la **Matrice EthicBPMN**. Il sfotware analizza il processo applicando un'architettura di validazione a due livelli:

1. **Hard Compliance (Analisi Deterministica):** Un parser incrocia la topologia del diagramma (i costrutti BPMN) con i parametri etici della matrice EthicBPMN per rilevare violazioni strutturali delle 11 regole etiche.
2. **Soft Compliance (Analisi Semantica):** Un'integrazione con LLM (Intelligenza Artificiale) analizza il contesto semantico dei nodi per suggerire ulteriori ottimizzazioni.
Il progetto utilizza **Llama-3.1-8b-instant** ospitato sull'infrastruttura di [GroqCloud](https://console.groq.com/), un'architettura hardware che garantisce un'inferenza ad alta velocità e che offre l'utilizzo perfetto per un progetto accademico come questo.
Le API di Groq sono progettate per essere compatibili al 100% con lo standard di mercato.

Dopo l'analisi la dashboard mostrerà i punteggi relativi all'analisi etica del processo, una rappresentazione grafica del processo con indicazione degli elementi BPMN problematici e un resoconto dell'analisi LLM.
L'output finale è un **Ethical Audit Report** formattato in PDF e scaricabile direttamente dalla dashboard, contenente i log degli errori classificati e il feedback dell'Intelligenza Artificiale.
Dalla dashboard è possibile scaricare anche un ulteriore file in formato .bpmn che contiene le correzioni a tutti i problemi che riguardano i parametri della matrice etica.

NB: eventuali problemi etici che riguardano la struttura del processo non possono essere risolti dal software, ma devono essere risolti tramite reingegnerizzazione del processo, anche basata sui suggerimenti proposti dal software.

---

## Guida all'Installazione

Per eseguire questo progetto, è necessario utilizzare un **Ambiente Virtuale Python** per mantenere le librerie isolate, di seguito i passaggi:

### 1. Creare l'ambiente virtuale
Nella cartella del progetto lanciare il comando (valido su Windows, Mac o Linux): python -m venv venv

### 2. Attivare l'Ambiente Virtuale
- Su Windows: .\venv\Scripts\activate
- Su Mac/Linux: source venv/bin/activate

### 3. Installare le dipendenze
pip install -r requirements.txt

### 4. Eseguire il software
streamlit run app.py
